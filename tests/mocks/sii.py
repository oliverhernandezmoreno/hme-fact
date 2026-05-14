from __future__ import annotations

import httpx


def mock_sii_upload_success(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        status_code=200,
        json={"track_id": "123456789", "status": "RECIBIDO"},
        request=request,
    )


def mock_sii_upload_rejected(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        status_code=422,
        json={"status": "RECHAZADO", "errors": ["XML schema validation failed"]},
        request=request,
    )


def mock_simpleapi_status_success(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        status_code=200,
        json={"track_id": "123456789", "estado": "ACEPTADO"},
        request=request,
    )
