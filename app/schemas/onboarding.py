from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class StepDefinitionResponse(ORMModel):
    code: str
    title: str
    description: Optional[str] = None
    component_type: str
    status: str
    required: bool
    skippable: bool
    can_access: bool
    can_complete: bool
    can_skip: bool
    blocking_reasons: List[str] = Field(default_factory=list)
    validation_schema: Dict[str, Any] = Field(default_factory=dict)
    help_content: Optional[str] = None


class OnboardingSessionResponse(ORMModel):
    session_id: uuid.UUID
    workflow_code: str
    status: str
    progress_percentage: int
    current_step_code: Optional[str] = None
    next_recommended_step: Optional[str] = None
    steps: List[StepDefinitionResponse] = Field(default_factory=list)


class OnboardingStartRequest(BaseModel):
    country_code: str = "CL"
    company_type: Optional[str] = None


class StepSaveRequest(BaseModel):
    input_data: Dict[str, Any]


class StepCompleteRequest(BaseModel):
    input_data: Dict[str, Any]
