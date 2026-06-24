from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision = "20260620_0005"
down_revision = "20260522_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    for value in ("pdf_generated", "emailed"):
        op.execute(f"ALTER TYPE dte_status ADD VALUE IF NOT EXISTS '{value}'")
        op.execute(f"ALTER TYPE dte_event_type ADD VALUE IF NOT EXISTS '{value}'")

    if "audit_logs" not in inspector.get_table_names():
        op.create_table(
            "audit_logs",
            sa.Column("company_id", sa.UUID(), nullable=True),
            sa.Column("user_id", sa.UUID(), nullable=True),
            sa.Column("entity_type", sa.String(length=100), nullable=False),
            sa.Column("entity_id", sa.UUID(), nullable=True),
            sa.Column("action", sa.String(length=100), nullable=False),
            sa.Column("previous_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("new_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("ip_address", sa.String(length=45), nullable=True),
            sa.Column("user_agent", sa.String(length=512), nullable=True),
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["company_id"],
                ["companies.id"],
                name="fk_audit_logs_company_id_companies",
                ondelete="SET NULL",
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name="fk_audit_logs_user_id_users",
                ondelete="SET NULL",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
        )
        op.create_index("ix_audit_logs_company_id", "audit_logs", ["company_id"])
        op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
        op.create_index("ix_audit_logs_entity_type_id", "audit_logs", ["entity_type", "entity_id"])
        op.create_index("ix_audit_logs_action", "audit_logs", ["action"])

    columns = [c["name"] for c in inspector.get_columns("certificates")]
    if "encrypted_password" not in columns:
        op.add_column("certificates", sa.Column("encrypted_password", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    columns = [c["name"] for c in inspector.get_columns("certificates")]
    if "encrypted_password" in columns:
        op.drop_column("certificates", "encrypted_password")

    if "audit_logs" in inspector.get_table_names():
        op.drop_index("ix_audit_logs_action", table_name="audit_logs")
        op.drop_index("ix_audit_logs_entity_type_id", table_name="audit_logs")
        op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
        op.drop_index("ix_audit_logs_company_id", table_name="audit_logs")
        op.drop_table("audit_logs")
