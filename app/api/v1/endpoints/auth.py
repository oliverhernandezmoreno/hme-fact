from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.core.config import get_settings
from app.schemas.auth import TokenResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    response: Response,
) -> TokenResponse:
    service = AuthService(session)
    user = await service.authenticate(email=form_data.username, password=form_data.password)
    token = service.create_access_token(user)

    settings = get_settings()
    for key in ["access_token", "hme_fact_token", "ohmefact_token"]:
        response.set_cookie(
            key=key,
            value=token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=True if settings.ENVIRONMENT in ("production", "staging") else False,
        )
    return TokenResponse(access_token=token)


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    for key in ["access_token", "hme_fact_token", "ohmefact_token"]:
        response.delete_cookie(
            key=key,
            samesite="lax",
            secure=False,
        )
    return {"detail": "Successfully logged out"}
