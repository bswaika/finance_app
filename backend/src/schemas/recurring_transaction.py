from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel


class RecurringTransactionBase(BaseModel):
    account_id: UUID
    category_id: UUID | None = None
    amount: float
    description: str | None = None
    frequency: str  # daily, weekly, monthly, yearly
    interval: int = 1
    start_date: date
    end_date: date | None = None
    next_occurrence: date
    is_active: bool = True


class RecurringTransactionCreate(RecurringTransactionBase):
    pass


class RecurringTransactionUpdate(BaseModel):
    category_id: UUID | None = None
    amount: float | None = None
    description: str | None = None
    frequency: str | None = None
    interval: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    next_occurrence: date | None = None
    is_active: bool | None = None


class RecurringTransactionRead(RecurringTransactionBase):
    id: UUID


