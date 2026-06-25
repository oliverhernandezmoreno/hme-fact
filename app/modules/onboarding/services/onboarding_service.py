from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.onboarding import OnboardingWizard, ONBOARDING_STEPS
from app.repositories.onboarding import OnboardingRepository


STEP_LABELS = {
    1: "Datos de empresa",
    2: "Configuración tributaria",
    3: "Certificado digital",
    4: "Carga de CAF",
    5: "Configuración de correo",
    6: "Logo corporativo",
    7: "Usuario administrador",
    8: "Validación final",
}


@dataclass
class OnboardingProgress:
    company_id: uuid.UUID
    current_step: int
    total_steps: int
    completed_steps: list[int]
    skipped_steps: list[int]
    progress_pct: int
    is_completed: bool
    next_step: int | None
    next_step_label: str | None
    step_labels: dict[int, str]


class OnboardingService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = OnboardingRepository(session)

    async def get_or_create(self, company_id: uuid.UUID) -> OnboardingWizard:
        return await self._repo.get_or_create(company_id)

    async def get_progress(self, company_id: uuid.UUID) -> OnboardingProgress:
        wizard = await self._repo.get_or_create(company_id)
        next_step = wizard.next_step
        return OnboardingProgress(
            company_id=company_id,
            current_step=wizard.current_step,
            total_steps=wizard.total_steps,
            completed_steps=list(wizard.completed_steps or []),
            skipped_steps=list(wizard.skipped_steps or []),
            progress_pct=wizard.progress_pct,
            is_completed=wizard.is_completed,
            next_step=next_step,
            next_step_label=STEP_LABELS.get(next_step) if next_step else None,
            step_labels=STEP_LABELS,
        )

    async def advance_step(
        self,
        company_id: uuid.UUID,
        step: int,
        step_data: dict,
    ) -> OnboardingWizard:
        if step < 1 or step > ONBOARDING_STEPS:
            raise ValueError(f"Step must be between 1 and {ONBOARDING_STEPS}")
        wizard = await self._repo.get_or_create(company_id)
        updated = await self._repo.advance_step(wizard, step, step_data)

        # Auto-complete if all steps done
        all_steps = set(range(1, ONBOARDING_STEPS + 1))
        done = set(updated.completed_steps or []) | set(updated.skipped_steps or [])
        if all_steps <= done and not updated.is_completed:
            updated = await self._repo.mark_complete(updated)

        return updated

    async def skip_step(self, company_id: uuid.UUID, step: int) -> OnboardingWizard:
        wizard = await self._repo.get_or_create(company_id)
        skipped = list(wizard.skipped_steps or [])
        if step not in skipped:
            skipped.append(step)
        return await self._repo.update(wizard, {"skipped_steps": skipped})

    async def complete(self, company_id: uuid.UUID) -> OnboardingWizard:
        wizard = await self._repo.get_or_create(company_id)
        if wizard.is_completed:
            return wizard
        return await self._repo.mark_complete(wizard)
