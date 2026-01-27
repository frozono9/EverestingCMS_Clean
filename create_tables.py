
import asyncio
from database import engine
from models import Base

async def create_tables():
    print("Creating tables in Supabase...")
    try:
        async with engine.begin() as conn:
            # This will create all tables that don't exist yet
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    asyncio.run(create_tables())
