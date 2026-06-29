from __future__ import annotations

import logging

from app.modules.notifications.providers.base import BaseEmailProvider
from app.modules.notifications.providers.smtp import SmtpEmailProvider

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, provider: BaseEmailProvider | None = None) -> None:
        self.provider = provider or SmtpEmailProvider()

    def send_dte_notification(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        pdf_content: bytes | None = None,
        xml_content: bytes | None = None,
        folio: str | int = "",
    ) -> bool:
        attachments = []
        if pdf_content:
            attachments.append({"filename": f"dte_{folio}.pdf", "content": pdf_content})
        if xml_content:
            attachments.append({"filename": f"dte_{folio}.xml", "content": xml_content})

        logger.info("Sending DTE notification email", extra={"to": to_email, "folio": folio})
        return self.provider.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            attachments=attachments,
        )

    def send_simple_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
    ) -> bool:
        logger.info("Sending simple notification email", extra={"to": to_email, "subject": subject})
        return self.provider.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )
