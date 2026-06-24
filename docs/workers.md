# Asynchronous Workers (Celery)

We use Celery to process background tasks in an asynchronous, non-blocking manner.
The broker and result backend are powered by **Redis**.

## Configured Tasks
- `send_dte_task`: Dispatches the DTE XML to the SII via the tax provider. Retries automatically on temporary network errors.
- `check_dte_status_task`: Polls the SII to verify if a DTE was accepted or rejected.
- `generate_dte_pdf_task`: Renders the high-quality PDF, including the PDF417 barcode.
- `send_dte_email_task`: Retrieves the generated PDF and XML, attaches them to an HTML email, and sends it to the customer via SMTP.
- `retry_failed_dtes_task`: A Celery Beat scheduled task that runs periodically to find DTEs stuck in `error` state and re-queue them.

## Async Runner Utility
Because Celery operates synchronously, we implemented an `async_task` decorator that bootstraps an asyncio event loop and provides a fresh `AsyncSession` to the task.
