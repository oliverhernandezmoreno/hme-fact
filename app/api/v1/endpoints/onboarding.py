from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import CurrentUserDep, SessionDep, TenantDep
from app.modules.onboarding.services.onboarding_service import OnboardingService

router = APIRouter()


class StepRequest(BaseModel):
    data: dict = {}


@router.get("", summary="Get onboarding progress for company")
async def get_onboarding(
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = OnboardingService(session)
    progress = await svc.get_progress(company_id)
    return {
        "company_id": str(progress.company_id),
        "current_step": progress.current_step,
        "total_steps": progress.total_steps,
        "completed_steps": progress.completed_steps,
        "skipped_steps": progress.skipped_steps,
        "progress_pct": progress.progress_pct,
        "is_completed": progress.is_completed,
        "next_step": progress.next_step,
        "next_step_label": progress.next_step_label,
        "step_labels": {str(k): v for k, v in progress.step_labels.items()},
    }


@router.post("/step/{step_number}", summary="Complete onboarding step N")
async def complete_step(
    step_number: int,
    body: StepRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = OnboardingService(session)
    try:
        wizard = await svc.advance_step(company_id, step_number, body.data)
        return {
            "step": step_number,
            "completed": True,
            "is_onboarding_completed": wizard.is_completed,
            "progress_pct": wizard.progress_pct,
            "completed_steps": wizard.completed_steps,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/step/{step_number}/skip", summary="Skip optional onboarding step")
async def skip_step(
    step_number: int,
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = OnboardingService(session)
    try:
        wizard = await svc.skip_step(company_id, step_number)
        return {"step": step_number, "skipped": True, "skipped_steps": wizard.skipped_steps}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/complete", summary="Mark onboarding as completed")
async def complete_onboarding(
    session: SessionDep,
    current_user: CurrentUserDep,
    company_id: TenantDep,
):
    svc = OnboardingService(session)
    wizard = await svc.complete(company_id)
    return {"is_completed": wizard.is_completed, "completed_at": wizard.completed_at.isoformat() if wizard.completed_at else None}
