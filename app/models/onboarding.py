from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class OnboardingWorkflow(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "onboarding_workflows"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    country_code: Mapped[str] = mapped_column(String(2), default="CL", nullable=False)
    company_type: Mapped[str | None] = mapped_column(String(50))
    plan_code: Mapped[str | None] = mapped_column(String(50))
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_: Mapped[dict] = mapped_column(JSONB, name="metadata", default=dict, nullable=False)

    step_definitions: Mapped[list["OnboardingStepDefinition"]] = relationship(
        "OnboardingStepDefinition",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="OnboardingStepDefinition.order_index"
    )


class OnboardingStepDefinition(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "onboarding_step_definitions"
    __table_args__ = (
        UniqueConstraint("workflow_id", "code", name="uq_step_def_workflow_code"),
    )

    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_workflows.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    help_content: Mapped[str | None] = mapped_column(Text)
    component_type: Mapped[str] = mapped_column(String(100), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    skippable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    validation_schema: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    depends_on: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    completion_rules: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    actions: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    metadata_: Mapped[dict] = mapped_column(JSONB, name="metadata", default=dict, nullable=False)

    workflow: Mapped["OnboardingWorkflow"] = relationship("OnboardingWorkflow", back_populates="step_definitions")


class OnboardingSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "onboarding_sessions"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), unique=True)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_workflows.id"))
    current_step_code: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="not_started", nullable=False) # not_started, in_progress, blocked, completed, abandoned, skipped
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict] = mapped_column(JSONB, name="metadata", default=dict, nullable=False)

    company: Mapped["Company"] = relationship("Company")
    workflow: Mapped["OnboardingWorkflow"] = relationship("OnboardingWorkflow")
    step_statuses: Mapped[list["OnboardingStepStatus"]] = relationship(
        "OnboardingStepStatus",
        back_populates="session",
        cascade="all, delete-orphan"
    )


class OnboardingStepStatus(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "onboarding_step_status"
    __table_args__ = (
        UniqueConstraint("session_id", "step_definition_id", name="uq_onboarding_session_stepdef"),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id", ondelete="CASCADE"))
    step_definition_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_step_definitions.id"))
    step_code: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False) # pending, available, in_progress, completed, skipped, blocked, failed
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    skipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    blocked_reason: Mapped[str | None] = mapped_column(Text)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    input_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    output_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    validation_errors: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    session: Mapped["OnboardingSession"] = relationship("OnboardingSession", back_populates="step_statuses")
    step_definition: Mapped["OnboardingStepDefinition"] = relationship("OnboardingStepDefinition")


class OnboardingEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "onboarding_events"

    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id", ondelete="CASCADE"))
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    step_code: Mapped[str | None] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(50))
    user_agent: Mapped[str | None] = mapped_column(Text)

    session: Mapped["OnboardingSession"] = relationship("OnboardingSession")
