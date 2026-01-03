from __future__ import annotations

import uuid

from peewee import BooleanField, CharField, ForeignKeyField, UUIDField

from ..utils.database import BaseModel
from .user import User


class ChartOfAccount(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKeyField(User, backref="chart_of_accounts", on_delete="CASCADE")
    account_code = CharField(max_length=20)
    account_name = CharField(max_length=255)
    account_type = CharField(max_length=20)  # asset, liability, equity, income, expense
    parent_account = ForeignKeyField(
        "self", backref="children", null=True, on_delete="SET NULL"
    )
    is_active = BooleanField(default=True)

    class Meta:
        table_name = "chart_of_accounts"


