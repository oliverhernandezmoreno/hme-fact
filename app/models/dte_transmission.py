from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DTETransmission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dte_transmissions"
    __table_args__ = (
        Index("ix_dte_transmissions_dte_id", "dte_id"),
        Index("ix_dte_transmissions_provider", "provider"),
        Index("ix_dte_transmissions_external_track_id", "external_track_id"),
        Index("ix_dte_transmissions_status", "status"),
        Index("ix_dte_transmissions_sent_at", "sent_at"),
    )

    dte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dte.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    external_track_id: Mapped[str | None] = mapped_column(String(128))
    request_payload: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    response_payload: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_check_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    dte: Mapped["DTE"] = relationship(back_populates="transmissions")
