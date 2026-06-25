from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# Onboarding steps:
# 1 = Company data
# 2 = Tax configuration (SII resolution)
# 3 = Digital certificate upload
# 4 = CAF upload
# 5 = Email configuration
# 6 = Corporate logo
# 7 = Admin user setup
# 8 = Final validation

ONBOARDING_STEPS = 8


class OnboardingWizard(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "onboarding_wizards"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    current_step: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=ONBOARDING_STEPS, nullable=False)
    completed_steps: Mapped[list[int]] = mapped_column(JSONB, default=list, nullable=False)
    step_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)  # Stores per-step validated data
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    skipped_steps: Mapped[list[int]] = mapped_column(JSONB, default=list, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)  # Internal notes for support

    company: Mapped["Company"] = relationship("Company", foreign_keys=[company_id])

    @property
    def progress_pct(self) -> int:
        if not self.completed_steps:
            return 0
        return int(len(self.completed_steps) / self.total_steps * 100)

    @property
    def next_step(self) -> int | None:
        if self.is_completed:
            return None
        for step in range(1, self.total_steps + 1):
            if step not in self.completed_steps and step not in self.skipped_steps:
                return step
        return None
