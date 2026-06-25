"""fase6_saas_platform

Revision ID: 20260624_0006
Revises: 20260620_0005_phase5_updates
Create Date: 2026-06-24

Fase 6 changes:
- subscription_plans: add description, trial_days, sort_order, is_public
- subscription_features: add api_rate_limit_per_min, support_level
- subscriptions: add trial_end, cancelled_at, upgraded_from_plan_id
- billing_events: add description, metadata (JSONB)
- api_keys: add created_by_user_id, last_used_at, is_active
- api_usage_logs: add user_agent
- roles: add scope column
- users: add mfa_enabled, mfa_secret, mfa_backup_codes
- NEW: onboarding_wizards
- NEW: saas_metrics_snapshots
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "20260624_0006"
down_revision = "20260620_0005_phase5_updates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── subscription_plans ────────────────────────────────────────────────
    op.add_column("subscription_plans", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("subscription_plans", sa.Column("trial_days", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("subscription_plans", sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("subscription_plans", sa.Column("is_public", sa.Boolean(), nullable=False, server_default="true"))

    # ── subscription_features ─────────────────────────────────────────────
    op.add_column("subscription_features", sa.Column("api_rate_limit_per_min", sa.Integer(), nullable=False, server_default="60"))
    op.add_column("subscription_features", sa.Column("support_level", sa.String(50), nullable=False, server_default="'community'"))

    # ── subscriptions ─────────────────────────────────────────────────────
    op.add_column("subscriptions", sa.Column("trial_end", sa.DateTime(timezone=True), nullable=True))
    op.add_column("subscriptions", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "subscriptions",
        sa.Column(
            "upgraded_from_plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subscription_plans.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    # Update status values
    op.execute("UPDATE subscriptions SET status = 'active' WHERE status NOT IN ('active', 'trial', 'suspended', 'cancelled', 'expired')")

    # ── billing_events ────────────────────────────────────────────────────
    op.add_column("billing_events", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("billing_events", sa.Column("metadata", postgresql.JSONB(), nullable=True))

    # ── api_keys ──────────────────────────────────────────────────────────
    op.add_column(
        "api_keys",
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column("api_keys", sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("api_keys", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"))

    # ── api_usage_logs ────────────────────────────────────────────────────
    op.add_column("api_usage_logs", sa.Column("user_agent", sa.String(512), nullable=True))

    # ── roles ─────────────────────────────────────────────────────────────
    op.add_column("roles", sa.Column("scope", sa.String(20), nullable=False, server_default="'company'"))

    # ── users ─────────────────────────────────────────────────────────────
    op.add_column("users", sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("mfa_secret", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("mfa_backup_codes", postgresql.JSONB(), nullable=True))

    # ── onboarding_wizards (NEW TABLE) ────────────────────────────────────
    op.create_table(
        "onboarding_wizards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("current_step", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("total_steps", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("completed_steps", postgresql.JSONB(), nullable=False, server_default="'[]'"),
        sa.Column("step_data", postgresql.JSONB(), nullable=False, server_default="'{}'"),
        sa.Column("skipped_steps", postgresql.JSONB(), nullable=False, server_default="'[]'"),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── saas_metrics_snapshots (NEW TABLE) ────────────────────────────────
    op.create_table(
        "saas_metrics_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("snapshot_date", sa.Date(), nullable=False, unique=True),
        sa.Column("period_label", sa.String(20), nullable=False),
        sa.Column("mrr", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("arr", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("active_companies", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trial_companies", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("suspended_companies", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("new_companies_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("churned_companies_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active_users_30d", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dtes_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("api_calls_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("churn_rate_pct", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("growth_rate_pct", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("plan_distribution", postgresql.JSONB(), nullable=False, server_default="'{}'"),
        sa.Column("extra", postgresql.JSONB(), nullable=False, server_default="'{}'"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("saas_metrics_snapshots")
    op.drop_table("onboarding_wizards")
    op.drop_column("users", "mfa_backup_codes")
    op.drop_column("users", "mfa_secret")
    op.drop_column("users", "mfa_enabled")
    op.drop_column("roles", "scope")
    op.drop_column("api_usage_logs", "user_agent")
    op.drop_column("api_keys", "is_active")
    op.drop_column("api_keys", "last_used_at")
    op.drop_column("api_keys", "created_by_user_id")
    op.drop_column("billing_events", "metadata")
    op.drop_column("billing_events", "description")
    op.drop_column("subscriptions", "upgraded_from_plan_id")
    op.drop_column("subscriptions", "cancelled_at")
    op.drop_column("subscriptions", "trial_end")
    op.drop_column("subscription_features", "support_level")
    op.drop_column("subscription_features", "api_rate_limit_per_min")
    op.drop_column("subscription_plans", "is_public")
    op.drop_column("subscription_plans", "sort_order")
    op.drop_column("subscription_plans", "trial_days")
    op.drop_column("subscription_plans", "description")
