# OhmEFACT - Backend-Driven Tenant Onboarding Engine

## Concept
The onboarding process is strictly backend-driven. The frontend acts as a "dumb" renderer that displays steps, forms, and actions based entirely on the JSON payload provided by the backend API.

## Core Principles
1. **No hardcoded steps in UI:** The frontend loops over the `steps` array received from the API and dynamically selects the correct React component based on `component_type`.
2. **Rule Engine:** The backend dictates what steps are available (`can_access`), which ones block others (`blocking_reasons`), and what is the `next_recommended_step`.
3. **Auditability:** Every user interaction (start, view step, save, complete, skip) is logged as an `OnboardingEvent`.
4. **Resumability:** A user can stop at any time and resume later. The state is fully persisted in `onboarding_sessions` and `onboarding_step_status`.

## Database Entities
- **OnboardingWorkflow:** Templates for onboarding. Allows different flows per country, plan, or business type.
- **OnboardingStepDefinition:** The individual steps belonging to a workflow. Contains the JSON schemas for validation and dependency rules.
- **OnboardingSession:** A company's active instance of a workflow. Tracks global progress.
- **OnboardingStepStatus:** Tracks the status of each step within a session (pending, in_progress, completed, skipped).
- **OnboardingEvent:** Append-only audit log for analytics.

## Workflows
The initial active workflow is `chile_dte_standard_onboarding`.
It defines 10 sequential steps:
1. `welcome`
2. `company_profile`
3. `tax_configuration`
4. `digital_certificate`
5. `caf_upload`
6. `users_setup`
7. `products_setup`
8. `customers_setup`
9. `first_dte`
10. `completion`

## APIs
- `GET /api/v1/onboarding/session`: Retrieves the full state, calculating rules on the fly.
- `POST /api/v1/onboarding/steps/{step_code}/save`: Auto-saves form data.
- `POST /api/v1/onboarding/steps/{step_code}/complete`: Validates and marks the step as completed.
