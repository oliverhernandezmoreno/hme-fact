"""Unit tests for QuotaService."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.billing.services.quota_service import QuotaResult, QuotaService


@pytest.fixture
def company_id():
    return uuid.uuid4()


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_sub_with_features(company_id):
    feat = MagicMock()
    feat.dte_limit = 100
    feat.users_limit = 10
    feat.api_access = True
    feat.api_rate_limit_per_min = 60
    feat.storage_limit_mb = 1024

    plan = MagicMock()
    plan.code = "pyme"
    plan.name = "PyME"
    plan.features = feat

    sub = MagicMock()
    sub.company_id = company_id
    sub.status = "active"
    sub.plan = plan

    return sub


class TestQuotaResult:
    def test_remaining_unlimited(self):
        result = QuotaResult(allowed=True, used=999, limit=-1, feature="dte_limit")
        assert result.remaining == -1

    def test_remaining_limited(self):
        result = QuotaResult(allowed=True, used=30, limit=100, feature="dte_limit")
        assert result.remaining == 70

    def test_usage_pct(self):
        result = QuotaResult(allowed=True, used=80, limit=100, feature="dte_limit")
        assert result.usage_pct == 80.0

    def test_usage_pct_zero_limit(self):
        result = QuotaResult(allowed=False, used=0, limit=0, feature="dte_limit")
        assert result.usage_pct == 0.0


class TestQuotaService:
    @pytest.mark.asyncio
    async def test_check_dte_quota_no_subscription(self, mock_session, company_id):
        svc = QuotaService(mock_session)
        with patch.object(svc._sub_repo, "get_active", return_value=None):
            result = await svc.check_dte_quota(company_id)
        assert result.allowed is False
        assert result.reason == "No active subscription"

    @pytest.mark.asyncio
    async def test_check_dte_quota_within_limit(
        self, mock_session, company_id, mock_sub_with_features
    ):
        svc = QuotaService(mock_session)
        mock_metric = MagicMock()
        mock_metric.dtes_emitted = 30

        with (
            patch.object(svc._sub_repo, "get_active", return_value=mock_sub_with_features),
            patch.object(svc._usage_repo, "get_or_create_current", return_value=mock_metric),
        ):
            result = await svc.check_dte_quota(company_id)

        assert result.allowed is True
        assert result.used == 30
        assert result.limit == 100
        assert result.remaining == 70

    @pytest.mark.asyncio
    async def test_check_dte_quota_exceeded(self, mock_session, company_id, mock_sub_with_features):
        svc = QuotaService(mock_session)
        mock_metric = MagicMock()
        mock_metric.dtes_emitted = 100  # At limit

        with (
            patch.object(svc._sub_repo, "get_active", return_value=mock_sub_with_features),
            patch.object(svc._usage_repo, "get_or_create_current", return_value=mock_metric),
        ):
            result = await svc.check_dte_quota(company_id)

        assert result.allowed is False
        assert "exceeded" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_check_dte_quota_unlimited(
        self, mock_session, company_id, mock_sub_with_features
    ):
        mock_sub_with_features.plan.features.dte_limit = -1
        svc = QuotaService(mock_session)
        mock_metric = MagicMock()
        mock_metric.dtes_emitted = 50000

        with (
            patch.object(svc._sub_repo, "get_active", return_value=mock_sub_with_features),
            patch.object(svc._usage_repo, "get_or_create_current", return_value=mock_metric),
        ):
            result = await svc.check_dte_quota(company_id)

        assert result.allowed is True
        assert result.remaining == -1

    @pytest.mark.asyncio
    async def test_check_api_access_denied(self, mock_session, company_id, mock_sub_with_features):
        mock_sub_with_features.plan.features.api_access = False
        svc = QuotaService(mock_session)

        with patch.object(svc._sub_repo, "get_active", return_value=mock_sub_with_features):
            result = await svc.check_api_access(company_id)

        assert result.allowed is False
        assert "API access not included" in result.reason

    @pytest.mark.asyncio
    async def test_get_usage_summary(self, mock_session, company_id, mock_sub_with_features):
        svc = QuotaService(mock_session)
        mock_metric = MagicMock()
        mock_metric.dtes_emitted = 25
        mock_metric.api_calls = 100
        mock_metric.active_users = 3
        mock_metric.storage_used_bytes = 1024 * 1024
        mock_metric.period_month = 6
        mock_metric.period_year = 2026

        with (
            patch.object(svc._sub_repo, "get_active", return_value=mock_sub_with_features),
            patch.object(svc._usage_repo, "get_or_create_current", return_value=mock_metric),
        ):
            summary = await svc.get_usage_summary(company_id)

        assert summary is not None
        assert summary.plan_code == "pyme"
        assert summary.dtes_used == 25
        assert summary.dtes_limit == 100
        assert summary.api_access is True
