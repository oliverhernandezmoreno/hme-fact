from __future__ import annotations

from app.modules.integrations.exceptions.tax import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderConnectionError,
    ProviderHTTPError,
    ProviderRateLimitError,
    ProviderTemporaryError,
    ProviderTimeoutError,
    TaxIntegrationError,
    TaxRejectionError,
    XMLInvalidError,
)

__all__ = [
    "ProviderAuthenticationError",
    "ProviderConfigurationError",
    "ProviderConnectionError",
    "ProviderHTTPError",
    "ProviderRateLimitError",
    "ProviderTemporaryError",
    "ProviderTimeoutError",
    "TaxIntegrationError",
    "TaxRejectionError",
    "XMLInvalidError",
]
