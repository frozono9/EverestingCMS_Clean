
import streamlit as st
import pandas as pd
from sqlalchemy import select, update, delete
from database import SessionLocal
from models import User, Activity, Challenge, Collection, UserChallenge
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
                # Try to get credentials from environment variables first (for local development with .env)
                # Then fall back to streamlit secrets (for cloud deployment)
                correct_username = os.getenv("ADMIN_USERNAME") or st.secrets.to_dict().get("ADMIN_USERNAME")
                correct_password = os.getenv("ADMIN_PASSWORD") or st.secrets.to_dict().get("ADMIN_PASSWORD")
                
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

def ensure_featured_collection():
    with SessionLocal() as session:
        from sqlalchemy import func
        featured = session.query(Collection).filter(func.lower(Collection.title) == "featured").first()
        if not featured:
            new_coll = Collection(title="Featured", channel_ids=[])
            session.add(new_coll)
            session.commit()

def main():
    if not check_password():
        st.stop()
    
    ensure_featured_collection()
        
    st.title("🏔️ Everesting Admin")
    st.divider()
    
    with st.sidebar:
        st.subheader("Navigation")
        choice = st.radio(
            "Manage Data",
            ["Challenges", "Collections", "Database"],
            index=0
        )
        st.divider()
        
        # Dashboard Stats
        with SessionLocal() as session:
            challenge_count = session.query(Challenge).count()
            collection_count = session.query(Collection).count()
            user_challenge_count = session.query(UserChallenge).count()
            activity_count = session.query(Activity).count()
            user_count = session.query(User).count()
            
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f"**Challenges**: {challenge_count}")
        st.markdown(f"**Collections**: {collection_count}")
        st.markdown(f"**User Enrollments**: {user_challenge_count}")
        st.markdown(f"**Activities**: {activity_count}")
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
        st.header("Collections Management")
        tab_view, tab_new, tab_modify = st.tabs(["📋 View Collections", "➕ Create Collection", "🔧 Modify Collection"])
        
        collections = get_all(Collection)
        challenges = get_all(Challenge)
        challenge_map = {c.title: str(c.id) for c in challenges}
        id_to_title = {str(c.id): c.title for c in challenges}

        with tab_view:
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
                        if c.title.lower() != "featured":
                            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_coll_{c.id}", help="Delete collection"):
                                delete_item(Collection, c.id)
                                st.toast(f"Collection '{c.title}' removed")
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.button("🔒", key=f"lock_coll_{c.id}", help="Featured collection cannot be deleted", disabled=True)
            else:
                st.info("No collections defined.")

        with tab_new:
            with st.form("new_coll_form_updated"):
                st.subheader("Create New Collection")
                new_title = st.text_input("Collection Name", placeholder="e.g. Summer Series")
                selected_challenges = st.multiselect(
                    "Select Challenges to Include",
                    options=list(challenge_map.keys())
                )
                if st.form_submit_button("Create Collection"):
                    if not new_title:
                        st.error("Name is required")
                    elif new_title.lower() == "featured":
                        st.error("The 'Featured' collection already exists and is managed automatically.")
                    else:
                        new_ids = [challenge_map[t] for t in selected_challenges]
                        create_item(Collection, {"title": new_title, "channel_ids": new_ids})
                        st.toast("Collection created with selected challenges!", icon="📁")
                        st.rerun()

        with tab_modify:
            if not collections:
                st.info("No collections to modify.")
            else:
                selected_coll_title = st.selectbox(
                    "Select Collection to Modify",
                    options=[c.title for c in collections]
                )
                
                selected_coll = next(c for c in collections if c.title == selected_coll_title)
                
                is_featured = selected_coll.title.lower() == "featured"
                
                with st.form(f"modify_coll_{selected_coll.id}"):
                    if is_featured:
                        st.info("This is the 'Featured' collection. You can only select one challenge.")
                        edit_title = st.text_input("Edit Name (Locked)", value=selected_coll.title, disabled=True)
                    else:
                        edit_title = st.text_input("Edit Name", value=selected_coll.title)
                        
                    current_ids = getattr(selected_coll, "channel_ids", []) or []
                    current_titles = [id_to_title.get(cid, cid) for cid in current_ids if cid in id_to_title]
                    
                    if is_featured:
                        selected_title = st.selectbox(
                            "Featured Challenge",
                            options=["None"] + list(challenge_map.keys()),
                            index=0 if not current_titles or current_titles[0] not in challenge_map 
                                  else list(challenge_map.keys()).index(current_titles[0]) + 1
                        )
                        new_ids = [challenge_map[selected_title]] if selected_title != "None" else []
                    else:
                        edit_challenges = st.multiselect(
                            "Modify Included Challenges",
                            options=list(challenge_map.keys()),
                            default=current_titles
                        )
                        new_ids = [challenge_map[t] for t in edit_challenges]
                    
                    if st.form_submit_button("Save Changes"):
                        with SessionLocal() as session:
                            db_coll = session.get(Collection, selected_coll.id)
                            if db_coll:
                                if not is_featured:
                                    db_coll.title = edit_title
                                db_coll.channel_ids = new_ids
                                session.commit()
                                st.toast(f"Updated {selected_coll.title}", icon="💾")
                                st.rerun()
                    
    elif choice == "Database":
        st.header("Database Explorer")
        
        tab_users, tab_activities, tab_collections, tab_challenges, tab_enrollments = st.tabs([
            "👥 Users", "🚴 Activities", "📁 Collections", "🏔️ Challenges", "🏆 Enrollments"
        ])
        
        with tab_users:
            users = get_all(User)
            if users:
                u_col1, u_col2, u_col3, u_col4 = st.columns([2, 3, 2, 2])
                u_col1.markdown("**Full Name**")
                u_col2.markdown("**Email**")
                u_col3.markdown("**Strava Link**")
                u_col4.markdown("**Date Joined**")
                st.divider()
                for u in users:
                    r_u1, r_u2, r_u3, r_u4 = st.columns([2, 3, 2, 2])
                    r_u1.write(f"{u.name} {u.last_name}")
                    r_u2.write(u.email or "—")
                    r_u3.write(f"[Profile](https://strava.com/athletes/{u.strava_id})" if u.strava_id else "—")
                    r_u4.write(u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "—")
            else:
                st.info("No users found in database.")

        with tab_activities:
            activities = get_all(Activity)
            if activities:
                a_col1, a_col2, a_col3, a_col4 = st.columns([1, 2, 1, 2])
                a_col1.markdown("**User ID**")
                a_col2.markdown("**Climb**")
                a_col3.markdown("**Elevation**")
                a_col4.markdown("**Timestamp**")
                st.divider()
                for a in activities:
                    r_a1, r_a2, r_a3, r_a4 = st.columns([1, 2, 1, 2])
                    r_a1.code(str(a.user_id)[:8])
                    r_a2.write(a.climb_name or "—")
                    r_a3.write(f"{a.elevation:,.0f} m")
                    r_a4.write(a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else "—")
            else:
                st.info("No activities/challenges found.")

        with tab_collections:
            collections = get_all(Collection)
            challenges = get_all(Challenge)
            id_to_title = {str(c.id): c.title for c in challenges}
            
            if collections:
                c1, c2, c3 = st.columns([3, 6, 1])
                c1.markdown("**Collection Name**")
                c2.markdown("**Assigned Challenges**")
                c3.markdown("")
                st.divider()
                for c in collections:
                    r1, r2, r3 = st.columns([3, 6, 1])
                    r1.write(f"**{c.title}**")
                    channel_ids = getattr(c, "channel_ids", []) or []
                    titles = [id_to_title.get(cid, cid) for cid in channel_ids]
                    r2.write(", ".join(titles) if titles else "—")
                    with r3:
                        if c.title.lower() != "featured":
                            if st.button("🗑️", key=f"db_del_coll_{c.id}"):
                                delete_item(Collection, c.id)
                                st.toast(f"Collection deleted", icon="🗑️")
                                st.rerun()
                        else:
                            st.button("🔒", key=f"db_lock_coll_{c.id}", disabled=True)
            else:
                st.info("No collections found.")

        with tab_challenges:
            challenges = get_all(Challenge)
            if challenges:
                ch1, ch2, ch3, ch4 = st.columns([3, 2, 3, 2])
                ch1.markdown("**Title**")
                ch2.markdown("**Elevation**")
                ch3.markdown("**Modalities**")
                ch4.markdown("**Start/End**")
                st.divider()
                for c in challenges:
                    r1, r2, r3, r4 = st.columns([3, 2, 3, 2])
                    r1.write(c.title)
                    r2.write(f"{c.elevation:,.0f} m")
                    r3.write(", ".join(c.modalidad or []))
                    dates = f"{c.start_date.strftime('%Y-%m-%d')} / {c.end_date.strftime('%Y-%m-%d')}" if c.start_date and c.end_date else "—"
                    r4.write(dates)
            else:
                st.info("No challenges found.")

        with tab_enrollments:
            enrollments = get_all(UserChallenge)
            users = get_all(User)
            challenges = get_all(Challenge)
            
            user_map = {u.id: f"{u.name} {u.last_name}" for u in users}
            challenge_map = {c.id: c.title for c in challenges}
            
            if enrollments:
                e_col1, e_col2, e_col3, e_col4, e_col5 = st.columns([2, 2, 1.5, 1.5, 2])
                e_col1.markdown("**User**")
                e_col2.markdown("**Challenge**")
                e_col3.markdown("**Status**")
                e_col4.markdown("**Progress**")
                e_col5.markdown("**Joined Date**")
                st.divider()
                for e in enrollments:
                    r_e1, r_e2, r_e3, r_e4, r_e5 = st.columns([2, 2, 1.5, 1.5, 2])
                    r_e1.write(user_map.get(e.user_id, str(e.user_id)[:8]))
                    r_e2.write(challenge_map.get(e.challenge_id, str(e.challenge_id)[:8]))
                    r_e3.write(e.status)
                    r_e4.write(f"{e.progress:.1f}%")
                    r_e5.write(e.created_at.strftime("%Y-%m-%d %H:%M") if e.created_at else "—")
            else:
                st.info("No user enrollments found.")

if __name__ == "__main__":
    main()
