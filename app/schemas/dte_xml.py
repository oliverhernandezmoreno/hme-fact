from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import DTEXmlType


class DTEXmlGenerateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dte_id: uuid.UUID
    xml_type: DTEXmlType
    generated_at: datetime
    xml_content: str
