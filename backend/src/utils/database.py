from __future__ import annotations

from peewee import Model
from playhouse.db_url import connect

from ..config import settings

# Single shared Peewee database instance, configured from DATABASE_URL
db = connect(settings.database_url)


class BaseModel(Model):
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
    from ..models.category import Category
    from ..models.transaction import Transaction
    from ..models.budget import Budget
    from ..models.chart_of_accounts import ChartOfAccount
    from ..models.family import Family
    from ..models.bank_integration import BankIntegration

    db.create_tables(
        [
            User,
            Family,
            Account,
            Category,
            ChartOfAccount,
            Transaction,
            Budget,
            BankIntegration,
        ]
    )


