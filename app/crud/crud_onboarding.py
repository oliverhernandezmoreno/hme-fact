import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.onboarding import OnboardingSession, OnboardingWorkflow


class CRUDOnboarding:
    async def get_active_workflow(
        self, db: AsyncSession, country_code: str = "CL"
    ) -> OnboardingWorkflow | None:
        result = await db.execute(
            select(OnboardingWorkflow)
            .where(
                OnboardingWorkflow.country_code == country_code,
                OnboardingWorkflow.is_active,
            )
            .options(selectinload(OnboardingWorkflow.step_definitions))
        )
        return result.scalars().first()

    async def get_session_by_company(
        self, db: AsyncSession, company_id: uuid.UUID
    ) -> OnboardingSession | None:
        result = await db.execute(
            select(OnboardingSession)
            .where(OnboardingSession.company_id == company_id)
            .options(
                selectinload(OnboardingSession.workflow).selectinload(
                    OnboardingWorkflow.step_definitions
                ),
                selectinload(OnboardingSession.step_statuses),
            )
        )
        return result.scalars().first()


onboarding = CRUDOnboarding()
