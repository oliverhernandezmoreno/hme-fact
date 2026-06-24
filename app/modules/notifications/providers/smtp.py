from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings
from app.modules.notifications.providers.base import BaseEmailProvider

logger = logging.getLogger(__name__)


class SmtpEmailProvider(BaseEmailProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachments: list[dict[str, object]] | None = None,
    ) -> bool:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg.set_content("Por favor active la vista HTML para visualizar este mensaje.")
        msg.add_alternative(html_content, subtype="html")

        if attachments:
            for attachment in attachments:
                file_name = str(attachment.get("filename", "document.pdf"))
                content = attachment.get("content")
                if isinstance(content, bytes):
                    msg.add_attachment(
                        content,
                        maintype="application",
                        subtype="pdf",
                        filename=file_name,
                    )

        try:
            with smtplib.SMTP(self.settings.SMTP_HOST, self.settings.SMTP_PORT) as server:
                if self.settings.SMTP_USER and self.settings.SMTP_PASSWORD:
                    server.login(self.settings.SMTP_USER, self.settings.SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as exc:
            logger.error("Failed to send email via SMTP", exc_info=exc)
            return False
