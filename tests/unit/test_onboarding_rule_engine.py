from uuid import uuid4

from app.models.onboarding import OnboardingSession, OnboardingStepDefinition, OnboardingStepStatus
from app.services.onboarding_rule_engine import OnboardingRuleEngine


def test_evaluate_step_no_dependencies():
    step = OnboardingStepDefinition(
        id=uuid4(),
        code="step1",
        title="Step 1",
        description="First step",
        component_type="Form",
        required=True,
        skippable=False,
        depends_on=[],
        validation_schema={},
        help_content="Help",
    )
    session = OnboardingSession(id=uuid4())
    status = OnboardingStepStatus(
        step_definition_id=step.id,
        step_code="step1",
        status="pending",
    )

    res = OnboardingRuleEngine.evaluate_step(step, session, [status])
    assert res.code == "step1"
    assert res.can_access is True
    assert res.can_complete is True
    assert res.blocking_reasons == []


def test_evaluate_step_with_unmet_dependency():
    step_dep = OnboardingStepDefinition(
        id=uuid4(),
        code="dep1",
        title="Dep",
        component_type="Form",
        validation_schema={},
    )
    step = OnboardingStepDefinition(
        id=uuid4(),
        code="step2",
        title="Step 2",
        depends_on=["dep1"],
        required=True,
        skippable=False,
        component_type="Form",
        validation_schema={},
    )
    session = OnboardingSession(id=uuid4())
    status_dep = OnboardingStepStatus(
        step_definition_id=step_dep.id,
        step_code="dep1",
        status="pending",
    )
    status_step = OnboardingStepStatus(
        step_definition_id=step.id,
        step_code="step2",
        status="pending",
    )

    res = OnboardingRuleEngine.evaluate_step(step, session, [status_dep, status_step])
    assert res.can_access is False
    assert len(res.blocking_reasons) == 1
    assert "Requires step 'dep1'" in res.blocking_reasons[0]


def test_calculate_progress():
    step1 = OnboardingStepDefinition(id=uuid4(), code="s1")
    step2 = OnboardingStepDefinition(id=uuid4(), code="s2")
    session = OnboardingSession(id=uuid4())
    status1 = OnboardingStepStatus(step_definition_id=step1.id, status="completed")
    status2 = OnboardingStepStatus(step_definition_id=step2.id, status="pending")

    progress = OnboardingRuleEngine.calculate_progress(session, [step1, step2], [status1, status2])
    assert progress == 50


def test_determine_next_step():
    from app.schemas.onboarding import StepDefinitionResponse

    estep1 = StepDefinitionResponse(
        code="s1",
        title="S1",
        description="D",
        component_type="F",
        status="completed",
        required=True,
        skippable=False,
        can_access=True,
        can_complete=True,
        can_skip=False,
        blocking_reasons=[],
        validation_schema={},
        help_content="",
    )
    estep2 = StepDefinitionResponse(
        code="s2",
        title="S2",
        description="D",
        component_type="F",
        status="pending",
        required=True,
        skippable=False,
        can_access=True,
        can_complete=True,
        can_skip=False,
        blocking_reasons=[],
        validation_schema={},
        help_content="",
    )
    next_step = OnboardingRuleEngine.determine_next_step([], [estep1, estep2])
    assert next_step == "s2"
