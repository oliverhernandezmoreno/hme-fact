"""Phase 7 Integrations

Revision ID: 20260624_0007
Revises: 20260624_0006
Create Date: 2026-06-24 19:48:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260624_0007"
down_revision = "20260624_0006"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    # integration_connections
    if "integration_connections" not in tables:
        op.create_table(
            "integration_connections",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("provider", sa.String(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("credentials", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
            sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_integration_connections_company_id"), "integration_connections", ["company_id"], unique=False)
        op.create_index(op.f("ix_integration_connections_provider"), "integration_connections", ["provider"], unique=False)

    # integration_events
    if "integration_events" not in tables:
        op.create_table(
            "integration_events",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("connection_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("event_type", sa.String(), nullable=False),
            sa.Column("status", sa.String(), nullable=False),
            sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
            sa.Column("error_detail", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["connection_id"], ["integration_connections.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_integration_events_company_id"), "integration_events", ["company_id"], unique=False)
        op.create_index(op.f("ix_integration_events_connection_id"), "integration_events", ["connection_id"], unique=False)
        op.create_index(op.f("ix_integration_events_status"), "integration_events", ["status"], unique=False)

    # external_mappings
    if "external_mappings" not in tables:
        op.create_table(
            "external_mappings",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("connection_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("entity_type", sa.String(), nullable=False),
            sa.Column("internal_id", sa.String(), nullable=False),
            sa.Column("external_id", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["connection_id"], ["integration_connections.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_external_mappings_company_id"), "external_mappings", ["company_id"], unique=False)
        op.create_index(op.f("ix_external_mappings_internal_id"), "external_mappings", ["internal_id"], unique=False)
        op.create_index(op.f("ix_external_mappings_external_id"), "external_mappings", ["external_id"], unique=False)

    # webhook_subscriptions
    if "webhook_subscriptions" not in tables:
        op.create_table(
            "webhook_subscriptions",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("target_url", sa.String(), nullable=False),
            sa.Column("event_types", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
            sa.Column("secret", sa.String(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_webhook_subscriptions_company_id"), "webhook_subscriptions", ["company_id"], unique=False)

    # webhook_deliveries
    if "webhook_deliveries" not in tables:
        op.create_table(
            "webhook_deliveries",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("event_type", sa.String(), nullable=False),
            sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column("status", sa.String(), nullable=False),
            sa.Column("status_code", sa.Integer(), nullable=True),
            sa.Column("response_body", sa.Text(), nullable=True),
            sa.Column("attempt", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["subscription_id"], ["webhook_subscriptions.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_webhook_deliveries_subscription_id"), "webhook_deliveries", ["subscription_id"], unique=False)

    # idempotency_keys
    if "idempotency_keys" not in tables:
        op.create_table(
            "idempotency_keys",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("key", sa.String(), nullable=False),
            sa.Column("response_code", sa.Integer(), nullable=True),
            sa.Column("response_body", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("expires_at", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_idempotency_keys_key"), "idempotency_keys", ["key"], unique=True)


def downgrade():
    op.drop_table("idempotency_keys")
    op.drop_table("webhook_deliveries")
    op.drop_table("webhook_subscriptions")
    op.drop_table("external_mappings")
    op.drop_table("integration_events")
    op.drop_table("integration_connections")
