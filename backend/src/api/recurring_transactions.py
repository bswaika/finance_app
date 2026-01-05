from __future__ import annotations

from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from peewee import DoesNotExist

from ..models.account import Account
from ..models.category import Category
from ..models.recurring_transaction import RecurringTransaction
from ..models.user import User
from ..schemas.recurring_transaction import (
    RecurringTransactionCreate,
    RecurringTransactionRead,
    RecurringTransactionUpdate,
)
from ..services.auth_service import get_current_active_user
from ..services.transaction_service import (
    generate_due_recurring_transactions,
    generate_for_recurring_transaction,
)


router = APIRouter()


@router.get("/", response_model=List[RecurringTransactionRead])
async def list_recurring_transactions(
    current_user: User = Depends(get_current_active_user),
) -> List[RecurringTransactionRead]:
    q = RecurringTransaction.select().where(RecurringTransaction.user == current_user)
    return [_rt_to_read(rt) for rt in q]


@router.post("/", response_model=RecurringTransactionRead, status_code=status.HTTP_201_CREATED)
async def create_recurring_transaction(
    rt_in: RecurringTransactionCreate,
    current_user: User = Depends(get_current_active_user),
) -> RecurringTransactionRead:
    try:
        account = Account.get(Account.id == rt_in.account_id, Account.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account_id")

    category = None
    if rt_in.category_id is not None:
        try:
            category = Category.get(Category.id == rt_in.category_id)
        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category_id")

    rt = RecurringTransaction.create(
        user=current_user,
        account=account,
        category=category,
        amount=rt_in.amount,
        description=rt_in.description,
        frequency=rt_in.frequency,
        interval=rt_in.interval,
        start_date=rt_in.start_date,
        end_date=rt_in.end_date,
        next_occurrence=rt_in.next_occurrence,
        is_active=rt_in.is_active,
    )

    return _rt_to_read(rt)


@router.get("/{rt_id}", response_model=RecurringTransactionRead)
async def get_recurring_transaction(
    rt_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> RecurringTransactionRead:
    try:
        rt = RecurringTransaction.get(
            RecurringTransaction.id == rt_id,
            RecurringTransaction.user == current_user,
        )
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring transaction not found")

    return _rt_to_read(rt)


@router.put("/{rt_id}", response_model=RecurringTransactionRead)
async def update_recurring_transaction(
    rt_id: UUID,
    rt_in: RecurringTransactionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> RecurringTransactionRead:
    try:
        rt = RecurringTransaction.get(
            RecurringTransaction.id == rt_id,
            RecurringTransaction.user == current_user,
        )
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring transaction not found")

    update_data = rt_in.dict(exclude_unset=True)

    if "account_id" in update_data:
        try:
            account = Account.get(Account.id == update_data["account_id"], Account.user == current_user)
        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account_id")
        rt.account = account
        update_data.pop("account_id")

    if "category_id" in update_data:
        if update_data["category_id"] is None:
            rt.category = None
        else:
            try:
                category = Category.get(Category.id == update_data["category_id"])
            except DoesNotExist:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category_id")
            rt.category = category
        update_data.pop("category_id")

    for field, value in update_data.items():
        setattr(rt, field, value)
    rt.save()

    return _rt_to_read(rt)


@router.delete("/{rt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_transaction(
    rt_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> None:
    try:
        rt = RecurringTransaction.get(
            RecurringTransaction.id == rt_id,
            RecurringTransaction.user == current_user,
        )
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring transaction not found")

    rt.delete_instance()
    return None


@router.post("/run-due", response_model=int)
async def run_due_recurring_transactions(
    current_user: User = Depends(get_current_active_user),
) -> int:
    """Generate all due occurrences for the current user as of today."""
    txs = generate_due_recurring_transactions(current_user, today=date.today())
    return len(txs)


@router.post("/{rt_id}/generate", response_model=bool)
async def generate_for_single(
    rt_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> bool:
    try:
        rt = RecurringTransaction.get(
            RecurringTransaction.id == rt_id,
            RecurringTransaction.user == current_user,
        )
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring transaction not found")

    tx = generate_for_recurring_transaction(rt)
    return tx is not None


def _rt_to_read(rt: RecurringTransaction) -> RecurringTransactionRead:
    return RecurringTransactionRead(
        id=rt.id,
        account_id=rt.account_id,
        category_id=rt.category_id,
        amount=float(rt.amount),
        description=rt.description,
        frequency=rt.frequency,
        interval=int(rt.interval or 1),
        start_date=rt.start_date,
        end_date=rt.end_date,
        next_occurrence=rt.next_occurrence,
        is_active=rt.is_active,
    )


