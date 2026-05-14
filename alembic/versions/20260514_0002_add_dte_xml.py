from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

revision = "20260514_0002"
down_revision = "20260514_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    if "dte_xml" in inspector.get_table_names():
        return

    dte_xml_type = postgresql.ENUM(
        "unsigned_dte",
        "signed_dte",
        "envelope",
        "sii_response",
        name="dte_xml_type",
        create_type=False,
    )
    dte_xml_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "dte_xml",
        sa.Column("dte_id", sa.UUID(), nullable=False),
        sa.Column("xml_content", sa.Text(), nullable=False),
        sa.Column("xml_type", dte_xml_type, nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["dte_id"], ["dte.id"], name="fk_dte_xml_dte_id_dte", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_dte_xml"),
    )
    op.create_index("ix_dte_xml_created_at", "dte_xml", ["created_at"])
    op.create_index("ix_dte_xml_dte_id", "dte_xml", ["dte_id"])
    op.create_index("ix_dte_xml_xml_type", "dte_xml", ["xml_type"])


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    if "dte_xml" not in inspector.get_table_names():
        return

    op.drop_index("ix_dte_xml_xml_type", table_name="dte_xml")
    op.drop_index("ix_dte_xml_dte_id", table_name="dte_xml")
    op.drop_index("ix_dte_xml_created_at", table_name="dte_xml")
    op.drop_table("dte_xml")
    postgresql.ENUM(name="dte_xml_type").drop(op.get_bind(), checkfirst=True)
