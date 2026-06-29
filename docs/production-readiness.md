# Production Readiness Architecture

The HME Fact Phase 5 update introduces several crucial components to elevate the system from a prototype to a production-grade SaaS.

## Key Additions
1. **Asynchronous Background Processing:** Celery + Redis offload heavy I/O operations (PDF rendering, email sending, SII communication) from the main API thread.
2. **Observability:** Structured JSON Logging with injected request and tenant context variables enables log ingestion into ELK/Datadog.
3. **Decoupled File Storage:** A unified interface for file storage allows saving generated PDFs and XMLs locally now, with a straightforward upgrade path to AWS S3.
4. **Audit Logging:** Critical state transitions and DTE events are asynchronously logged with complete context (IP, User Agent, User ID).
5. **Certificate Security:** PFX certificates and passwords are now encrypted at rest using AES-256-GCM.

---

## General System Audit & Production Plan

A complete general audit of the codebase was conducted. The main highlights, resolved issues, and a detailed production checklist have been documented:

- **Full Audit Report:** See [system-audit.md](file:///home/ohm/Documentos/hme-fact/docs/system-audit.md) for full details.
- **Resolved Bugs:** Fixed a critical bug in `retry_failed_dtes_task` (undefined `select` from `sqlalchemy` in Celery workers).
- **TypeScript & Tests:** All frontend TypeScript errors were fixed, and both Vitest (frontend) and Pytest (backend) suites pass with 100% success.
- **Production Checklist:** Plan includes migrating the file storage driver to AWS S3, configuring transactional mailers (SES/SendGrid), setting up cloud database/cache nodes, and obtaining the official SII resolution via the Maullin certification environment.
