
import asyncio
import os
from sqlalchemy import select
from database import AsyncSessionLocal
from models import User, Activity

async def test_connection():
    print("Testing connection to Supabase...")
    try:
        async with AsyncSessionLocal() as session:
            # Query users
            print("\n--- Users ---")
            user_query = select(User).limit(5)
            result = await session.execute(user_query)
            users = result.scalars().all()
            if not users:
                print("No users found.")
            for user in users:
                print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")

            # Query activities
            print("\n--- Activities ---")
            activity_query = select(Activity).limit(5)
            result = await session.execute(activity_query)
            activities = result.scalars().all()
            if not activities:
                print("No activities found.")
            for activity in activities:
                print(f"ID: {activity.id}, Name: {activity.climb_name}, Elevation: {activity.elevation}")
                
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
