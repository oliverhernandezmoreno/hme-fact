from __future__ import annotations

import uuid
from datetime import UTC

from sqlalchemy import select

from app.models.onboarding import OnboardingWizard
from app.repositories.base import BaseRepository


class OnboardingRepository(BaseRepository[OnboardingWizard]):
    model = OnboardingWizard

    async def get_by_company(self, company_id: uuid.UUID) -> OnboardingWizard | None:
        result = await self.session.scalars(
            select(OnboardingWizard).where(OnboardingWizard.company_id == company_id)
        )
        return result.first()

    async def get_or_create(self, company_id: uuid.UUID) -> OnboardingWizard:
        wizard = await self.get_by_company(company_id)
        if wizard is None:
            wizard = await self.create({"company_id": company_id})
        return wizard

    async def advance_step(
        self, wizard: OnboardingWizard, step: int, step_data: dict
    ) -> OnboardingWizard:
        completed = list(wizard.completed_steps or [])
        if step not in completed:
            completed.append(step)

        merged_data = dict(wizard.step_data or {})
        merged_data[str(step)] = step_data

        next_step = step + 1 if step < wizard.total_steps else wizard.current_step

        return await self.update(
            wizard,
            {
                "completed_steps": completed,
                "step_data": merged_data,
                "current_step": next_step,
            },
        )

    async def mark_complete(self, wizard: OnboardingWizard) -> OnboardingWizard:
        from datetime import datetime

        return await self.update(
            wizard,
            {
                "is_completed": True,
                "completed_at": datetime.now(UTC),
            },
        )
