from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEmailProvider(ABC):
    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachments: list[dict[str, object]] | None = None,
    ) -> bool:
        pass
