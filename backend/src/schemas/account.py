from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from .bank_account import BankAccountCreate, BankAccountRead, BankAccountUpdate


class AccountBase(BaseModel):
    name: str
    account_type: str
    balance: float = 0.0
    currency: str = "USD"
    is_active: bool = True


class AccountCreate(AccountBase):
    bank_account: BankAccountCreate | None = None


class AccountUpdate(BaseModel):
    name: str | None = None
    account_type: str | None = None
    balance: float | None = None
    currency: str | None = None
    is_active: bool | None = None
    bank_account: BankAccountUpdate | None = None


class AccountRead(AccountBase):
    id: UUID
    bank_account: BankAccountRead | None = None


