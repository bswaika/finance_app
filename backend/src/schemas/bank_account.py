from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class BankAccountBase(BaseModel):
    bank_name: str | None = None
    bank_account_type: str | None = None
    account_number: str | None = None
    routing_number: str | None = None


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountUpdate(BankAccountBase):
    pass


class BankAccountRead(BankAccountBase):
    id: UUID


