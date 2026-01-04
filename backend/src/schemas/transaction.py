from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel


class TransactionBase(BaseModel):
    account_id: UUID
    category_id: UUID | None = None
    amount: float
    description: str | None = None
    transaction_date: date
    transaction_type: str  # income, expense, transfer
    transfer_to_account_id: UUID | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    category_id: UUID | None = None
    amount: float | None = None
    description: str | None = None
    transaction_date: date | None = None
    transaction_type: str | None = None
    transfer_to_account_id: UUID | None = None


class TransactionRead(TransactionBase):
    id: UUID


