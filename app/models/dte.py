from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DTEStatus


class DTE(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dte"
    __table_args__ = (
        CheckConstraint("dte_type IN (33, 34, 39, 41, 56, 61)", name="dte_type_valid"),
        UniqueConstraint("company_id", "dte_type", "folio", name="uq_dte_company_type_folio"),
        Index("ix_dte_company_id", "company_id"),
        Index("ix_dte_customer_id", "customer_id"),
        Index("ix_dte_certificate_id", "certificate_id"),
        Index("ix_dte_caf_file_id", "caf_file_id"),
        Index("ix_dte_status", "status"),
        Index("ix_dte_issue_date", "issue_date"),
        Index("ix_dte_sii_track_id", "sii_track_id"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    certificate_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("certificates.id", ondelete="SET NULL"),
    )
    caf_file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("caf_files.id", ondelete="SET NULL"),
    )
    dte_type: Mapped[int] = mapped_column(Integer, nullable=False)
    folio: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[DTEStatus] = mapped_column(
        Enum(
            DTEStatus,
            name="dte_status",
            values_callable=lambda items: [item.value for item in items],
        ),
        default=DTEStatus.DRAFT,
        nullable=False,
    )
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    exempt_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    sii_track_id: Mapped[str | None] = mapped_column(String(64))
    sii_xml: Mapped[str | None] = mapped_column(Text)
    sii_response: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reference_dte_type: Mapped[int | None] = mapped_column(Integer)
    reference_folio: Mapped[int | None] = mapped_column(BigInteger)
    reference_date: Mapped[date | None] = mapped_column(Date)
    reference_code: Mapped[int | None] = mapped_column(Integer)
    reference_reason: Mapped[str | None] = mapped_column(String(90))

    company: Mapped["Company"] = relationship(back_populates="dtes")
    customer: Mapped["Customer"] = relationship(back_populates="dtes")
    certificate: Mapped["Certificate | None"] = relationship(back_populates="dtes")
    caf_file: Mapped["CAFFile | None"] = relationship(back_populates="dtes")
    items: Mapped[list["DTEItem"]] = relationship(
        back_populates="dte",
        cascade="all, delete-orphan",
        order_by="DTEItem.line_number",
    )
    events: Mapped[list["DTEEvent"]] = relationship(
        back_populates="dte",
        cascade="all, delete-orphan",
        order_by="DTEEvent.created_at",
    )
    xml_documents: Mapped[list["DTEXml"]] = relationship(
        back_populates="dte",
        cascade="all, delete-orphan",
        order_by="DTEXml.created_at.desc()",
    )
