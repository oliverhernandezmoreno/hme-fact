from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class StepDefinitionResponse(ORMModel):
    code: str
    title: str
    description: str | None = None
    component_type: str
    status: str
    required: bool
    skippable: bool
    can_access: bool
    can_complete: bool
    can_skip: bool
    blocking_reasons: list[str] = Field(default_factory=list)
    validation_schema: dict[str, Any] = Field(default_factory=dict)
    help_content: str | None = None


class OnboardingSessionResponse(ORMModel):
    session_id: uuid.UUID
    workflow_code: str
    status: str
    progress_percentage: int
    current_step_code: str | None = None
    next_recommended_step: str | None = None
    steps: list[StepDefinitionResponse] = Field(default_factory=list)


class OnboardingStartRequest(BaseModel):
    country_code: str = "CL"
    company_type: str | None = None


class StepSaveRequest(BaseModel):
    input_data: dict[str, Any]


class StepCompleteRequest(BaseModel):
    input_data: dict[str, Any]
