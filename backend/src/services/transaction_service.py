from __future__ import annotations

from datetime import date
from typing import Iterable, List

from dateutil.relativedelta import relativedelta

from ..models.account import Account
from ..models.recurring_transaction import RecurringTransaction
from ..models.transaction import Transaction
from ..models.user import User


def _advance_next_occurrence(rt: RecurringTransaction) -> None:
    """Advance next_occurrence based on frequency and interval."""
    interval = int(rt.interval or 1)
    if rt.frequency == "daily":
        rt.next_occurrence = rt.next_occurrence + relativedelta(days=interval)
    elif rt.frequency == "weekly":
        rt.next_occurrence = rt.next_occurrence + relativedelta(weeks=interval)
    elif rt.frequency == "monthly":
        rt.next_occurrence = rt.next_occurrence + relativedelta(months=interval)
    elif rt.frequency == "yearly":
        rt.next_occurrence = rt.next_occurrence + relativedelta(years=interval)
    else:
        # Fallback: treat as monthly
        rt.next_occurrence = rt.next_occurrence + relativedelta(months=interval)


def generate_due_recurring_transactions(
    user: User,
    today: date | None = None,
) -> List[Transaction]:
    """
    Generate Transaction rows for all of the user's recurring transactions
    that are due on or before `today`.
    """
    if today is None:
        today = date.today()

    q = (
        RecurringTransaction.select()
        .where(
            RecurringTransaction.user == user,
            RecurringTransaction.is_active == True,  # type: ignore  # noqa: E712
            RecurringTransaction.next_occurrence <= today,
        )
    )

    created: List[Transaction] = []
    for rt in q:
        # Check end_date if present
        if rt.end_date and rt.next_occurrence > rt.end_date:
            rt.is_active = False
            rt.save()
            continue

        account = Account.get(Account.id == rt.account_id)

        tx = Transaction.create(
            user=user,
            account=account,
            category=rt.category,
            amount=rt.amount,
            description=rt.description,
            transaction_date=rt.next_occurrence,
            transaction_type="expense",  # by default; can be refined
            transfer_to_account=None,
            is_recurring=True,
            recurring_template_id=rt.id,
        )
        created.append(tx)

        _advance_next_occurrence(rt)
        rt.save()

    return created


def generate_for_recurring_transaction(rt: RecurringTransaction) -> Transaction | None:
    """
    Generate a single occurrence for the given recurring transaction
    (used by the manual /generate endpoint).
    """
    if not rt.is_active:
        return None

    today = date.today()
    if rt.next_occurrence > today:
        # Not yet due, but we still allow manual generation
        pass

    account = Account.get(Account.id == rt.account_id)

    tx = Transaction.create(
        user=rt.user,
        account=account,
        category=rt.category,
        amount=rt.amount,
        description=rt.description,
        transaction_date=rt.next_occurrence,
        transaction_type="expense",
        transfer_to_account=None,
        is_recurring=True,
        recurring_template_id=rt.id,
    )

    _advance_next_occurrence(rt)
    rt.save()

    return tx


