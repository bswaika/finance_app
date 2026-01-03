from __future__ import annotations

import uuid

from peewee import BooleanField, CharField, DateField, DecimalField, ForeignKeyField, UUIDField

from ..utils.database import BaseModel
from .account import Account
from .category import Category
from .user import User


class RecurringTransaction(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKeyField(User, backref="recurring_transactions", on_delete="CASCADE")
    account = ForeignKeyField(Account, backref="recurring_transactions", on_delete="CASCADE")
    category = ForeignKeyField(Category, backref="recurring_transactions", null=True, on_delete="SET NULL")
    amount = DecimalField(max_digits=14, decimal_places=2)
    description = CharField(max_length=500, null=True)
    frequency = CharField(max_length=20)  # daily, weekly, monthly, yearly
    interval = DecimalField(max_digits=4, decimal_places=0, default=1)
    start_date = DateField()
    end_date = DateField(null=True)
    next_occurrence = DateField()
    is_active = BooleanField(default=True)

    class Meta:
        table_name = "recurring_transactions"


