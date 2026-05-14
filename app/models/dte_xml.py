from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DTEXmlType


class DTEXml(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dte_xml"
    __table_args__ = (
        Index("ix_dte_xml_dte_id", "dte_id"),
        Index("ix_dte_xml_xml_type", "xml_type"),
        Index("ix_dte_xml_created_at", "created_at"),
    )

    dte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dte.id", ondelete="CASCADE"),
        nullable=False,
    )
    xml_content: Mapped[str] = mapped_column(Text, nullable=False)
    xml_type: Mapped[DTEXmlType] = mapped_column(
        Enum(
            DTEXmlType,
            name="dte_xml_type",
            values_callable=lambda items: [item.value for item in items],
        ),
        default=DTEXmlType.UNSIGNED_DTE,
        nullable=False,
    )

    dte: Mapped["DTE"] = relationship(back_populates="xml_documents")
