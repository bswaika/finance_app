from __future__ import annotations

import uuid

from peewee import BooleanField, CharField, ForeignKeyField, UUIDField

from ..utils.database import BaseModel
from .user import User


class Category(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKeyField(
        User, backref="categories", null=True, on_delete="SET NULL"
    )  # null => system category
    name = CharField(max_length=255)
    parent_category = ForeignKeyField(
        "self", backref="subcategories", null=True, on_delete="SET NULL"
    )
    category_type = CharField(max_length=20)  # income, expense, both
    is_system = BooleanField(default=False)

    class Meta:
        table_name = "categories"


