
import asyncio
import sys
import os

# Add parent directory to path so we can import from backend root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from models import User
from database import engine
from utils.security import verify_password

async def check_users():
    print("Checking users in database...")
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("No users found in database!")
            return

        print(f"Found {len(users)} users:")
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Hashed Password: {user.hashed_password[:20]}...")
            
            # Test default passwords
            expected_pw = "admin123" if "admin" in user.email else "citizen123"
            try:
                is_valid = verify_password(expected_pw, user.hashed_password)
                print(f"Password '{expected_pw}' valid? {is_valid}")
            except Exception as e:
                print(f"Error verifying password: {e}")
            print("-" * 20)
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_users())
