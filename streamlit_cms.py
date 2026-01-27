
import streamlit as st
import pandas as pd
from sqlalchemy import select, update, delete
from database import SessionLocal
from models import User, Activity, Challenge, Collection
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Everesting CMS",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a more "serious" look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    /* Style for delete buttons */
    .del-btn>div>button {
        background-color: transparent !important;
        color: #ef4444 !important;
        border: 1px solid #fee2e2 !important;
        height: 2.5em !important;
        width: 2.5em !important;
        padding: 0 !important;
    }
    .del-btn>div>button:hover {
        background-color: #fee2e2 !important;
        border-color: #ef4444 !important;
    }
    /* Data card styling */
    .data-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Constants
MODALITY_OPTIONS = ["Bicycle", "Running", "Skiing", "Multisport", "Hiking", "Walking"]
LABEL_OPTIONS = ["Beginner", "Amateur", "Pro", "Legend", "Easy", "Difficult", "Expert", "Hardcore"]

def check_password():
    """Returns `True` if the user had the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    # Center the login form
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.write("")
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 3rem;">🏔️</h1>
                <h2>Everesting Admin Login</h2>
                <p style="color: #64748b;">Please enter your credentials to continue</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                # Try to get credentials from streamlit secrets first (for cloud deployment)
                # Then fall back to environment variables (for local development)
                correct_username = st.secrets.get("ADMIN_USERNAME") or os.getenv("ADMIN_USERNAME")
                correct_password = st.secrets.get("ADMIN_PASSWORD") or os.getenv("ADMIN_PASSWORD")
                
                if not correct_username or not correct_password:
                    st.error("Authentication configuration missing. Please check Secrets or .env file.")
                elif username == correct_username and password == correct_password:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    with col3:
        st.write("")
        
    return False

def get_all(model):
    with SessionLocal() as session:
        result = session.execute(select(model))
        return result.scalars().all()

def create_item(model, data):
    with SessionLocal() as session:
        new_item = model(**data)
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
        return new_item

def delete_item(model, item_id):
    with SessionLocal() as session:
        item = session.get(model, item_id)
        if item:
            session.delete(item)
            session.commit()

def main():
    if not check_password():
        st.stop()
        
    st.title("🏔️ Everesting Admin")
    st.divider()
    
    with st.sidebar:
        st.subheader("Navigation")
        choice = st.radio(
            "Manage Data",
            ["Challenges", "Collections", "Assign", "Users", "Activities"],
            index=0
        )
        st.divider()
        
        # Dashboard Stats
        with SessionLocal() as session:
            challenge_count = session.query(Challenge).count()
            collection_count = session.query(Collection).count()
            user_count = session.query(User).count()
            
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f"**Challenges**: {challenge_count}")
        st.markdown(f"**Collections**: {collection_count}")
        st.markdown(f"**Users**: {user_count}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state["authenticated"] = False
            st.rerun()
            
        st.divider()
        st.caption("🟢 Connected to Production DB")
        st.caption("v1.2.0-Alpha")

    if choice == "Challenges":
        st.header("Challenges")
        
        tab_list, tab_create = st.tabs(["📋 View All", "➕ Create New"])
        
        with tab_list:
            sc1, sc2 = st.columns([5, 1])
            with sc1:
                search_query = st.text_input("🔍 Search Challenges", placeholder="Filter by title or modality...")
            with sc2:
                st.write("##")
                if st.button("Reset"):
                    st.rerun()
                    
            challenges = get_all(Challenge)
            
            if challenges:
                filtered_challenges = [
                    c for c in challenges 
                    if not search_query or 
                    search_query.lower() in c.title.lower() or 
                    any(search_query.lower() in m.lower() for m in (getattr(c, "modalidad", []) or []))
                ]
                
                if filtered_challenges:
                    # Header Row
                    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([3, 1.5, 2, 2, 2, 0.5])
                    h_col1.markdown("**Title**")
                    h_col2.markdown("**Elevation**")
                    h_col3.markdown("**Modalities**")
                    h_col4.markdown("**Labels**")
                    h_col5.markdown("**Dates**")
                    h_col6.markdown("") # For trash icon
                    st.divider()

                    for c in filtered_challenges:
                        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6 = st.columns([3, 1.5, 2, 2, 2, 0.5])
                        r_col1.write(c.title)
                        r_col2.write(f"{c.elevation:,.0f} m")
                        r_col3.write(", ".join(getattr(c, "modalidad", []) or []))
                        r_col4.write(", ".join(getattr(c, "labels", []) or []))
                        
                        dates = f"{c.start_date.strftime('%b %d')} - {c.end_date.strftime('%b %d')}" if c.start_date and c.end_date else "N/A"
                        r_col5.write(dates)
                        
                        with r_col6:
                            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_ch_{c.id}", help="Delete this challenge"):
                                delete_item(Challenge, c.id)
                                st.toast(f"Deleted {c.title}")
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("No matches found for your search.")
            else:
                st.info("No challenges found yet.")

        with tab_create:
            with st.form("new_challenge_form", clear_on_submit=True):
                st.subheader("New Challenge Details")
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Title", placeholder="e.g. Winter Peak 2026")
                    foto = st.text_input("Header Image URL")
                    elevation = st.number_input("Target Elevation (m)", min_value=0.0, step=100.0)
                with col2:
                    start_date = st.date_input("Start Date")
                    end_date = st.date_input("End Date")
                    
                description = st.text_area("Description")
                rules = st.text_area("Rules & Regulations")
                
                col_m, col_l = st.columns(2)
                with col_m:
                    modalidad = st.multiselect("Allowed Modalities", options=MODALITY_OPTIONS)
                with col_l:
                    labels = st.multiselect("Complexity Labels", options=LABEL_OPTIONS)
                
                if st.form_submit_button("Save New Challenge"):
                    if not title:
                        st.error("Title is required")
                    else:
                        data = {
                            "title": title,
                            "foto": foto,
                            "description": description,
                            "rules": rules,
                            "elevation": elevation,
                            "start_date": pd.to_datetime(start_date).to_pydatetime(),
                            "end_date": pd.to_datetime(end_date).to_pydatetime(),
                            "modalidad": modalidad,
                            "labels": labels
                        }
                        create_item(Challenge, data)
                        st.toast("Challenge created successfully!", icon="✅")
                        st.rerun()

    elif choice == "Collections":
        st.header("Collections")
        tab_view, tab_new = st.tabs(["📁 Active Collections", "➕ New Collection"])
        
        with tab_view:
            collections = get_all(Collection)
            challenges = get_all(Challenge)
            id_to_title = {str(c.id): c.title for c in challenges}

            if collections:
                # Header Row
                col_c1, col_c2, col_c3 = st.columns([3, 6, 1])
                col_c1.markdown("**Collection Name**")
                col_c2.markdown("**Assigned Challenges**")
                col_c3.markdown("")
                st.divider()

                for c in collections:
                    r_c1, r_c2, r_c3 = st.columns([3, 6, 1])
                    r_c1.write(f"**{c.title}**")
                    
                    channel_ids = getattr(c, "channel_ids", []) or []
                    titles = [id_to_title.get(cid, cid) for cid in channel_ids]
                    r_c2.write(", ".join(titles) if titles else "—")
                    
                    with r_c3:
                        st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_coll_{c.id}", help="Delete collection"):
                            delete_item(Collection, c.id)
                            st.toast(f"Collection '{c.title}' removed")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No collections defined.")

        with tab_new:
            with st.form("new_coll_form"):
                st.subheader("Create Collection")
                new_title = st.text_input("Name", placeholder="e.g. Summer Series")
                if st.form_submit_button("Create Collection"):
                    if new_title:
                        create_item(Collection, {"title": new_title, "channel_ids": []})
                        st.toast("Collection created!", icon="📁")
                        st.rerun()
                    else:
                        st.error("Name is required")

    elif choice == "Assign":
        st.header("Manage Content Assignments")
        st.info("Assign challenges to collections. Changes are saved per collection.")
        
        collections = get_all(Collection)
        challenges = get_all(Challenge)
        
        if not collections or not challenges:
            st.warning("Please ensure both Collections and Challenges exist before assigning.")
        else:
            challenge_map = {c.title: str(c.id) for c in challenges}
            id_to_title = {str(c.id): c.title for c in challenges}
            
            # 2-column layout for assignment cards
            cols = st.columns(2)
            for i, coll in enumerate(collections):
                with cols[i % 2]:
                    st.markdown(f"""
                        <div class="data-card">
                            <h3 style="margin-top:0;">📁 {coll.title}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    with st.container():
                        current_ids = getattr(coll, "channel_ids", []) or []
                        current_titles = [id_to_title.get(cid, cid) for cid in current_ids]
                        
                        selected_titles = st.multiselect(
                            "Included Challenges",
                            options=list(challenge_map.keys()),
                            default=[t for t in current_titles if t in challenge_map],
                            key=f"assign_{coll.id}"
                        )
                        
                        btn_col1, btn_col2 = st.columns([2, 1])
                        if btn_col1.button("Save Changes", key=f"save_{coll.id}"):
                            new_ids = [challenge_map[t] for t in selected_titles]
                            with SessionLocal() as session:
                                db_coll = session.get(Collection, coll.id)
                                if db_coll:
                                    db_coll.channel_ids = new_ids
                                    session.commit()
                                    st.toast(f"Updated {coll.title}", icon="💾")
                                    st.rerun()
                        st.divider()

    elif choice == "Users":
        st.header("User Registry")
        users = get_all(User)
        if users:
            # Table-like view with custom columns
            u_col1, u_col2, u_col3, u_col4 = st.columns([2, 3, 2, 2])
            u_col1.markdown("**Full Name**")
            u_col2.markdown("**Email**")
            u_col3.markdown("**Strava Link**")
            u_col4.markdown("**Date Joined**")
            st.divider()
            
            for u in users:
                r_u1, r_u2, r_u3, r_u4 = st.columns([2, 3, 2, 2])
                r_u1.write(f"{u.first_name} {u.last_name}")
                r_u2.write(u.email or "—")
                r_u3.write(f"[Profile](https://strava.com/athletes/{u.strava_id})" if u.strava_id else "—")
                r_u4.write(u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "—")
        else:
            st.info("No users found.")

    elif choice == "Activities":
        st.header("Activity Log")
        activities = get_all(Activity)
        if activities:
            a_col1, a_col2, a_col3, a_col4 = st.columns([1, 2, 1, 2])
            a_col1.markdown("**User ID**")
            a_col2.markdown("**Challenge**")
            a_col3.markdown("**Metric**")
            a_col4.markdown("**Timestamp**")
            st.divider()
            
            for a in activities:
                r_a1, r_a2, r_a3, r_a4 = st.columns([1, 2, 1, 2])
                r_a1.code(str(a.user_id)[:8])
                r_a2.write(str(a.challenge_id)[:8])
                r_a3.write(f"{a.current_elevation} m")
                r_a4.write(a.timestamp.strftime("%Y-%m-%d %H:%M") if a.timestamp else "—")
        else:
            st.info("No recent activities.")

if __name__ == "__main__":
    main()
