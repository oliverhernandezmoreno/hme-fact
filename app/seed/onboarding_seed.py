import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.onboarding import OnboardingStepDefinition, OnboardingWorkflow


async def seed_chile_dte_onboarding(db: AsyncSession):
    # Check if workflow already exists
    existing = await db.execute(
        select(OnboardingWorkflow).where(OnboardingWorkflow.code == "chile_dte_standard_onboarding")
    )
    if existing.scalars().first():
        print("Workflow 'chile_dte_standard_onboarding' already exists. Skipping seed.")
        return

    print("Seeding Workflow: chile_dte_standard_onboarding")

    workflow = OnboardingWorkflow(
        code="chile_dte_standard_onboarding",
        name="Onboarding Estándar Facturación Electrónica Chile",
        description="Flujo completo para configurar y emitir el primer DTE en Chile.",
        country_code="CL",
        version="1.0.0",
        is_active=True,
    )
    db.add(workflow)
    await db.flush()  # To get workflow.id

    steps_data = [
        {
            "code": "welcome",
            "title": "Bienvenido a hmEFACT",
            "description": "Comencemos a configurar tu plataforma de facturación. Te guiaremos paso a paso.",
            "component_type": "welcome_screen",
            "order_index": 1,
            "required": True,
            "skippable": False,
            "depends_on": [],
        },
        {
            "code": "company_profile",
            "title": "Perfil de la Empresa",
            "description": "Ingresa los datos legales de tu empresa.",
            "component_type": "company_profile_form",
            "order_index": 2,
            "required": True,
            "skippable": False,
            "depends_on": ["welcome"],
        },
        {
            "code": "tax_configuration",
            "title": "Configuración Tributaria",
            "description": "Información requerida por el SII (Resolución, IVA).",
            "component_type": "tax_configuration_form",
            "order_index": 3,
            "required": True,
            "skippable": False,
            "depends_on": ["company_profile"],
        },
        {
            "code": "digital_certificate",
            "title": "Certificado Digital",
            "description": "Sube tu certificado .pfx o .p12 para poder firmar los documentos.",
            "component_type": "certificate_upload_form",
            "order_index": 4,
            "required": True,
            "skippable": False,
            "depends_on": ["company_profile"],
        },
        {
            "code": "caf_upload",
            "title": "Carga de Folios (CAF)",
            "description": "Sube los folios autorizados por el SII.",
            "component_type": "caf_upload_form",
            "order_index": 5,
            "required": True,
            "skippable": False,
            "depends_on": ["company_profile"],
        },
        {
            "code": "users_setup",
            "title": "Usuarios del Sistema",
            "description": "Invita a tu contador y equipo de ventas.",
            "component_type": "users_setup_form",
            "order_index": 6,
            "required": False,
            "skippable": True,
            "depends_on": ["welcome"],
        },
        {
            "code": "products_setup",
            "title": "Catálogo de Productos",
            "description": "Crea o importa tus productos para facturar más rápido.",
            "component_type": "products_setup_form",
            "order_index": 7,
            "required": True,
            "skippable": False,
            "depends_on": ["company_profile"],
        },
        {
            "code": "customers_setup",
            "title": "Base de Clientes",
            "description": "Crea o importa tus clientes habituales.",
            "component_type": "customers_setup_form",
            "order_index": 8,
            "required": True,
            "skippable": False,
            "depends_on": ["company_profile"],
        },
        {
            "code": "first_dte",
            "title": "Primera Factura",
            "description": "¡Todo listo! Emite tu primer documento.",
            "component_type": "first_dte_wizard",
            "order_index": 9,
            "required": True,
            "skippable": False,
            "depends_on": [
                "company_profile",
                "tax_configuration",
                "digital_certificate",
                "caf_upload",
                "products_setup",
                "customers_setup",
            ],
        },
        {
            "code": "completion",
            "title": "¡Felicitaciones!",
            "description": "Has completado la configuración exitosamente.",
            "component_type": "completion_screen",
            "order_index": 10,
            "required": True,
            "skippable": False,
            "depends_on": ["first_dte"],
        },
    ]

    for step in steps_data:
        s_def = OnboardingStepDefinition(workflow_id=workflow.id, **step)
        db.add(s_def)

    await db.commit()
    print("Seed completed successfully.")


async def main():
    async with AsyncSessionLocal() as session:
        await seed_chile_dte_onboarding(session)


if __name__ == "__main__":
    asyncio.run(main())
