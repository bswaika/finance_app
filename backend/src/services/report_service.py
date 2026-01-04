from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from peewee import fn

from ..models.account import Account
from ..models.budget import Budget
from ..models.category import Category
from ..models.recurring_transaction import RecurringTransaction
from ..models.transaction import Transaction
from ..models.user import User
from ..utils.database import db
from .budget_service import calculate_budget_status


def income_expense_summary(
    user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, float]:
    """
    Aggregate total income and expenses over an optional date range.

    Uses explicit transaction_type flags to classify rows.
    Transfers are ignored.
    """
    q = Transaction.select().where(Transaction.user == user)

    if start_date is not None:
        q = q.where(Transaction.transaction_date >= start_date)
    if end_date is not None:
        q = q.where(Transaction.transaction_date <= end_date)

    income_q = q.where(Transaction.transaction_type == "income")
    expense_q = q.where(Transaction.transaction_type == "expense")

    income = income_q.aggregate(fn.SUM(Transaction.amount)) or Decimal("0.0")
    expenses = expense_q.aggregate(fn.SUM(Transaction.amount)) or Decimal("0.0")

    return {
        "income": float(income),
        "expenses": float(expenses),
        "net": float(income + expenses),
    }


def category_breakdown(
    user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Dict]:
    """
    Sum expenses by category over an optional date range.
    """
    q = (
        Transaction.select(
            Transaction.category,
            fn.SUM(Transaction.amount).alias("total"),
        )
        .join(Category, on=(Transaction.category == Category.id))
        .where(
            Transaction.user == user,
            Transaction.transaction_type == "expense",
        )
        .group_by(Transaction.category)
    )

    if start_date is not None:
        q = q.where(Transaction.transaction_date >= start_date)
    if end_date is not None:
        q = q.where(Transaction.transaction_date <= end_date)

    results: List[Dict] = []
    for row in q:
        cat = row.category
        total = getattr(row, "total", Decimal("0.0"))
        results.append(
            {
                "category_id": str(cat.id),
                "category_name": cat.name,
                "amount": float(total),
            }
        )

    return results


def account_balances(user: User) -> List[Dict]:
    """
    Return current balances for all of the user's accounts.

    Note: this uses the stored Account.balance field, not a recomputed
    sum of transactions.
    """
    qs = Account.select().where(Account.user == user)

    return [
        {
            "account_id": str(a.id),
            "name": a.name,
            "account_type": a.account_type,
            "balance": float(a.balance),
            "currency": a.currency,
            "is_active": a.is_active,
        }
        for a in qs
    ]


def all_budgets_status(user: User) -> List[Dict]:
    """
    Compute status for all budgets belonging to the user.
    """
    qs = Budget.select().where(Budget.user == user)
    return [calculate_budget_status(b, user) for b in qs]


def budget_vs_expense_report(
    user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Dict]:
    """
    Compare budget limits vs actual expenses per budget.

    Uses budget periods by default, but optional start/end can further restrict
    the window for the expense side.
    """
    results: List[Dict] = []
    qs = Budget.select().where(Budget.user == user)

    for budget in qs:
        status = calculate_budget_status(budget, user)

        # Optionally override the spent/remaining with a narrower window
        if start_date is not None or end_date is not None:
            b_start = max(start_date or budget.period_start, budget.period_start)
            b_end = min(end_date or budget.period_end, budget.period_end)

            q = (
                Transaction.select()
                .where(
                    Transaction.user == user,
                    Transaction.category == budget.category,
                    Transaction.transaction_date >= b_start,
                    Transaction.transaction_date <= b_end,
                    Transaction.transaction_type == "expense",
                )
            )
            spent = sum((t.amount for t in q), Decimal("0.0"))
            limit_amount = budget.amount
            remaining = limit_amount - spent
            percent_used = float(spent / limit_amount * 100) if limit_amount else 0.0

            status["spent"] = float(spent)
            status["remaining"] = float(remaining)
            status["percent_used"] = percent_used

        results.append(status)

    return results


def expense_breakdown_by_account(
    user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Dict]:
    """
    Sum expenses by account over an optional date range.
    """
    q = (
        Transaction.select(
            Transaction.account,
            fn.SUM(Transaction.amount).alias("total"),
        )
        .join(Account, on=(Transaction.account == Account.id))
        .where(
            Transaction.user == user,
            Transaction.transaction_type == "expense",
        )
        .group_by(Transaction.account)
    )

    if start_date is not None:
        q = q.where(Transaction.transaction_date >= start_date)
    if end_date is not None:
        q = q.where(Transaction.transaction_date <= end_date)

    results: List[Dict] = []
    for row in q:
        acc = row.account
        total = getattr(row, "total", Decimal("0.0"))
        results.append(
            {
                "account_id": str(acc.id),
                "account_name": acc.name,
                "account_type": acc.account_type,
                "amount": float(total),
                "currency": acc.currency,
            }
        )

    return results


def recurring_transactions_report(user: User) -> List[Dict]:
    """
    Summary of recurring transactions (subscriptions-like view).
    """
    qs = RecurringTransaction.select().where(RecurringTransaction.user == user)
    results: List[Dict] = []
    for rt in qs:
        results.append(
            {
                "id": str(rt.id),
                "account_id": str(rt.account.id),
                "category_id": str(rt.category.id) if rt.category is not None else None,
                "amount": float(rt.amount),
                "description": rt.description,
                "frequency": rt.frequency,
                "interval": int(rt.interval or 1),
                "next_occurrence": rt.next_occurrence,
                "is_active": rt.is_active,
            }
        )
    return results


def run_custom_sql(query: str) -> Dict[str, List[Dict]]:
    """
    Run a read-only custom SQL query and return rows as a list of dicts.

    For safety, we enforce that the query starts with SELECT and contains
    no obvious write keywords.
    """
    q = query.strip().rstrip(";")
    lower = q.lower()
    if not lower.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")
    forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "truncate "]
    if any(word in lower for word in forbidden):
        raise ValueError("Only read-only SELECT queries are allowed")

    cursor = db.execute_sql(q)
    columns = [col[0] for col in cursor.description] if cursor.description else []
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return {"columns": columns, "rows": rows}



