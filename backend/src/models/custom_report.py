from __future__ import annotations

import uuid

from peewee import CharField, ForeignKeyField, TextField, UUIDField

from ..utils.database import BaseModel
from .user import User


class CustomReport(BaseModel):
    """
    Saved custom report definition for a user.

    Stores a name/description and a read-only SQL query that can be executed
    via the custom SQL report endpoint.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKeyField(User, backref="custom_reports", on_delete="CASCADE")

    name = CharField(max_length=255)
    description = CharField(max_length=500, null=True)
    sql_query = TextField()

    class Meta:
        table_name = "custom_reports"


