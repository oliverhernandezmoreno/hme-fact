"""
CLI commands for hmEFact platform seeding.
Usage:
    python -m app.cli.seed_fase6
"""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)

PLANS_SEED = [
    {
        "code": "starter",
        "name": "Starter",
        "description": "Plan gratuito para comenzar — ideal para empresas pequeñas.",
        "price": 0,
        "currency": "CLP",
        "billing_cycle": "monthly",
        "trial_days": 0,
        "sort_order": 1,
        "is_active": True,
        "is_public": True,
        "features": {
            "dte_limit": 50,
            "users_limit": 2,
            "branches_limit": 1,
            "api_access": False,
            "api_rate_limit_per_min": 0,
            "storage_limit_mb": 512,
            "support_level": "community",
        },
    },
    {
        "code": "pyme",
        "name": "PyME",
        "description": "Para PyMEs en crecimiento con necesidades de facturación moderadas.",
        "price": 29990,
        "currency": "CLP",
        "billing_cycle": "monthly",
        "trial_days": 14,
        "sort_order": 2,
        "is_active": True,
        "is_public": True,
        "features": {
            "dte_limit": 500,
            "users_limit": 10,
            "branches_limit": 3,
            "api_access": True,
            "api_rate_limit_per_min": 60,
            "storage_limit_mb": 5120,
            "support_level": "email",
        },
    },
    {
        "code": "business",
        "name": "Business",
        "description": (
            "Para empresas medianas con alto volumen de facturación y múltiples sucursales."
        ),
        "price": 79990,
        "currency": "CLP",
        "billing_cycle": "monthly",
        "trial_days": 14,
        "sort_order": 3,
        "is_active": True,
        "is_public": True,
        "features": {
            "dte_limit": 2000,
            "users_limit": 50,
            "branches_limit": 10,
            "api_access": True,
            "api_rate_limit_per_min": 300,
            "storage_limit_mb": 20480,
            "support_level": "priority",
        },
    },
    {
        "code": "enterprise",
        "name": "Enterprise",
        "description": "Facturación ilimitada, soporte dedicado y SLA garantizado.",
        "price": 0,  # Custom pricing
        "currency": "CLP",
        "billing_cycle": "monthly",
        "trial_days": 0,
        "sort_order": 4,
        "is_active": True,
        "is_public": False,  # Contact sales
        "features": {
            "dte_limit": -1,  # Unlimited
            "users_limit": -1,
            "branches_limit": -1,
            "api_access": True,
            "api_rate_limit_per_min": 1000,
            "storage_limit_mb": -1,
            "support_level": "dedicated",
        },
    },
]


async def seed_plans_and_roles() -> None:
    from sqlalchemy import select

    from app.db.session import AsyncSessionLocal
    from app.models.billing import SubscriptionFeature, SubscriptionPlan
    from app.modules.rbac.services.rbac_service import RBACService

    async with AsyncSessionLocal() as session:
        # ── Seed Plans ────────────────────────────────────────────────────
        for plan_data in PLANS_SEED:
            features_data = plan_data.pop("features")
            result = await session.scalars(
                select(SubscriptionPlan).where(SubscriptionPlan.code == plan_data["code"])
            )
            existing = result.first()

            if existing is None:
                plan = SubscriptionPlan(**plan_data)
                session.add(plan)
                await session.flush()

                feature = SubscriptionFeature(plan_id=plan.id, **features_data)
                session.add(feature)
                logger.info(f"✅ Plan '{plan_data['code']}' created")
            else:
                logger.info(f"⏭  Plan '{plan_data['code']}' already exists — skipping")
                plan_data["features"] = features_data  # Restore for next iteration
                continue

            plan_data["features"] = features_data

        await session.commit()

        # ── Seed Roles & Permissions ──────────────────────────────────────
        rbac_svc = RBACService(session)
        await rbac_svc.seed_default_roles()
        logger.info("✅ System roles and permissions seeded")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    asyncio.run(seed_plans_and_roles())
    print("\n🎉 hmEFact Fase 6 seed completed successfully!")
    print("   Plans: Starter, PyME, Business, Enterprise")
    print("   Roles: SuperAdmin, CompanyOwner, Accountant, Seller, Viewer, APIUser")


if __name__ == "__main__":
    main()
