
import asyncio
from database import engine, Base
import models
from sqlalchemy import text

async def reset():
    print("Resetting database (Safe Cascade Mode)...")
    print(f"Registered models: {Base.metadata.tables.keys()}")
    
    async with engine.begin() as conn:
        tables = ["votes", "reports", "users", "field_teams", "departments"]
        for table in tables:
            print(f"Dropping {table}...")
            await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database reset complete.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset())
