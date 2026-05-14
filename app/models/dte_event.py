from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DTEEventType


class DTEEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dte_events"
    __table_args__ = (
        Index("ix_dte_events_dte_id", "dte_id"),
        Index("ix_dte_events_event_type", "event_type"),
    )

    dte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dte.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[DTEEventType] = mapped_column(
        Enum(
            DTEEventType,
            name="dte_event_type",
            values_callable=lambda items: [item.value for item in items],
        ),
        nullable=False,
    )
    message: Mapped[str | None] = mapped_column(Text)
    actor: Mapped[str | None] = mapped_column(String(255))
    payload: Mapped[dict[str, object] | None] = mapped_column(JSONB)

    dte: Mapped["DTE"] = relationship(back_populates="events")
