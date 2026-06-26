from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    BILLING = "billing"
    VIEWER = "viewer"


class DTEStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    QUEUED = "queued"
    SIGNED = "signed"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PARTIALLY_ACCEPTED = "partially_accepted"
    ERROR = "error"
    CANCELLED = "cancelled"
    PDF_GENERATED = "pdf_generated"
    EMAILED = "emailed"
    CONTINGENCY = "contingency"


class DTEEventType(str, enum.Enum):
    CREATED = "created"
    GENERATED = "generated"
    QUEUED = "queued"
    SIGNED = "signed"
    SENT_TO_SII = "sent_to_sii"
    SII_ACCEPTED = "sii_accepted"
    SII_REJECTED = "sii_rejected"
    SII_STATUS_CHECKED = "sii_status_checked"
    SII_ERROR = "sii_error"
    CANCELLED = "cancelled"
    PDF_GENERATED = "pdf_generated"
    EMAILED = "emailed"
    SII_CONTINGENCY = "sii_contingency"


class DTEXmlType(str, enum.Enum):
    UNSIGNED_DTE = "unsigned_dte"
    SIGNED_DTE = "signed_dte"
    ENVELOPE = "envelope"
    SII_RESPONSE = "sii_response"


class DTEType(enum.IntEnum):
    FACTURA_ELECTRONICA = 33
    FACTURA_EXENTA = 34
    BOLETA_ELECTRONICA = 39
    BOLETA_EXENTA = 41
    NOTA_DEBITO = 56
    NOTA_CREDITO = 61
