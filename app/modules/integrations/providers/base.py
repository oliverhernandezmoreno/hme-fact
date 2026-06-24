from __future__ import annotations

from abc import ABC, abstractmethod

from app.modules.integrations.schemas import (
    CompanyInfoResponse,
    ProviderHealthResponse,
    TaxProviderResponse,
    TaxSendRequest,
)


class BaseTaxProvider(ABC):
    provider_name: str

    @abstractmethod
    async def send_dte(self, request: TaxSendRequest) -> TaxProviderResponse:
        raise NotImplementedError

    @abstractmethod
    async def get_status(self, track_id: str) -> TaxProviderResponse:
        raise NotImplementedError

    @abstractmethod
    async def validate_connection(self) -> ProviderHealthResponse:
        raise NotImplementedError

    @abstractmethod
    async def generate_pdf(self, track_id: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def get_company_info(self, rut: str) -> CompanyInfoResponse:
        raise NotImplementedError
