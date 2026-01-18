from database import engine
from sqlalchemy import text
import asyncio

async def add_columns():
    async with engine.begin() as conn:
        print("Checking if columns exist...")
        try:
            # Try adding location_meta
            try:
                await conn.execute(text("ALTER TABLE reports ADD COLUMN location_meta VARCHAR"))
                print("Added location_meta column")
            except Exception as e:
                print(f"location_meta might already exist or error: {e}")

            # Try adding sentiment_meta
            try:
                await conn.execute(text("ALTER TABLE reports ADD COLUMN sentiment_meta VARCHAR"))
                print("Added sentiment_meta column")
            except Exception as e:
                print(f"sentiment_meta might already exist or error: {e}")
                
        except Exception as e:
            print(f"General error: {e}")

if __name__ == "__main__":
    asyncio.run(add_columns())
