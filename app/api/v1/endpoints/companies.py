from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, SessionDep
from app.models import CompanyUser, UserRole
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate

router = APIRouter()


@router.get("", response_model=list[CompanyRead])
async def list_companies(
    session: SessionDep,
    current_user: CurrentUserDep,
) -> list[CompanyRead]:
    companies = await CompanyRepository(session).list_for_user(current_user.id)
    return [CompanyRead.model_validate(company) for company in companies]


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    payload: CompanyCreate,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> CompanyRead:
    company = await CompanyRepository(session).create(payload.model_dump())
    membership = CompanyUser(company_id=company.id, user_id=current_user.id, role=UserRole.OWNER)
    session.add(membership)
    await session.commit()
    await session.refresh(company)
    return CompanyRead.model_validate(company)


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> CompanyRead:
    companies = await CompanyRepository(session).list_for_user(current_user.id)
    company = next((item for item in companies if item.id == company_id), None)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return CompanyRead.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: uuid.UUID,
    payload: CompanyUpdate,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> CompanyRead:
    companies = await CompanyRepository(session).list_for_user(current_user.id)
    company = next((item for item in companies if item.id == company_id), None)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    updated = await CompanyRepository(session).update(
        company,
        payload.model_dump(exclude_unset=True),
    )
    return CompanyRead.model_validate(updated)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> None:
    companies = await CompanyRepository(session).list_for_user(current_user.id)
    company = next((item for item in companies if item.id == company_id), None)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    await CompanyRepository(session).delete(company)
