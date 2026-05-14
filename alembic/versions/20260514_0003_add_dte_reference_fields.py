from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260514_0003"
down_revision = "20260514_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    existing_columns = {column["name"] for column in inspect(op.get_bind()).get_columns("dte")}
    if "reference_dte_type" not in existing_columns:
        op.add_column("dte", sa.Column("reference_dte_type", sa.Integer(), nullable=True))
    if "reference_folio" not in existing_columns:
        op.add_column("dte", sa.Column("reference_folio", sa.BigInteger(), nullable=True))
    if "reference_date" not in existing_columns:
        op.add_column("dte", sa.Column("reference_date", sa.Date(), nullable=True))
    if "reference_code" not in existing_columns:
        op.add_column("dte", sa.Column("reference_code", sa.Integer(), nullable=True))
    if "reference_reason" not in existing_columns:
        op.add_column("dte", sa.Column("reference_reason", sa.String(length=90), nullable=True))


def downgrade() -> None:
    existing_columns = {column["name"] for column in inspect(op.get_bind()).get_columns("dte")}
    if "reference_reason" in existing_columns:
        op.drop_column("dte", "reference_reason")
    if "reference_code" in existing_columns:
        op.drop_column("dte", "reference_code")
    if "reference_date" in existing_columns:
        op.drop_column("dte", "reference_date")
    if "reference_folio" in existing_columns:
        op.drop_column("dte", "reference_folio")
    if "reference_dte_type" in existing_columns:
        op.drop_column("dte", "reference_dte_type")
