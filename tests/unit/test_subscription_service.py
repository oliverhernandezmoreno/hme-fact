"""Unit tests for SubscriptionService."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.billing.services.subscription_service import (
    SubscriptionService,
    SubscriptionServiceError,
)


@pytest.fixture
def company_id():
    return uuid.uuid4()


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_plan():
    plan = MagicMock()
    plan.id = uuid.uuid4()
    plan.code = "pyme"
    plan.name = "PyME"
    plan.price = 29990
    plan.currency = "CLP"
    plan.is_active = True
    plan.trial_days = 14
    plan.features = MagicMock()
    return plan


class TestSubscriptionService:
    @pytest.mark.asyncio
    async def test_activate_new_subscription(self, mock_session, company_id, mock_plan):
        svc = SubscriptionService(mock_session)
        mock_sub = MagicMock()
        mock_sub.id = uuid.uuid4()
        mock_sub.status = "active"
        mock_sub.plan_id = mock_plan.id

        with (
            patch.object(svc._plan_repo, "get_by_code", return_value=mock_plan),
            patch.object(svc._sub_repo, "get_by_company", return_value=None),
            patch.object(svc._sub_repo, "create", return_value=mock_sub),
            patch.object(svc, "_ensure_usage_metric", return_value=None),
            patch.object(svc, "_record_billing_event", return_value=None),
        ):
            sub = await svc.activate(company_id, "pyme")

        assert sub.status == "active"

    @pytest.mark.asyncio
    async def test_activate_invalid_plan(self, mock_session, company_id):
        svc = SubscriptionService(mock_session)
        with patch.object(svc._plan_repo, "get_by_code", return_value=None):
            with pytest.raises(SubscriptionServiceError, match="not found"):
                await svc.activate(company_id, "nonexistent")

    @pytest.mark.asyncio
    async def test_activate_already_active(self, mock_session, company_id, mock_plan):
        svc = SubscriptionService(mock_session)
        existing = MagicMock()
        existing.status = "active"

        with (
            patch.object(svc._plan_repo, "get_by_code", return_value=mock_plan),
            patch.object(svc._sub_repo, "get_by_company", return_value=existing),
        ):
            with pytest.raises(SubscriptionServiceError, match="already has an active"):
                await svc.activate(company_id, "pyme")

    @pytest.mark.asyncio
    async def test_suspend_no_subscription(self, mock_session, company_id):
        svc = SubscriptionService(mock_session)
        with patch.object(svc._sub_repo, "get_active", return_value=None):
            with pytest.raises(SubscriptionServiceError, match="No active subscription"):
                await svc.suspend(company_id)

    @pytest.mark.asyncio
    async def test_cancel_at_period_end(self, mock_session, company_id):
        svc = SubscriptionService(mock_session)
        mock_sub = MagicMock()
        mock_sub.id = uuid.uuid4()
        mock_sub.plan = MagicMock()
        mock_sub.plan.currency = "CLP"
        updated = MagicMock()
        updated.status = "active"
        updated.cancel_at_period_end = True

        with (
            patch.object(svc._sub_repo, "get_active", return_value=mock_sub),
            patch.object(svc._sub_repo, "update", return_value=updated),
            patch.object(svc, "_record_billing_event", return_value=None),
        ):
            result = await svc.cancel(company_id, at_period_end=True)

        assert result.cancel_at_period_end is True

    @pytest.mark.asyncio
    async def test_change_plan_upgrade(self, mock_session, company_id, mock_plan):
        svc = SubscriptionService(mock_session)
        new_plan = MagicMock()
        new_plan.id = uuid.uuid4()
        new_plan.code = "business"
        new_plan.name = "Business"
        new_plan.price = 79990  # Higher than PyME
        new_plan.currency = "CLP"

        mock_sub = MagicMock()
        mock_sub.id = uuid.uuid4()
        mock_sub.plan = mock_plan  # current: pyme

        updated = MagicMock()
        updated.plan_id = new_plan.id

        with (
            patch.object(svc._sub_repo, "get_active", return_value=mock_sub),
            patch.object(svc._plan_repo, "get_by_code", return_value=new_plan),
            patch.object(svc._sub_repo, "update", return_value=updated),
            patch.object(svc, "_record_billing_event", return_value=None),
        ):
            result = await svc.change_plan(company_id, "business")

        assert result.plan_id == new_plan.id
