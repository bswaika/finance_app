from __future__ import annotations

import uuid

from peewee import CharField, ForeignKeyField, UUIDField

from ..utils.database import BaseModel
from .account import Account


class BankAccount(BaseModel):
    """
    Optional bank details for an account.

    Keeping this in a separate model makes it easier to evolve the schema
    (e.g. additional bank identifiers) without bloating the core Account
    table. There is a logical 1:1 relationship with Account.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    account = ForeignKeyField(Account, backref="bank_account", unique=True, on_delete="CASCADE")

    bank_name = CharField(max_length=255, null=True)
    bank_account_type = CharField(
        max_length=50, null=True
    )  # checking, savings, credit_card, etc. (bank-facing)
    account_number = CharField(max_length=64, null=True)
    routing_number = CharField(max_length=64, null=True)

    class Meta:
        table_name = "bank_accounts"


