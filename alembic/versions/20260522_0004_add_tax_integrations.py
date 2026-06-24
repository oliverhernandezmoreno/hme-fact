from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision = "20260522_0004"
down_revision = "20260514_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    for value in ("generated", "queued", "partially_accepted", "error"):
        op.execute(f"ALTER TYPE dte_status ADD VALUE IF NOT EXISTS '{value}'")

    for value in ("generated", "queued", "sii_status_checked", "sii_error"):
        op.execute(f"ALTER TYPE dte_event_type ADD VALUE IF NOT EXISTS '{value}'")

    if "dte_transmissions" not in inspector.get_table_names():
        op.create_table(
            "dte_transmissions",
            sa.Column("dte_id", sa.UUID(), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_track_id", sa.String(length=128), nullable=True),
            sa.Column("request_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("response_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_check_at", sa.DateTime(timezone=True), nullable=True),
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
                ["dte_id"],
                ["dte.id"],
                name="fk_dte_transmissions_dte_id_dte",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_dte_transmissions"),
        )
        op.create_index("ix_dte_transmissions_dte_id", "dte_transmissions", ["dte_id"])
        op.create_index("ix_dte_transmissions_provider", "dte_transmissions", ["provider"])
        op.create_index(
            "ix_dte_transmissions_external_track_id",
            "dte_transmissions",
            ["external_track_id"],
        )
        op.create_index("ix_dte_transmissions_status", "dte_transmissions", ["status"])
        op.create_index("ix_dte_transmissions_sent_at", "dte_transmissions", ["sent_at"])

    if "dte_status_history" not in inspector.get_table_names():
        op.create_table(
            "dte_status_history",
            sa.Column("dte_id", sa.UUID(), nullable=False),
            sa.Column("previous_status", sa.String(length=32), nullable=True),
            sa.Column("new_status", sa.String(length=32), nullable=False),
            sa.Column("provider_response", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
                ["dte_id"],
                ["dte.id"],
                name="fk_dte_status_history_dte_id_dte",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_dte_status_history"),
        )
        op.create_index("ix_dte_status_history_dte_id", "dte_status_history", ["dte_id"])
        op.create_index("ix_dte_status_history_new_status", "dte_status_history", ["new_status"])
        op.create_index("ix_dte_status_history_created_at", "dte_status_history", ["created_at"])


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    if "dte_status_history" in inspector.get_table_names():
        op.drop_index("ix_dte_status_history_created_at", table_name="dte_status_history")
        op.drop_index("ix_dte_status_history_new_status", table_name="dte_status_history")
        op.drop_index("ix_dte_status_history_dte_id", table_name="dte_status_history")
        op.drop_table("dte_status_history")
    if "dte_transmissions" in inspector.get_table_names():
        op.drop_index("ix_dte_transmissions_sent_at", table_name="dte_transmissions")
        op.drop_index("ix_dte_transmissions_status", table_name="dte_transmissions")
        op.drop_index("ix_dte_transmissions_external_track_id", table_name="dte_transmissions")
        op.drop_index("ix_dte_transmissions_provider", table_name="dte_transmissions")
        op.drop_index("ix_dte_transmissions_dte_id", table_name="dte_transmissions")
        op.drop_table("dte_transmissions")
