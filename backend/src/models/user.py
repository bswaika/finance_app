from __future__ import annotations

import uuid

from peewee import BooleanField, CharField, UUIDField

from ..utils.database import BaseModel


class User(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    username = CharField(unique=True, max_length=150)
    email = CharField(unique=True, max_length=255)
    hashed_password = CharField(max_length=255)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = "users"


