"""
Seed script to populate the database with demo data for Cloud Cost Optimizer.
"""
import asyncio
from apps.api.core.database import AsyncSessionLocal, engine, Base
from apps.api.core.security import get_password_hash
from apps.api.models.user import User
from apps.api.models.billing import Subscription


async def create_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        # Drop tables in correct order to handle dependencies
        from sqlalchemy import text
        tables = [
            "configs",
            "config_versions",
            "validation_runs",
            "policies",
            "audit_logs",
            "projects",
            "users"
        ]
        for table in tables:
            await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def seed_data():
    """Seed the database with demo data."""
    async with AsyncSessionLocal() as db:
        # Create users
        admin_user = User(
            email="admin@demo.io",
            name="Admin User",
            password_hash=get_password_hash("changeme"),
            role="ADMIN",
        )

        maintainer_user = User(
            email="maint@demo.io",
            name="Maintainer User",
            password_hash=get_password_hash("changeme"),
            role="MAINTAINER",
        )

        viewer_user = User(
            email="viewer@demo.io",
            name="Viewer User",
            password_hash=get_password_hash("changeme"),
            role="VIEWER",
        )

        db.add_all([admin_user, maintainer_user, viewer_user])
        await db.flush()

        print(f"✓ Created users:")
        print(f"  - admin@demo.io (ADMIN) - password: changeme")
        print(f"  - maint@demo.io (MAINTAINER) - password: changeme")
        print(f"  - viewer@demo.io (VIEWER) - password: changeme")

        # Create FREE subscriptions for all users
        admin_sub = Subscription(
            user_id=admin_user.id,
            plan="FREE",
            status="ACTIVE",
        )

        maintainer_sub = Subscription(
            user_id=maintainer_user.id,
            plan="FREE",
            status="ACTIVE",
        )

        viewer_sub = Subscription(
            user_id=viewer_user.id,
            plan="FREE",
            status="ACTIVE",
        )

        db.add_all([admin_sub, maintainer_sub, viewer_sub])
        await db.flush()

        print(f"✓ Created FREE subscriptions for all demo users")

        await db.commit()

        print("\n✅ Database seeded successfully!")
        print("\nDemo users created:")
        print("  - admin@demo.io / changeme (ADMIN role)")
        print("  - maint@demo.io / changeme (MAINTAINER role)")
        print("  - viewer@demo.io / changeme (VIEWER role)")
        print("\nAll users have FREE subscriptions. Connect cloud accounts to start analyzing costs!")


async def main():
    """Main entry point."""
    print("Creating tables...")
    await create_tables()
    print("✓ Tables created\n")

    print("Seeding data...")
    await seed_data()


if __name__ == "__main__":
    asyncio.run(main())
