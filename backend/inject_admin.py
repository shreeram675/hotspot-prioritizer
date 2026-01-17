import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from database import DATABASE_URL
from models import User, UserRole
from utils.security import get_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

async def inject():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        email = "superadmin@example.com"
        password = "admin123"
        print(f"DEBUG: Original password: '{password}'")
        print(f"Injecting user: {email}")
        
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if user:
            print(f"User {email} already exists, updating password...")
            user.hashed_password = get_password_hash(password)
            user.role = UserRole.admin
        else:
            print(f"Creating new superadmin: {email}")
            hashed_pw = get_password_hash(password)
            print(f"DEBUG: Generated hash for password '{password}': {hashed_pw}")
            print(f"DEBUG: Hash length: {len(hashed_pw)}, Type: {type(hashed_pw)}")
            new_user = User(
                email=email,
                name="Super Admin",
                hashed_password=hashed_pw,
                role=UserRole.admin
            )
            session.add(new_user)
        
        await session.commit()
        print("Injection complete!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(inject())
