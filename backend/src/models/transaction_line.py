from __future__ import annotations

import uuid

from peewee import CharField, DecimalField, ForeignKeyField, UUIDField

from ..utils.database import BaseModel
from .chart_of_accounts import ChartOfAccount
from .transaction import Transaction


class TransactionLine(BaseModel):
    """
    Split/line item for a transaction mapped to a chart of accounts entry.

    A transaction can have zero or many lines; lines can be used for
    accounting and reporting without changing the core Transaction schema.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    transaction = ForeignKeyField(Transaction, backref="lines", on_delete="CASCADE")
    chart_of_account = ForeignKeyField(ChartOfAccount, backref="transaction_lines", on_delete="CASCADE")

    amount = DecimalField(max_digits=14, decimal_places=2)
    memo = CharField(max_length=500, null=True)

    class Meta:
        table_name = "transaction_lines"


