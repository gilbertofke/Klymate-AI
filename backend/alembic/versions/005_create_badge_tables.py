"""Create badge and gamification tables

Revision ID: 005
Revises: 004
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'  # AI conversations table
branch_labels = None
depends_on = None


def upgrade():
    """Create badge and gamification tables."""
    
    # Create badges table
    op.create_table(
        'badges',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.Enum('milestone', 'achievement', 'streak', 'social', 'special', name='badgecategory'), nullable=False, index=True),
        sa.Column('points_value', sa.Integer(), nullable=False, default=0),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('criteria', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, default=0),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        
        # Indexes for performance
        sa.Index('idx_badges_category_active', 'category', 'is_active'),
        sa.Index('idx_badges_active_sort', 'is_active', 'sort_order'),
        sa.Index('idx_badges_name_active', 'name', 'is_active'),
    )
    
    # Create user_badges table
    op.create_table(
        'user_badges',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('badge_id', sa.Integer(), nullable=False, index=True),
        sa.Column('earned_at', sa.DateTime(), nullable=True),
        sa.Column('progress_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['badge_id'], ['badges.id'], ondelete='CASCADE'),
        
        # Unique constraint to prevent duplicate badge awards
        sa.UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),
        
        # Indexes for performance
        sa.Index('idx_user_badges_user_earned', 'user_id', 'earned_at'),
        sa.Index('idx_user_badges_badge_earned', 'badge_id', 'earned_at'),
        sa.Index('idx_user_badges_user_created', 'user_id', 'created_at'),
    )


def downgrade():
    """Drop badge and gamification tables."""
    
    # Drop tables in reverse order
    op.drop_table('user_badges')
    op.drop_table('badges')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS badgecategory")