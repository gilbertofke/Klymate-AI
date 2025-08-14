"""Create carbon credits tables

Revision ID: 006_create_carbon_credits_tables
Revises: 005_create_badge_tables
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '006_create_carbon_credits_tables'
down_revision = '005_create_badge_tables'
branch_labels = None
depends_on = None


def upgrade():
    """Create carbon credits system tables"""
    
    # Create carbon_credit_rates table
    op.create_table(
        'carbon_credit_rates',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('rate_type', sa.Enum('co2_to_kc', 'kc_to_usd', name='ratetype'), nullable=False),
        sa.Column('rate_value', sa.DECIMAL(10, 6), nullable=False),
        sa.Column('effective_date', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('source', sa.String(255)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('created_by', sa.CHAR(36)),
        sa.Column('updated_by', sa.CHAR(36)),
    )
    
    # Create indexes for carbon_credit_rates
    op.create_index('idx_rate_date', 'carbon_credit_rates', ['rate_type', 'effective_date'])
    op.create_index('idx_rate_type', 'carbon_credit_rates', ['rate_type'])
    
    # Create user_carbon_credits table
    op.create_table(
        'user_carbon_credits',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('current_balance', sa.DECIMAL(12, 4), default=0, nullable=False),
        sa.Column('total_earned', sa.DECIMAL(12, 4), default=0, nullable=False),
        sa.Column('total_redeemed', sa.DECIMAL(12, 4), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('created_by', sa.CHAR(36)),
        sa.Column('updated_by', sa.CHAR(36)),
    )
    
    # Create carbon_credit_transactions table
    op.create_table(
        'carbon_credit_transactions',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('transaction_type', sa.Enum('earned', 'redeemed', 'transferred', 'expired', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.DECIMAL(12, 4), nullable=False),
        sa.Column('co2_saved', sa.DECIMAL(8, 4)),
        sa.Column('activity_reference', sa.CHAR(36)),
        sa.Column('verification_status', sa.Enum('pending', 'verified', 'rejected', name='verificationstatus'), default='pending'),
        sa.Column('verification_method', sa.Enum('automatic', 'ai_verified', 'manual_review', name='verificationmethod'), default='automatic'),
        sa.Column('verification_metadata', sa.JSON),
        sa.Column('transaction_hash', sa.String(64)),
        sa.Column('exchange_rate', sa.DECIMAL(10, 6)),
        sa.Column('usd_value', sa.DECIMAL(10, 2)),
        sa.Column('notes', sa.Text),
        sa.Column('verified_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('created_by', sa.CHAR(36)),
        sa.Column('updated_by', sa.CHAR(36)),
    )
    
    # Create indexes for carbon_credit_transactions
    op.create_index('idx_user_transactions', 'carbon_credit_transactions', ['user_id', 'created_at'])
    op.create_index('idx_verification_status', 'carbon_credit_transactions', ['verification_status'])
    op.create_index('idx_transaction_type', 'carbon_credit_transactions', ['transaction_type', 'created_at'])
    op.create_index('idx_activity_reference', 'carbon_credit_transactions', ['activity_reference'])
    
    # Create carbon_credit_redemptions table
    op.create_table(
        'carbon_credit_redemptions',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('transaction_id', sa.CHAR(36), sa.ForeignKey('carbon_credit_transactions.id'), nullable=False),
        sa.Column('redemption_type', sa.Enum('cash_out', 'carbon_offset', 'donation', 'marketplace', name='redemptiontype'), nullable=False),
        sa.Column('amount_kc', sa.DECIMAL(12, 4), nullable=False),
        sa.Column('amount_usd', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('recipient_info', sa.JSON),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='redemptionstatus'), default='pending'),
        sa.Column('external_reference', sa.String(255)),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('created_by', sa.CHAR(36)),
        sa.Column('updated_by', sa.CHAR(36)),
    )
    
    # Create indexes for carbon_credit_redemptions
    op.create_index('idx_user_redemptions', 'carbon_credit_redemptions', ['user_id', 'created_at'])
    op.create_index('idx_redemption_status', 'carbon_credit_redemptions', ['status'])
    op.create_index('idx_redemption_type', 'carbon_credit_redemptions', ['redemption_type'])
    
    # Create carbon_verification_rules table
    op.create_table(
        'carbon_verification_rules',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('activity_type', sa.String(100), nullable=False),
        sa.Column('min_amount', sa.DECIMAL(8, 4)),
        sa.Column('max_amount', sa.DECIMAL(8, 4)),
        sa.Column('verification_method', sa.Enum('automatic', 'ai_verified', 'manual_review', name='ruleverificationmethod'), nullable=False),
        sa.Column('credit_multiplier', sa.DECIMAL(4, 2), default=1.0),
        sa.Column('requires_evidence', sa.Boolean, default=False),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('created_by', sa.CHAR(36)),
        sa.Column('updated_by', sa.CHAR(36)),
    )
    
    # Create indexes for carbon_verification_rules
    op.create_index('idx_activity_type', 'carbon_verification_rules', ['activity_type'])
    op.create_index('idx_verification_method', 'carbon_verification_rules', ['verification_method'])
    op.create_index('idx_active_rules', 'carbon_verification_rules', ['active'])


def downgrade():
    """Drop carbon credits system tables"""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('carbon_verification_rules')
    op.drop_table('carbon_credit_redemptions')
    op.drop_table('carbon_credit_transactions')
    op.drop_table('user_carbon_credits')
    op.drop_table('carbon_credit_rates')
    
    # Drop custom enum types
    op.execute("DROP TYPE IF EXISTS ratetype")
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS verificationstatus")
    op.execute("DROP TYPE IF EXISTS verificationmethod")
    op.execute("DROP TYPE IF EXISTS redemptiontype")
    op.execute("DROP TYPE IF EXISTS redemptionstatus")
    op.execute("DROP TYPE IF EXISTS ruleverificationmethod")