from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DTEStatusHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dte_status_history"
    __table_args__ = (
        Index("ix_dte_status_history_dte_id", "dte_id"),
        Index("ix_dte_status_history_new_status", "new_status"),
        Index("ix_dte_status_history_created_at", "created_at"),
    )

    dte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dte.id", ondelete="CASCADE"),
        nullable=False,
    )
    previous_status: Mapped[str | None] = mapped_column(String(32))
    new_status: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_response: Mapped[dict[str, object] | None] = mapped_column(JSONB)

    dte: Mapped["DTE"] = relationship(back_populates="status_history")
