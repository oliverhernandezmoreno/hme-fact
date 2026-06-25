from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SaasMetricsSnapshot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Daily snapshot of platform-wide SaaS KPIs.
    Created by Celery beat task at 02:00 UTC daily.
    """

    __tablename__ = "saas_metrics_snapshots"

    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    period_label: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. "2025-06"

    # Revenue
    mrr: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)  # Monthly Recurring Revenue (CLP)
    arr: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)  # Annual Recurring Revenue (CLP)

    # Companies
    active_companies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trial_companies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    suspended_companies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_companies_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    churned_companies_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Users
    total_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_users_30d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Usage
    dtes_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    api_calls_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Computed KPIs
    churn_rate_pct: Mapped[float] = mapped_column(Numeric(6, 4), default=0.0, nullable=False)
    growth_rate_pct: Mapped[float] = mapped_column(Numeric(6, 4), default=0.0, nullable=False)

    # Plan breakdown (e.g. {"starter": 10, "pyme": 25, "business": 5})
    plan_distribution: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Extra breakdown data
    extra: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
