from __future__ import annotations

import uuid

from peewee import BooleanField, CharField, DecimalField, ForeignKeyField, UUIDField

from ..utils.database import BaseModel
from .user import User


class Account(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKeyField(User, backref="accounts", on_delete="CASCADE")
    name = CharField(max_length=255)
    account_type = CharField(max_length=50)  # checking, savings, credit_card, etc.
    balance = DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = CharField(max_length=10, default="USD")
    is_active = BooleanField(default=True)
    is_shared = BooleanField(default=False)  # reserved for future family sharing

    class Meta:
        table_name = "accounts"


