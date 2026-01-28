from database import engine, SessionLocal
from models import Base, Collection
from sqlalchemy import func

def create_tables():
    print("Creating tables in database...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")

        # Ensure 'Featured' collection exists
        with SessionLocal() as session:
            featured = session.query(Collection).filter(func.lower(Collection.title) == "featured").first()
            if not featured:
                print("Creating 'Featured' collection...")
                new_coll = Collection(title="Featured", channel_ids=[])
                session.add(new_coll)
                session.commit()
                print("'Featured' collection created!")
            else:
                print("'Featured' collection already exists.")
                
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
