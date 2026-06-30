"""
CLI commands for seeding valid companies, customers, and products for Chilean invoicing.
Usage:
    python -m app.cli.seed_demo_data
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.models import Company, CompanyUser, Customer, Product, User
from app.models.enums import UserRole

logger = logging.getLogger(__name__)

COMPANIES_SEED = [
    {
        "rut": "76.123.456-7",
        "legal_name": "TechCorp Chile SpA",
        "fantasy_name": "TechCorp",
        "giro": "Desarrollo de Software y Consultoría",
        "address": "Av. Providencia 1234, Of. 401",
        "comuna": "Providencia",
        "city": "Santiago",
        "sii_resolution_number": 80,
        "sii_resolution_date": date(2024, 1, 15),
        "is_active": True,
        "onboarding_step": 10,
        "is_onboarding_completed": True,
    },
    {
        "rut": "77.987.654-3",
        "legal_name": "Retail Demo Ltda.",
        "fantasy_name": "RetailDemo",
        "giro": "Comercio al por menor y Distribución",
        "address": "Calle Merced 456",
        "comuna": "Santiago",
        "city": "Santiago",
        "sii_resolution_number": 120,
        "sii_resolution_date": date(2024, 3, 1),
        "is_active": True,
        "onboarding_step": 10,
        "is_onboarding_completed": True,
    },
    {
        "rut": "14.372.204-K",
        "legal_name": "Distribuidora HME Fact Ltda.",
        "fantasy_name": "HME Fact",
        "giro": "Servicios de Facturación Electrónica",
        "address": "Cam. Capilla Quieme Parc. 40, Vegas del sauzal",
        "comuna": "Quillón",
        "city": "Quillón",
        "sii_resolution_number": 150,
        "sii_resolution_date": date(2024, 5, 10),
        "is_active": True,
        "onboarding_step": 10,
        "is_onboarding_completed": True,
    },
]

CUSTOMERS_SEED = [
    {
        "rut": "12.345.678-9",
        "legal_name": "Empresa Cliente Alpha SpA",
        "giro": "Servicios Informáticos e Integración",
        "email": "contacto@alpha.cl",
        "phone": "+56 9 1111 2222",
        "address": "Los Conquistadores 1700",
        "comuna": "Providencia",
        "city": "Santiago",
        "is_active": True,
    },
    {
        "rut": "98.765.432-1",
        "legal_name": "Beta Inversiones SA",
        "giro": "Inversiones y Asesorías Financieras",
        "email": "contacto@beta.cl",
        "phone": "+56 9 3333 4444",
        "address": "Apoquindo 3000",
        "comuna": "Las Condes",
        "city": "Santiago",
        "is_active": True,
    },
    {
        "rut": "11.222.333-4",
        "legal_name": "Gamma Retail Ltda.",
        "giro": "Comercio Establecido y Supermercados",
        "email": "contacto@gamma.cl",
        "phone": "+56 9 5555 6666",
        "address": "Irarrázaval 2000",
        "comuna": "Ñuñoa",
        "city": "Santiago",
        "is_active": True,
    },
    {
        "rut": "76.999.888-0",
        "legal_name": "Cliente de Prueba SpA",
        "giro": "Servicios Comerciales Generales",
        "email": "contacto@pruebaspa.cl",
        "phone": "+56 9 7777 8888",
        "address": "Av. Nueva Providencia 1234",
        "comuna": "Providencia",
        "city": "Santiago",
        "is_active": True,
    },
    {
        "rut": "88.888.888-8",
        "legal_name": "Consumidor Final Genérico",
        "giro": "Particular",
        "email": "particular@correo.cl",
        "phone": "+56 9 9999 9999",
        "address": "Santiago Centro 100",
        "comuna": "Santiago",
        "city": "Santiago",
        "is_active": True,
    },
]

PRODUCTS_SEED = [
    {
        "sku": "SRV-001",
        "name": "Consultoría Técnica (hr)",
        "description": "Hora de consultoría técnica especializada en sistemas cloud",
        "unit": "hr",
        "unit_price": Decimal("85000"),
        "tax_exempt": False,
        "is_active": True,
    },
    {
        "sku": "LIC-001",
        "name": "Licencia Software Anual",
        "description": "Licencia de uso anual de la plataforma SaaS",
        "unit": "un",
        "unit_price": Decimal("250000"),
        "tax_exempt": False,
        "is_active": True,
    },
    {
        "sku": "CAP-001",
        "name": "Capacitación Corporativa",
        "description": "Módulo de capacitación presencial y soporte de inducción",
        "unit": "un",
        "unit_price": Decimal("120000"),
        "tax_exempt": False,
        "is_active": True,
    },
    {
        "sku": "VIA-001",
        "name": "Viáticos y Gastos de Traslado",
        "description": "Reembolso de viáticos y gastos operacionales exentos",
        "unit": "un",
        "unit_price": Decimal("35000"),
        "tax_exempt": True,
        "is_active": True,
    },
]


async def seed_demo_data() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        # 1. Fetch the default superuser/admin user
        email = settings.FIRST_SUPERUSER_EMAIL
        user_result = await session.execute(select(User).where(User.email == email))
        admin_user = user_result.scalar_one_or_none()

        if admin_user is None:
            logger.error(f"❌ User '{email}' not found. Please run the superuser creation first.")
            return

        logger.info(f"👤 Found admin user: {admin_user.email} (ID: {admin_user.id})")

        for company_data in COMPANIES_SEED:
            rut = company_data["rut"]
            comp_result = await session.execute(select(Company).where(Company.rut == rut))
            company = comp_result.scalar_one_or_none()

            # Create or update company
            if company is None:
                company = Company(**company_data)
                session.add(company)
                await session.flush()
                logger.info(f"🏢 Company created: {company.legal_name} ({rut})")
            else:
                for key, val in company_data.items():
                    setattr(company, key, val)
                logger.info(f"🏢 Company updated: {company.legal_name} ({rut})")

            # Link user as OWNER if not linked
            member_result = await session.execute(
                select(CompanyUser).where(
                    CompanyUser.company_id == company.id, CompanyUser.user_id == admin_user.id
                )
            )
            membership = member_result.scalar_one_or_none()
            if membership is None:
                membership = CompanyUser(
                    company_id=company.id,
                    user_id=admin_user.id,
                    role=UserRole.OWNER,
                    is_active=True,
                )
                session.add(membership)
                logger.info(
                    f"🔗 Linked user '{admin_user.email}' as OWNER to '{company.legal_name}'"
                )
            else:
                membership.role = UserRole.OWNER
                membership.is_active = True
                logger.info(
                    f"🔗 Verified user '{admin_user.email}' as OWNER to '{company.legal_name}'"
                )

            # Seed customers for this company
            for customer_data in CUSTOMERS_SEED:
                cust_rut = customer_data["rut"]
                cust_result = await session.execute(
                    select(Customer).where(
                        Customer.company_id == company.id, Customer.rut == cust_rut
                    )
                )
                customer = cust_result.scalar_one_or_none()
                if customer is None:
                    customer = Customer(company_id=company.id, **customer_data)
                    session.add(customer)
                    logger.info(
                        f"   👥 Customer created: {customer_data['legal_name']} "
                        f"for {company.fantasy_name}"
                    )
                else:
                    for key, val in customer_data.items():
                        setattr(customer, key, val)
                    logger.info(
                        f"   👥 Customer updated: {customer_data['legal_name']} "
                        f"for {company.fantasy_name}"
                    )

            # Seed products for this company
            for product_data in PRODUCTS_SEED:
                sku = product_data["sku"]
                prod_result = await session.execute(
                    select(Product).where(Product.company_id == company.id, Product.sku == sku)
                )
                product = prod_result.scalar_one_or_none()
                if product is None:
                    product = Product(company_id=company.id, **product_data)
                    session.add(product)
                    logger.info(
                        f"   📦 Product created: {product_data['name']} "
                        f"(SKU: {sku}) for {company.fantasy_name}"
                    )
                else:
                    for key, val in product_data.items():
                        setattr(product, key, val)
                    logger.info(
                        f"   📦 Product updated: {product_data['name']} "
                        f"(SKU: {sku}) for {company.fantasy_name}"
                    )

        await session.commit()
        logger.info("🎉 Database seeding completed successfully!")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    asyncio.run(seed_demo_data())


if __name__ == "__main__":
    main()
