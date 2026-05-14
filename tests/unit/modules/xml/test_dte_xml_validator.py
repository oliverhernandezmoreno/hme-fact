from __future__ import annotations

from decimal import Decimal

import pytest

from app.modules.xml.validators.dte_validator import DTEXmlDataValidator
from app.modules.xml.validators.exceptions import XmlValidationError
from tests.unit.modules.xml.factories import make_dte

pytestmark = [pytest.mark.unit, pytest.mark.xml]


def test_validator_rejects_negative_amounts() -> None:
    dte = make_dte(33)
    dte.total_amount = Decimal("-1")

    with pytest.raises(XmlValidationError) as exc:
        DTEXmlDataValidator().validate(dte)

    assert "total_amount cannot be negative" in exc.value.errors


def test_validator_requires_credit_note_reference() -> None:
    dte = make_dte(61)
    dte.reference_folio = None

    with pytest.raises(XmlValidationError) as exc:
        DTEXmlDataValidator().validate(dte)

    assert "Credit note reference_folio is required" in exc.value.errors
