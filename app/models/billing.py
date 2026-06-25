from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SubscriptionPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subscription_plans"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="CLP", nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly", nullable=False)
    trial_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    features: Mapped["SubscriptionFeature"] = relationship("SubscriptionFeature", back_populates="plan", uselist=False)
    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="plan", foreign_keys="[Subscription.plan_id]")


class SubscriptionFeature(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subscription_features"

    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subscription_plans.id", ondelete="CASCADE"), unique=True)
    dte_limit: Mapped[int] = mapped_column(Integer, default=-1)  # -1 means unlimited
    users_limit: Mapped[int] = mapped_column(Integer, default=-1)
    branches_limit: Mapped[int] = mapped_column(Integer, default=-1)
    api_access: Mapped[bool] = mapped_column(Boolean, default=False)
    api_rate_limit_per_min: Mapped[int] = mapped_column(Integer, default=60)
    storage_limit_mb: Mapped[int] = mapped_column(Integer, default=1024)
    support_level: Mapped[str] = mapped_column(String(50), default="community", nullable=False)  # community, email, priority, dedicated

    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", back_populates="features")


class Subscription(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), unique=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"))
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # active, trial, suspended, cancelled, expired
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    upgraded_from_plan_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("subscription_plans.id", ondelete="SET NULL"))

    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", foreign_keys=[plan_id], back_populates="subscriptions")
    previous_plan: Mapped["SubscriptionPlan | None"] = relationship("SubscriptionPlan", foreign_keys=[upgraded_from_plan_id])


class UsageMetric(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "usage_metrics"
    __table_args__ = (
        UniqueConstraint("company_id", "period_month", "period_year", name="uix_usage_metrics_company_period"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    dtes_emitted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    api_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    storage_used_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class BillingEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "billing_events"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"))
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="CLP", nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # activation, renewal, upgrade, downgrade, cancellation, trial_start, trial_end
    description: Mapped[str | None] = mapped_column(Text)
    event_metadata: Mapped[dict | None] = mapped_column(JSONB, name="metadata")
