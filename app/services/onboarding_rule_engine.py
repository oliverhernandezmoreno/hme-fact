from typing import Any, Dict, List, Optional
from app.models.onboarding import OnboardingSession, OnboardingStepDefinition, OnboardingStepStatus
from app.schemas.onboarding import StepDefinitionResponse


class OnboardingRuleEngine:
    """
    Evaluates dynamic rules for onboarding steps based on the current session state.
    Calculates can_access, can_complete, can_skip, blocking_reasons and next_recommended_step.
    """
    
    @staticmethod
    def evaluate_step(
        step: OnboardingStepDefinition,
        session: OnboardingSession,
        all_statuses: List[OnboardingStepStatus]
    ) -> StepDefinitionResponse:
        
        status_obj = next((s for s in all_statuses if s.step_definition_id == step.id), None)
        current_status = status_obj.status if status_obj else "pending"
        
        blocking_reasons = []
        can_access = True
        
        # Check explicit dependencies
        for dep_code in step.depends_on:
            dep_status = next((s for s in all_statuses if s.step_code == dep_code), None)
            if not dep_status or dep_status.status not in ("completed", "skipped"):
                can_access = False
                blocking_reasons.append(f"Requires step '{dep_code}' to be completed.")
                
        # Check specific completion rules (e.g., must have an active certificate)
        # This will be expanded as we integrate the external SaaS services
        
        # Calculate can_complete based on schema validation
        can_complete = True if can_access else False
        
        return StepDefinitionResponse(
            code=step.code,
            title=step.title,
            description=step.description,
            component_type=step.component_type,
            status=current_status,
            required=step.required,
            skippable=step.skippable,
            can_access=can_access,
            can_complete=can_complete,
            can_skip=step.skippable and can_access,
            blocking_reasons=blocking_reasons,
            validation_schema=step.validation_schema,
            help_content=step.help_content,
        )

    @staticmethod
    def calculate_progress(session: OnboardingSession, all_steps: List[OnboardingStepDefinition], all_statuses: List[OnboardingStepStatus]) -> int:
        if not all_steps:
            return 0
            
        completed_or_skipped = sum(
            1 for s in all_statuses 
            if s.status in ("completed", "skipped") and s.step_definition_id in [step.id for step in all_steps]
        )
        return int((completed_or_skipped / len(all_steps)) * 100)

    @staticmethod
    def determine_next_step(
        all_steps: List[OnboardingStepDefinition], 
        evaluated_steps: List[StepDefinitionResponse]
    ) -> Optional[str]:
        # Steps are evaluated in order. Return the first one that is pending/available and can_access.
        for estep in evaluated_steps:
            if estep.status in ("pending", "available", "in_progress") and estep.can_access:
                return estep.code
        return None
