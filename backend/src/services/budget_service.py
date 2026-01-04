from __future__ import annotations

from decimal import Decimal

from ..models.budget import Budget
from ..models.transaction import Transaction
from ..models.user import User


def calculate_budget_status(budget: Budget, user: User) -> dict:
    """
    Compute basic budget status for the given budget.

    Spent: sum of expense transactions in the period for the budget's category.
    """
    q = (
        Transaction.select()
        .where(
            Transaction.user == user,
            Transaction.category == budget.category,
            Transaction.transaction_date >= budget.period_start,
            Transaction.transaction_date <= budget.period_end,
            Transaction.transaction_type == "expense",
        )
    )

    spent: Decimal = sum((t.amount for t in q), Decimal("0.00"))

    limit_amount = budget.amount
    remaining = limit_amount - spent
    percent_used = float(spent / limit_amount * 100) if limit_amount else 0.0
    over_limit = spent > limit_amount

    available_with_rollover = limit_amount
    if budget.rollover_enabled and budget.rollover_amount is not None:
        available_with_rollover += budget.rollover_amount

    return {
        "budget_id": str(budget.id),
        "category_id": str(budget.category.id),
        "period_start": budget.period_start,
        "period_end": budget.period_end,
        "limit": float(limit_amount),
        "spent": float(spent),
        "remaining": float(remaining),
        "percent_used": percent_used,
        "over_limit": over_limit,
        "available_with_rollover": float(available_with_rollover),
    }


