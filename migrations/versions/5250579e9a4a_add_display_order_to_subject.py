"""Add display_order to Subject

Revision ID: 5250579e9a4a
Revises: 77710e6b93d6
Create Date: 2025-12-14 14:57:45.846124

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '5250579e9a4a'
down_revision = '77710e6b93d6'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    # Add display_order column if it doesn't exist (PostgreSQL production)
    # SQLite dev database may already have it from partial migration runs
    if not column_exists('subject', 'display_order'):
        op.add_column('subject', sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))
    
    # Update any NULL values (safety measure)
    op.execute("UPDATE subject SET display_order = 0 WHERE display_order IS NULL")


def downgrade():
    op.drop_column('subject', 'display_order')
