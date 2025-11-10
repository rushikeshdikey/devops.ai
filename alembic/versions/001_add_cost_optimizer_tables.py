"""add cost optimizer tables

Revision ID: 001_cost_optimizer
Revises:
Create Date: 2025-11-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_cost_optimizer'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create subscriptions table
    op.create_table('subscriptions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
    sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
    sa.Column('plan', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
    sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
    sa.Column('cancel_at_period_end', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create cloud_accounts table
    op.create_table('cloud_accounts',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('credentials', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('region', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create cost_analyses table
    op.create_table('cost_analyses',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('cloud_account_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('total_monthly_cost', sa.Float(), nullable=False),
    sa.Column('potential_savings', sa.Float(), nullable=False),
    sa.Column('savings_percentage', sa.Float(), nullable=False),
    sa.Column('resource_count', sa.Integer(), nullable=False),
    sa.Column('cost_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['cloud_account_id'], ['cloud_accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create cost_recommendations table
    op.create_table('cost_recommendations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('cost_analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('resource_type', sa.String(length=100), nullable=False),
    sa.Column('resource_id', sa.String(length=255), nullable=False),
    sa.Column('recommendation_type', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('current_cost', sa.Float(), nullable=False),
    sa.Column('estimated_new_cost', sa.Float(), nullable=False),
    sa.Column('monthly_savings', sa.Float(), nullable=False),
    sa.Column('annual_savings', sa.Float(), nullable=False),
    sa.Column('priority', sa.String(length=20), nullable=False),
    sa.Column('implementation_effort', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('recommendation_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['cost_analysis_id'], ['cost_analyses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('cost_recommendations')
    op.drop_table('cost_analyses')
    op.drop_table('cloud_accounts')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
