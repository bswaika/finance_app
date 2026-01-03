from __future__ import annotations

import uuid

from peewee import CharField, DateTimeField, IntegerField, TextField, UUIDField, ForeignKeyField

from ..utils.database import BaseModel
from .user import User


class TransactionImport(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKeyField(User, backref="transaction_imports", on_delete="CASCADE")
    filename = CharField(max_length=255)
    import_date = DateTimeField()
    status = CharField(max_length=20)  # pending, completed, failed
    records_imported = IntegerField(default=0)
    errors = TextField(null=True)  # JSON string of errors
    bank_format = CharField(max_length=100, null=True)

    class Meta:
        table_name = "transaction_imports"


