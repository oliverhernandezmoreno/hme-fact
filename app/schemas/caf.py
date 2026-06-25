from typing import Optional
from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from app.schemas.common import ORMModel

class CAFFileResponse(ORMModel):
    id: UUID
    company_id: UUID
    dte_type: int
    folio_from: int
    folio_to: int
    authorization_date: date
    current_folio: Optional[int]
    
    # We do NOT return the private key in the response

class CAFFIleUploadResponse(BaseModel):
    message: str
    caf: CAFFileResponse
