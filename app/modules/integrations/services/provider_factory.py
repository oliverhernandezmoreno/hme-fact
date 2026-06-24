from __future__ import annotations

import httpx

from app.core.config import Settings
from app.modules.integrations.clients import SimpleApiHttpClient
from app.modules.integrations.exceptions import ProviderConfigurationError
from app.modules.integrations.providers import BaseTaxProvider, SimpleApiProvider


class TaxProviderFactory:
    def __init__(
        self,
        settings: Settings,
        *,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings
        self.http_client = http_client

    def create(self) -> BaseTaxProvider:
        provider_name = self.settings.SII_PROVIDER.strip().lower()
        if provider_name == "simpleapi":
            return SimpleApiProvider(
                SimpleApiHttpClient(
                    base_url=self.settings.SIMPLEAPI_BASE_URL,
                    api_key=self.settings.SIMPLEAPI_API_KEY,
                    timeout=self.settings.SIMPLEAPI_TIMEOUT,
                    max_retries=self.settings.TAX_PROVIDER_MAX_RETRIES,
                    backoff_base_seconds=self.settings.TAX_PROVIDER_BACKOFF_BASE_SECONDS,
                    http_client=self.http_client,
                )
            )
        raise ProviderConfigurationError(
            f"Unsupported SII provider: {self.settings.SII_PROVIDER}",
            provider=provider_name,
            retryable=False,
        )
