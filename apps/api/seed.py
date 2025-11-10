"""
Seed script to populate the database with demo data.
"""
import asyncio
import uuid
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.core.database import AsyncSessionLocal, engine, Base
from apps.api.core.security import get_password_hash
from apps.api.models.user import User
from apps.api.models.project import Project
from apps.api.models.config import Config, ConfigVersion
from apps.api.models.policy import Policy
from apps.api.models.billing import Subscription


K8S_DEPLOYMENT_YAML = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/example/api:1.2.3
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
            requests:
              cpu: "250m"
              memory: "256Mi"
"""

TERRAFORM_CONFIG = """provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "logs" {
  bucket = "demo-logs"
  tags = {
    environment = "dev"
    owner       = "platform-team"
  }
}

variable "region" {
  default = "ap-south-1"
}
"""


async def create_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
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

        # Create project
        demo_project = Project(
            name="Demo Platform",
            description="Demo project for DevOps automation",
            created_by_id=admin_user.id,
        )

        db.add(demo_project)
        await db.flush()

        print(f"✓ Created project: {demo_project.name}")

        # Create K8s config
        k8s_config = Config(
            project_id=demo_project.id,
            title="API Server Deployment",
            type="K8S_YAML",
            tags=["kubernetes", "deployment", "api"],
        )

        db.add(k8s_config)
        await db.flush()

        # Create K8s version
        k8s_checksum = hashlib.sha256(K8S_DEPLOYMENT_YAML.encode()).hexdigest()
        k8s_version = ConfigVersion(
            config_id=k8s_config.id,
            version_number=1,
            content=K8S_DEPLOYMENT_YAML,
            checksum=k8s_checksum,
            created_by_id=admin_user.id,
        )

        db.add(k8s_version)
        await db.flush()

        k8s_config.latest_version_id = k8s_version.id

        print(f"✓ Created K8s config: {k8s_config.title}")

        # Create Terraform config
        tf_config = Config(
            project_id=demo_project.id,
            title="S3 Bucket Configuration",
            type="TERRAFORM",
            tags=["terraform", "aws", "s3"],
        )

        db.add(tf_config)
        await db.flush()

        # Create Terraform version
        tf_checksum = hashlib.sha256(TERRAFORM_CONFIG.encode()).hexdigest()
        tf_version = ConfigVersion(
            config_id=tf_config.id,
            version_number=1,
            content=TERRAFORM_CONFIG,
            checksum=tf_checksum,
            created_by_id=admin_user.id,
        )

        db.add(tf_version)
        await db.flush()

        tf_config.latest_version_id = tf_version.id

        print(f"✓ Created Terraform config: {tf_config.title}")

        # Create global policy
        policy = Policy(
            name="Require Owner Tag and No Latest Image",
            scope="GLOBAL",
            type="OPA_MOCK",
            rule="INCLUDES('owner') AND NOT MATCHES(':\\s*latest\\b')",
            project_id=None,
        )

        db.add(policy)

        print(f"✓ Created policy: {policy.name}")

        await db.commit()

        print("\n✅ Database seeded successfully!")
        print("\nYou can now log in with any of the demo users.")


async def main():
    """Main entry point."""
    print("Creating tables...")
    await create_tables()
    print("✓ Tables created\n")

    print("Seeding data...")
    await seed_data()


if __name__ == "__main__":
    asyncio.run(main())
