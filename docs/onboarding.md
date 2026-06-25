# Onboarding Architecture (Phase 7A)

## Overview
This document describes the architectural implementation of the OhmEFACT Intelligent Onboarding Platform, a completely modular, decoupled onboarding system for new companies.

## Database Schema
The database uses three decoupled tables to track state:
1. `onboarding_sessions`: Tracks the company's overall progress.
2. `onboarding_steps`: Holds dynamic metadata about the steps (order, title).
3. `onboarding_step_status`: M:N relation tracking completions and durations per session/step.

## Directory Structure
The module lives primarily in `frontend/src/modules/onboarding` and `app/api/v1/endpoints/onboarding`.

### Backend Stack
- **Entities:** SQLAlchemy models (`OnboardingSession`, `OnboardingStep`, `OnboardingStepStatus`).
- **DTOs:** Pydantic schemas (`OnboardingStartRequest`, `OnboardingProgressResponse`).
- **API:** Dedicated `APIRouter` attached to `/api/v1/onboarding`.

### Frontend Stack
- **Context/Store:** Zustand store (`useOnboardingStore`) for state persistence.
- **Components:** `OnboardingSidebar`, `HelpPanel`, `DocumentUploader`, `ProgressStepper`.

## Design Constraints
- Never couple `Onboarding` directly to `Dashboard`.
- Do not hardcode step counts. Use the step list provided by `GET /api/v1/onboarding/steps`.
- Clean Architecture principles applied.

## Steps Defined
1. Bienvenida (Welcome)
2. Empresa (Company details)
3. Configuración Tributaria (Tax configs)
4. Certificado Digital (PFX upload)
5. CAF (CAF upload)
6. Usuarios (Invite users)
7. Productos (Create/Import)
8. Clientes (Create/Import)
9. Primera Factura (Issue first DTE)
10. Finalización (Success page & Redirect)
