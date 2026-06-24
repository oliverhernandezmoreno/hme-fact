from __future__ import annotations

from app.models.enums import DTEStatus

_ACCEPTED = {"accepted", "aceptado", "aceptada", "ok", "dte_aceptado"}
_PARTIAL = {"partially_accepted", "aceptado_con_reparos", "aceptado reparos", "reparo"}
_REJECTED = {"rejected", "rechazado", "rechazada", "dte_rechazado"}
_SENT = {"sent", "enviado", "recibido", "received", "procesando", "en_proceso"}
_QUEUED = {"queued", "pendiente", "pending", "cola"}
_ERROR = {"error", "failed", "fallido", "timeout"}


def normalize_tax_status(value: object) -> DTEStatus:
    normalized = str(value or "").strip().lower().replace("-", "_")
    normalized = " ".join(normalized.split())
    normalized_underscore = normalized.replace(" ", "_")

    if normalized_underscore in _ACCEPTED:
        return DTEStatus.ACCEPTED
    if normalized_underscore in _PARTIAL:
        return DTEStatus.PARTIALLY_ACCEPTED
    if normalized_underscore in _REJECTED:
        return DTEStatus.REJECTED
    if normalized_underscore in _SENT:
        return DTEStatus.SENT
    if normalized_underscore in _QUEUED:
        return DTEStatus.QUEUED
    if normalized_underscore in _ERROR:
        return DTEStatus.ERROR
    return DTEStatus.SENT
