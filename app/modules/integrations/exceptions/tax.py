from __future__ import annotations

from typing import Any


class TaxIntegrationError(Exception):
    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        status_code: int | None = None,
        payload: dict[str, Any] | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code
        self.payload = payload or {}
        self.retryable = retryable


class ProviderConfigurationError(TaxIntegrationError):
    pass


class ProviderConnectionError(TaxIntegrationError):
    pass


class ProviderTimeoutError(TaxIntegrationError):
    pass


class ProviderHTTPError(TaxIntegrationError):
    pass


class ProviderAuthenticationError(ProviderHTTPError):
    pass


class ProviderRateLimitError(ProviderHTTPError):
    pass


class ProviderTemporaryError(ProviderHTTPError):
    pass


class TaxRejectionError(TaxIntegrationError):
    pass


class XMLInvalidError(TaxIntegrationError):
    pass
