from __future__ import annotations

from datetime import datetime

from peewee import DateTimeField, Model
from playhouse.db_url import connect

from ..config import settings

# Single shared Peewee database instance, configured from DATABASE_URL
db = connect(settings.database_url)


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    class Meta:
        database = db


def init_db() -> None:
    """
    Initialize database tables by creating them directly from models.

    This helper is intended only for ad-hoc local testing or experimentation.
    The recommended approach for both development and production is to use a
    migration-based workflow (e.g. scripts that apply changes incrementally to
    the Render Postgres database), not `create_tables` on startup.
    """

    from ..models.user import User
    from ..models.account import Account
    from ..models.bank_account import BankAccount
    from ..models.category import Category
    from ..models.transaction import Transaction
    from ..models.transaction_line import TransactionLine
    from ..models.recurring_transaction import RecurringTransaction
    from ..models.budget import Budget
    from ..models.chart_of_accounts import ChartOfAccount
    from ..models.transaction_import import TransactionImport
    from ..models.custom_report import CustomReport

    db.create_tables(
        [
            User,
            Account,
            BankAccount,
            Category,
            ChartOfAccount,
            Transaction,
            TransactionLine,
            Budget,
            RecurringTransaction,
            TransactionImport,
            CustomReport,
        ]
    )


