from __future__ import annotations

from datetime import date
from decimal import Decimal

import factory
from faker import Faker

from app.core.security import hash_password
from app.models import DTE, Company, Customer, DTEItem, Product, User

fake = Faker("es_CL")


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.LazyFunction(fake.name)
    hashed_password = factory.LazyFunction(lambda: hash_password("ChangeMe123!"))
    is_active = True


class CompanyFactory(factory.Factory):
    class Meta:
        model = Company

    rut = factory.Sequence(lambda n: f"76123{n:03d}-7")
    legal_name = factory.Sequence(lambda n: f"Empresa Demo {n} SpA")
    fantasy_name = factory.Sequence(lambda n: f"Empresa Demo {n}")
    giro = "Servicios informaticos"
    address = "Av Providencia 123"
    comuna = "Providencia"
    city = "Santiago"
    is_active = True


class CustomerFactory(factory.Factory):
    class Meta:
        model = Customer

    rut = factory.Sequence(lambda n: f"77123{n:03d}-4")
    legal_name = factory.Sequence(lambda n: f"Cliente Demo {n} SpA")
    giro = "Comercio"
    email = factory.Sequence(lambda n: f"cliente{n}@example.com")
    phone = "+56912345678"
    address = "Alameda 456"
    comuna = "Santiago"
    city = "Santiago"
    is_active = True


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    sku = factory.Sequence(lambda n: f"SKU-{n:04d}")
    name = factory.Sequence(lambda n: f"Servicio Demo {n}")
    description = "Servicio mensual"
    unit = "UN"
    unit_price = Decimal("10000")
    tax_exempt = False
    is_active = True


class DTEFactory(factory.Factory):
    class Meta:
        model = DTE

    dte_type = 33
    folio = factory.Sequence(lambda n: n + 1)
    issue_date = date(2026, 5, 14)
    net_amount = Decimal("10000")
    exempt_amount = Decimal("0")
    tax_amount = Decimal("1900")
    total_amount = Decimal("11900")


class DTEItemFactory(factory.Factory):
    class Meta:
        model = DTEItem

    line_number = 1
    description = "Servicio de facturacion electronica"
    quantity = Decimal("1")
    unit = "UN"
    unit_price = Decimal("10000")
    discount_amount = Decimal("0")
    net_amount = Decimal("10000")
    tax_amount = Decimal("1900")
    total_amount = Decimal("11900")
    tax_exempt = False
