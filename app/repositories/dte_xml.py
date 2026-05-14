from __future__ import annotations

from app.models import DTEXml
from app.repositories.base import BaseRepository


class DTEXmlRepository(BaseRepository[DTEXml]):
    model = DTEXml
