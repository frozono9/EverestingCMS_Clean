"""
Migration script to add strava_id column to activities table.
This fixes the "column activities.strava_id does not exist" error.

This script can be run standalone or imported and called from the main app.
"""
from sqlalchemy import text
import os
from dotenv import load_dotenv

def add_strava_id_column(engine=None):
    """Add strava_id column to activities table if it doesn't exist."""
    print("Checking for strava_id column in activities table...")
    
    # If no engine provided, create one
    if engine is None:
        from database import engine as db_engine
        engine = db_engine
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='activities' AND column_name='strava_id'
            """))
            
            if result.fetchone() is None:
                # Column doesn't exist, add it
                print("Adding strava_id column...")
                conn.execute(text("""
                    ALTER TABLE activities 
                    ADD COLUMN strava_id VARCHAR
                """))
                
                # Add unique constraint and index
                print("Creating index on strava_id...")
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_activities_strava_id 
                    ON activities(strava_id)
                """))
                
                conn.commit()
                print("✓ Successfully added strava_id column to activities table")
                return True
            else:
                print("✓ strava_id column already exists in activities table")
                return False
                
    except Exception as e:
        print(f"✗ Error checking/adding strava_id column: {e}")
        # Don't raise - allow app to continue even if migration fails
        return False

if __name__ == "__main__":
    load_dotenv()
    add_strava_id_column()

