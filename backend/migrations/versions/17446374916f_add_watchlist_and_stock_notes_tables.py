"""Add watchlist and stock_notes tables

Revision ID: 17446374916f
Revises: b7c4f9e2a318
Create Date: 2026-05-19 13:32:39.562350

Adds two per-user feature tables (watchlist, stock_notes). Auto-generated
detected unrelated drift on the users.email index — that drift was
stripped out so this migration only touches the two new tables.
"""
from alembic import op
import sqlalchemy as sa


revision = '17446374916f'
down_revision = 'b7c4f9e2a318'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'stock_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'stock_id', name='uq_stock_notes_user_stock'),
    )
    op.create_index('ix_stock_notes_stock_id', 'stock_notes', ['stock_id'], unique=False)
    op.create_index('ix_stock_notes_user_id',  'stock_notes', ['user_id'],  unique=False)

    op.create_table(
        'watchlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'stock_id', name='uq_watchlist_user_stock'),
    )
    op.create_index('ix_watchlist_stock_id', 'watchlist', ['stock_id'], unique=False)
    op.create_index('ix_watchlist_user_id',  'watchlist', ['user_id'],  unique=False)


def downgrade():
    op.drop_index('ix_watchlist_user_id',  table_name='watchlist')
    op.drop_index('ix_watchlist_stock_id', table_name='watchlist')
    op.drop_table('watchlist')

    op.drop_index('ix_stock_notes_user_id',  table_name='stock_notes')
    op.drop_index('ix_stock_notes_stock_id', table_name='stock_notes')
    op.drop_table('stock_notes')
