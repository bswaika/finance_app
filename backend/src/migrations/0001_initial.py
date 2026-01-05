"""
Initial database migration: create core tables.

This script is intended to be run manually, for example:

    cd backend
    DATABASE_URL=postgresql://... python -m src.migrations.0001_initial

It will connect using the configured DATABASE_URL and create the core tables
if they do not already exist.
"""

from src.utils.database import db
from src.models import (
    User,
    Account,
    BankAccount,
    Category,
    Transaction,
    TransactionLine,
    RecurringTransaction,
    Budget,
    ChartOfAccount,
    TransactionImport,
    CustomReport,
)


def run() -> None:
    with db:
        db.create_tables(
            [
                User,
                Account,
                BankAccount,
                Category,
                ChartOfAccount,
                Transaction,
                TransactionLine,
                RecurringTransaction,
                Budget,
                TransactionImport,
                CustomReport,
            ]
        )


if __name__ == "__main__":
    run()


