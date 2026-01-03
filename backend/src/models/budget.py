from __future__ import annotations

import uuid

from peewee import BooleanField, CharField, DateField, DecimalField, ForeignKeyField, UUIDField

from ..utils.database import BaseModel
from .category import Category
from .user import User


class Budget(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKeyField(User, backref="budgets", on_delete="CASCADE")
    category = ForeignKeyField(Category, backref="budgets", on_delete="CASCADE")
    amount = DecimalField(max_digits=14, decimal_places=2)
    period_type = CharField(max_length=20)  # monthly, quarterly, yearly
    period_start = DateField()
    period_end = DateField()
    rollover_enabled = BooleanField(default=False)
    rollover_amount = DecimalField(max_digits=14, decimal_places=2, null=True)
    alert_threshold = DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        table_name = "budgets"


