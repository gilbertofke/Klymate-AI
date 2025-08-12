"""Create AI conversations table

Revision ID: 004
Revises: 003
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '918731ccee61'  # Create habit tracking tables
branch_labels = None
depends_on = None


def upgrade():
    """Create AI conversations table with vector support."""
    
    # Create ai_conversations table
    op.create_table(
        'ai_conversations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('message_type', sa.Enum('user', 'assistant', 'system', name='message_type_enum'), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('context_metadata', sa.JSON(), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True, index=True),
        sa.Column('response_rating', sa.Integer(), nullable=True),
        sa.Column('response_feedback', sa.Text(), nullable=True),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp()),
        
        # Foreign key constraint
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        
        # Indexes for performance
        sa.Index('idx_ai_conversations_user_created', 'user_id', 'created_at'),
        sa.Index('idx_ai_conversations_session_created', 'session_id', 'created_at'),
        sa.Index('idx_ai_conversations_message_type_created', 'message_type', 'created_at'),
        
        # Composite indexes for common queries
        sa.Index('idx_ai_conversations_user_session', 'user_id', 'session_id'),
        sa.Index('idx_ai_conversations_user_type', 'user_id', 'message_type'),
    )
    
    # Add check constraint for response rating
    op.create_check_constraint(
        'ck_ai_conversations_rating_range',
        'ai_conversations',
        'response_rating IS NULL OR (response_rating >= 1 AND response_rating <= 5)'
    )
    
    # Note: In a production TiDB setup, you would also create a vector index:
    # This would be done with TiDB-specific SQL for vector indexing
    # For now, we'll use JSON storage which is compatible with the current setup


def downgrade():
    """Drop AI conversations table."""
    
    # Drop check constraint
    op.drop_constraint('ck_ai_conversations_rating_range', 'ai_conversations', type_='check')
    
    # Drop indexes (they will be dropped automatically with the table)
    
    # Drop table
    op.drop_table('ai_conversations')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS message_type_enum")