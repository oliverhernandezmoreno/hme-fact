from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.models import DTE


class BasePdfRenderer(ABC):
    @abstractmethod
    def render(self, dte: DTE, template_data: dict[str, Any]) -> bytes:
        pass
