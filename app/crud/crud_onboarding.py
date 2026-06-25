import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.onboarding import OnboardingSession, OnboardingWorkflow


class CRUDOnboarding:
    async def get_active_workflow(self, db: AsyncSession, country_code: str = "CL") -> Optional[OnboardingWorkflow]:
        result = await db.execute(
            select(OnboardingWorkflow)
            .where(
                OnboardingWorkflow.country_code == country_code,
                OnboardingWorkflow.is_active == True
            )
            .options(selectinload(OnboardingWorkflow.step_definitions))
        )
        return result.scalars().first()

    async def get_session_by_company(self, db: AsyncSession, company_id: uuid.UUID) -> Optional[OnboardingSession]:
        result = await db.execute(
            select(OnboardingSession)
            .where(OnboardingSession.company_id == company_id)
            .options(
                selectinload(OnboardingSession.workflow).selectinload(OnboardingWorkflow.step_definitions),
                selectinload(OnboardingSession.step_statuses)
            )
        )
        return result.scalars().first()

onboarding = CRUDOnboarding()
