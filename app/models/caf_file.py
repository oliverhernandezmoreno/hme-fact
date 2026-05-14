from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CAFFile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "caf_files"
    __table_args__ = (
        CheckConstraint("dte_type IN (33, 34, 39, 41, 56, 61)", name="caf_dte_type_valid"),
        UniqueConstraint(
            "company_id",
            "dte_type",
            "folio_from",
            "folio_to",
            name="uq_caf_files_company_type_range",
        ),
        Index("ix_caf_files_company_id", "company_id"),
        Index("ix_caf_files_dte_type", "dte_type"),
        Index("ix_caf_files_folio_range", "folio_from", "folio_to"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    dte_type: Mapped[int] = mapped_column(Integer, nullable=False)
    folio_from: Mapped[int] = mapped_column(Integer, nullable=False)
    folio_to: Mapped[int] = mapped_column(Integer, nullable=False)
    authorization_date: Mapped[date] = mapped_column(Date, nullable=False)
    xml_content: Mapped[str] = mapped_column(Text, nullable=False)
    private_key: Mapped[str | None] = mapped_column(Text)
    current_folio: Mapped[int | None] = mapped_column(Integer)

    company: Mapped["Company"] = relationship(back_populates="caf_files")
    dtes: Mapped[list["DTE"]] = relationship(back_populates="caf_file")
