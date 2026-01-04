from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from peewee import DoesNotExist

from ..models.account import Account
from ..models.bank_account import BankAccount
from ..models.user import User
from ..schemas.account import AccountCreate, AccountRead, AccountUpdate
from ..schemas.bank_account import BankAccountRead
from ..services.auth_service import get_current_active_user


router = APIRouter()


@router.get("/", response_model=List[AccountRead])
async def list_accounts(current_user: User = Depends(get_current_active_user)) -> List[AccountRead]:
    accounts = Account.select().where(Account.user == current_user)
    return [
        _account_to_read(a)
        for a in accounts
    ]


@router.post("/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_in: AccountCreate,
    current_user: User = Depends(get_current_active_user),
) -> AccountRead:
    account = Account.create(
        user=current_user,
        name=account_in.name,
        account_type=account_in.account_type,
        balance=account_in.balance,
        currency=account_in.currency,
        is_active=account_in.is_active,
    )
    # Optional bank account details
    if account_in.bank_account is not None:
        BankAccount.create(
            account=account,
            bank_name=account_in.bank_account.bank_name,
            bank_account_type=account_in.bank_account.bank_account_type,
            account_number=account_in.bank_account.account_number,
            routing_number=account_in.bank_account.routing_number,
        )

    return _account_to_read(account)


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> AccountRead:
    try:
        account = Account.get(Account.id == account_id, Account.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    return _account_to_read(account)


@router.put("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: UUID,
    account_in: AccountUpdate,
    current_user: User = Depends(get_current_active_user),
) -> AccountRead:
    try:
        account = Account.get(Account.id == account_id, Account.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    update_data = account_in.dict(exclude_unset=True)

    # Handle nested bank_account updates separately
    bank_update = update_data.pop("bank_account", None)

    for field, value in update_data.items():
        setattr(account, field, value)
    account.save()

    if bank_update is not None:
        bank = BankAccount.get_or_none(BankAccount.account == account)
        if bank is None:
            # Create new bank account record
            BankAccount.create(
                account=account,
                bank_name=bank_update.bank_name,
                bank_account_type=bank_update.bank_account_type,
                account_number=bank_update.account_number,
                routing_number=bank_update.routing_number,
            )
        else:
            # Patch existing bank account record
            for field, value in bank_update.dict(exclude_unset=True).items():
                setattr(bank, field, value)
            bank.save()

    return _account_to_read(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> None:
    try:
        account = Account.get(Account.id == account_id, Account.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    # Soft delete: mark as inactive
    account.is_active = False
    account.save()

    return None


def _account_to_read(account: Account) -> AccountRead:
    bank = BankAccount.get_or_none(BankAccount.account == account)
    bank_schema: BankAccountRead | None = None
    if bank is not None:
        bank_schema = BankAccountRead(
            id=bank.id,
            bank_name=bank.bank_name,
            bank_account_type=bank.bank_account_type,
            account_number=bank.account_number,
            routing_number=bank.routing_number,
        )

    return AccountRead(
        id=account.id,
        name=account.name,
        account_type=account.account_type,
        balance=float(account.balance),
        currency=account.currency,
        is_active=account.is_active,
        bank_account=bank_schema,
    )


