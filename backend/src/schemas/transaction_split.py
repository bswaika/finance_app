from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class TransactionSplitBase(BaseModel):
    chart_of_account_id: UUID
    amount: float
    memo: str | None = None


class TransactionSplitCreate(TransactionSplitBase):
    pass


class TransactionSplitRead(TransactionSplitBase):
    id: UUID


