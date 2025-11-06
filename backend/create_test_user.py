#!/usr/bin/env python3
"""
Create a test user for development.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import AsyncSessionLocal, engine
from app.models.user import User


async def create_test_user():
    """Create a test user if it doesn't exist."""
    async with AsyncSessionLocal() as session:
        try:
            # Check if test user already exists
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✅ Test user already exists:")
                print(f"   Email: {existing_user.email}")
                print(f"   ID: {existing_user.id}")
                print(f"   Password: testpass123")
                return
            
            # Create test user
            test_user = User(
                email="test@example.com",
                hashed_password=get_password_hash("testpass123"),
                is_active=True,
                is_superuser=False,
            )
            
            session.add(test_user)
            await session.commit()
            
            # Refresh to get the ID
            await session.refresh(test_user)
            
            print("✅ Test user created successfully!")
            print(f"   Email: {test_user.email}")
            print(f"   Password: testpass123")
            print(f"   ID: {test_user.id}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating test user: {e}")
            raise


async def main():
    """Main function."""
    print("🔧 Creating test user...")
    print(f"   Database: {settings.database_url_str}")
    
    try:
        await create_test_user()
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

