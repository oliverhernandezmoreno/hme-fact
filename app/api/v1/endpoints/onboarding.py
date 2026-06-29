from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.crud.crud_onboarding import onboarding as crud_onboarding
from app.models.user import User
from app.schemas.onboarding import (
    OnboardingSessionResponse,
    OnboardingStartRequest,
)

router = APIRouter()


@router.post("/start", response_model=OnboardingSessionResponse)
async def start_onboarding(
    *,
    db: AsyncSession = Depends(get_db_session),
    obj_in: OnboardingStartRequest,
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """Initialize a new onboarding session based on backend workflow definition."""
    workflow = await crud_onboarding.get_active_workflow(db, obj_in.country_code)
    if not workflow:
        raise HTTPException(status_code=404, detail="No active workflow found for this country")
    # For now, return a 501 until full engine is connected. The DB entities are ready.
    raise HTTPException(status_code=501, detail="Workflow Initialization Logic Pending (Sprint 2)")


@router.get("/session", response_model=OnboardingSessionResponse)
async def get_session(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    company_id: UUID = Header(alias="X-Company-ID"),
) -> Any:
    """Gets the current session with dynamic progress and steps state."""
    session = await crud_onboarding.get_session_by_company(db, company_id)
    if not session:
        raise HTTPException(status_code=404, detail="No onboarding session found")
    raise HTTPException(status_code=501, detail="Rule Engine Builder Pending (Sprint 2)")
