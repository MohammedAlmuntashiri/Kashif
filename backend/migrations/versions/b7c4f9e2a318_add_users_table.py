"""add users table

Revision ID: b7c4f9e2a318
Revises: 276248ecd392
Create Date: 2026-05-18 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7c4f9e2a318'
down_revision = '276248ecd392'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id',            sa.Integer(),      nullable=False),
        sa.Column('email',         sa.String(length=255), nullable=False),
        sa.Column('name',          sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at',    sa.DateTime(),     nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=False)


def downgrade():
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
