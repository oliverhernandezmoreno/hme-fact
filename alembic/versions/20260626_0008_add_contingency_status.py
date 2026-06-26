"""Add contingency status

Revision ID: 20260626_0008
Revises: 20260624_0007
Create Date: 2026-06-26 18:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20260626_0008"
down_revision = "20260624_0007"
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL specific: ADD VALUE to custom Enum type
    # For PostgreSQL, we can use ALTER TYPE ADD VALUE IF NOT EXISTS.
    # Since sqlite/others don't support ALTER TYPE, we wrap it.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE dte_status ADD VALUE IF NOT EXISTS 'contingency'")
        op.execute("ALTER TYPE dte_event_type ADD VALUE IF NOT EXISTS 'sii_contingency'")


def downgrade():
    # Enums cannot be easily modified in downgrade for PostgreSQL, typically we leave them
    pass
