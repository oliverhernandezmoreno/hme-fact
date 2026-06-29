import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate


class CRUDCertificate:
    async def get(self, db: AsyncSession, id: uuid.UUID) -> Certificate | None:
        result = await db.execute(select(Certificate).where(Certificate.id == id))
        return result.scalars().first()

    async def get_by_company(self, db: AsyncSession, company_id: uuid.UUID) -> list[Certificate]:
        result = await db.execute(
            select(Certificate)
            .where(Certificate.company_id == company_id)
            .order_by(Certificate.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_for_company(
        self, db: AsyncSession, company_id: uuid.UUID
    ) -> Certificate | None:
        result = await db.execute(
            select(Certificate).where(
                Certificate.company_id == company_id, Certificate.is_active == True
            )
        )
        return result.scalars().first()

    async def create(
        self, db: AsyncSession, *, obj_in: CertificateCreate, company_id: uuid.UUID
    ) -> Certificate:
        # If there's an active one, deactivate it? Depends on business logic. Usually handled in the service/endpoint.
        db_obj = Certificate(company_id=company_id, **obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def deactivate_all_for_company(self, db: AsyncSession, company_id: uuid.UUID) -> None:
        active_certs = await self.get_by_company(db, company_id)
        for cert in active_certs:
            if cert.is_active:
                cert.is_active = False
                db.add(cert)
        await db.commit()


certificate = CRUDCertificate()
