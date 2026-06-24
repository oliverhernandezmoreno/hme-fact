from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "companies"
    __table_args__ = (
        UniqueConstraint("rut", name="uq_companies_rut"),
        Index("ix_companies_legal_name", "legal_name"),
        Index("ix_companies_is_active", "is_active"),
    )

    rut: Mapped[str] = mapped_column(String(12), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    fantasy_name: Mapped[str | None] = mapped_column(String(255))
    giro: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(255))
    comuna: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    sii_resolution_number: Mapped[int | None] = mapped_column(Integer)
    sii_resolution_date: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    onboarding_step: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ip_allowlist: Mapped[list[str] | None] = mapped_column(String) # Will be mapped as JSON or String list in DB

    users: Mapped[list["CompanyUser"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    customers: Mapped[list["Customer"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    products: Mapped[list["Product"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    certificates: Mapped[list["Certificate"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    caf_files: Mapped[list["CAFFile"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    dtes: Mapped[list["DTE"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
