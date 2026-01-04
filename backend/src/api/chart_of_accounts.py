from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from peewee import DoesNotExist
from pydantic import BaseModel

from ..models.chart_of_accounts import ChartOfAccount
from ..models.user import User
from ..services.auth_service import get_current_active_user


router = APIRouter()


class ChartOfAccountBase(BaseModel):
    account_code: str
    account_name: str
    account_type: str  # asset, liability, equity, income, expense
    parent_account_id: UUID | None = None
    is_active: bool = True


class ChartOfAccountCreate(ChartOfAccountBase):
    pass


class ChartOfAccountUpdate(BaseModel):
    account_code: str | None = None
    account_name: str | None = None
    account_type: str | None = None
    parent_account_id: UUID | None = None
    is_active: bool | None = None


class ChartOfAccountRead(ChartOfAccountBase):
    id: UUID


@router.get("/", response_model=List[ChartOfAccountRead])
async def list_chart_of_accounts(
    current_user: User = Depends(get_current_active_user),
) -> List[ChartOfAccountRead]:
    qs = ChartOfAccount.select().where(ChartOfAccount.user == current_user)
    return [_coa_to_read(a) for a in qs]


@router.post("/", response_model=ChartOfAccountRead, status_code=status.HTTP_201_CREATED)
async def create_chart_of_account(
    coa_in: ChartOfAccountCreate,
    current_user: User = Depends(get_current_active_user),
) -> ChartOfAccountRead:
    parent = None
    if coa_in.parent_account_id is not None:
        try:
            parent = ChartOfAccount.get(ChartOfAccount.id == coa_in.parent_account_id)
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent_account_id",
            )

    coa = ChartOfAccount.create(
        user=current_user,
        account_code=coa_in.account_code,
        account_name=coa_in.account_name,
        account_type=coa_in.account_type,
        parent_account=parent,
        is_active=coa_in.is_active,
    )
    return _coa_to_read(coa)


@router.put("/{coa_id}", response_model=ChartOfAccountRead)
async def update_chart_of_account(
    coa_id: UUID,
    coa_in: ChartOfAccountUpdate,
    current_user: User = Depends(get_current_active_user),
) -> ChartOfAccountRead:
    try:
        coa = ChartOfAccount.get(ChartOfAccount.id == coa_id, ChartOfAccount.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart of account not found")

    update_data = coa_in.dict(exclude_unset=True)

    if "parent_account_id" in update_data:
        if update_data["parent_account_id"] is None:
            coa.parent_account = None
        else:
            try:
                parent = ChartOfAccount.get(ChartOfAccount.id == update_data["parent_account_id"])
            except DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid parent_account_id",
                )
            coa.parent_account = parent
        update_data.pop("parent_account_id")

    for field, value in update_data.items():
        setattr(coa, field, value)
    coa.save()

    return _coa_to_read(coa)


@router.delete("/{coa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chart_of_account(
    coa_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> None:
    try:
        coa = ChartOfAccount.get(ChartOfAccount.id == coa_id, ChartOfAccount.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart of account not found")

    coa.delete_instance()
    return None


def _coa_to_read(coa: ChartOfAccount) -> ChartOfAccountRead:
    return ChartOfAccountRead(
        id=coa.id,
        account_code=coa.account_code,
        account_name=coa.account_name,
        account_type=coa.account_type,
        parent_account_id=coa.parent_account.id if coa.parent_account is not None else None,
        is_active=coa.is_active,
    )


