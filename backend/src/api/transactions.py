from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from peewee import DoesNotExist

from ..models.account import Account
from ..models.category import Category
from ..models.transaction import Transaction
from ..models.user import User
from ..schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from ..services.import_service import import_transactions_from_json
from ..services.auth_service import get_current_active_user


router = APIRouter()


@router.get("/", response_model=List[TransactionRead])
async def list_transactions(
    current_user: User = Depends(get_current_active_user),
    account_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> List[TransactionRead]:
    query = Transaction.select().where(Transaction.user == current_user)

    if account_id is not None:
        query = query.where(Transaction.account == account_id)
    if category_id is not None:
        query = query.where(Transaction.category == category_id)
    if start_date is not None:
        query = query.where(Transaction.transaction_date >= start_date)
    if end_date is not None:
        query = query.where(Transaction.transaction_date <= end_date)

    query = query.order_by(Transaction.transaction_date.desc()).limit(limit).offset(offset)

    return [
        TransactionRead(
            id=t.id,
            account_id=t.account_id,
            category_id=t.category_id,
            amount=float(t.amount),
            description=t.description,
            transaction_date=t.transaction_date,
            transaction_type=t.transaction_type,
            transfer_to_account_id=t.transfer_to_account_id,
        )
        for t in query
    ]


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    tx_in: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
) -> TransactionRead:
    # Ensure account belongs to user
    try:
        account = Account.get(Account.id == tx_in.account_id, Account.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account_id")

    category = None
    if tx_in.category_id is not None:
        try:
            category = Category.get(Category.id == tx_in.category_id)
        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category_id")

    transfer_to_account = None
    if tx_in.transfer_to_account_id is not None:
        try:
            transfer_to_account = Account.get(Account.id == tx_in.transfer_to_account_id)
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid transfer_to_account_id",
            )

    tx = Transaction.create(
        user=current_user,
        account=account,
        category=category,
        amount=tx_in.amount,
        description=tx_in.description,
        transaction_date=tx_in.transaction_date,
        transaction_type=tx_in.transaction_type,
        transfer_to_account=transfer_to_account,
        is_recurring=False,
    )

    return TransactionRead(
        id=tx.id,
        account_id=tx.account_id,
        category_id=tx.category_id,
        amount=float(tx.amount),
        description=tx.description,
        transaction_date=tx.transaction_date,
        transaction_type=tx.transaction_type,
        transfer_to_account_id=tx.transfer_to_account_id,
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> TransactionRead:
    try:
        tx = Transaction.get(Transaction.id == transaction_id, Transaction.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return TransactionRead(
        id=tx.id,
        account_id=tx.account_id,
        category_id=tx.category_id,
        amount=float(tx.amount),
        description=tx.description,
        transaction_date=tx.transaction_date,
        transaction_type=tx.transaction_type,
        transfer_to_account_id=tx.transfer_to_account_id,
    )


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: UUID,
    tx_in: TransactionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> TransactionRead:
    try:
        tx = Transaction.get(Transaction.id == transaction_id, Transaction.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    update_data = tx_in.dict(exclude_unset=True)

    if "account_id" in update_data:
        try:
            account = Account.get(Account.id == update_data["account_id"], Account.user == current_user)
        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account_id")
        tx.account = account
        update_data.pop("account_id")

    if "category_id" in update_data:
        if update_data["category_id"] is None:
            tx.category = None
        else:
            try:
                category = Category.get(Category.id == update_data["category_id"])
            except DoesNotExist:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category_id")
            tx.category = category
        update_data.pop("category_id")

    if "transfer_to_account_id" in update_data:
        if update_data["transfer_to_account_id"] is None:
            tx.transfer_to_account = None
        else:
            try:
                transfer_to = Account.get(Account.id == update_data["transfer_to_account_id"])
            except DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid transfer_to_account_id",
                )
            tx.transfer_to_account = transfer_to
        update_data.pop("transfer_to_account_id")

    for field, value in update_data.items():
        setattr(tx, field, value)
    tx.save()

    return TransactionRead(
        id=tx.id,
        account_id=tx.account_id,
        category_id=tx.category_id,
        amount=float(tx.amount),
        description=tx.description,
        transaction_date=tx.transaction_date,
        transaction_type=tx.transaction_type,
        transfer_to_account_id=tx.transfer_to_account_id,
    )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> None:
    try:
        tx = Transaction.get(Transaction.id == transaction_id, Transaction.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    tx.delete_instance()
    return None


@router.post("/import")
async def import_transactions(
    payload: dict,
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Import transactions from JSON or base64-encoded CSV.

    See `import_service.import_transactions_from_json` for payload structure.
    """
    ti = import_transactions_from_json(current_user, payload)
    return {
        "id": str(ti.id),
        "status": ti.status,
        "records_imported": ti.records_imported,
        "errors": ti.errors,
    }


