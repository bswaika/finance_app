from __future__ import annotations

import uuid

from peewee import BooleanField, CharField, DateField, DecimalField, ForeignKeyField, UUIDField

from ..utils.database import BaseModel
from .account import Account
from .category import Category
from .user import User


class Transaction(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKeyField(User, backref="transactions", on_delete="CASCADE")
    account = ForeignKeyField(Account, backref="transactions", on_delete="CASCADE")
    category = ForeignKeyField(Category, backref="transactions", null=True, on_delete="SET NULL")
    amount = DecimalField(max_digits=14, decimal_places=2)
    description = CharField(max_length=500, null=True)
    transaction_date = DateField()
    transaction_type = CharField(max_length=20)  # income, expense, transfer
    transfer_to_account = ForeignKeyField(
        Account, backref="incoming_transfers", null=True, on_delete="SET NULL"
    )
    is_recurring = BooleanField(default=False)
    recurring_template_id = UUIDField(null=True)

    class Meta:
        table_name = "transactions"


