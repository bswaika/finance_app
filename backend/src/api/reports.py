from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..models.user import User
from ..services.auth_service import get_current_active_user
from ..services.report_service import (
    account_balances,
    all_budgets_status,
    budget_vs_expense_report,
    category_breakdown,
    expense_breakdown_by_account,
    income_expense_summary,
    recurring_transactions_report,
    run_custom_sql,
)


router = APIRouter()


@router.get("/income-expense")
async def get_income_expense_report(
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> dict:
    return income_expense_summary(current_user, start_date=start_date, end_date=end_date)


@router.get("/category-breakdown")
async def get_category_breakdown_report(
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> dict:
    data = category_breakdown(current_user, start_date=start_date, end_date=end_date)
    return {"categories": data}


@router.get("/account-balances")
async def get_account_balances_report(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    return {"accounts": account_balances(current_user)}


@router.get("/budget-status")
async def get_budget_status_report(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    return {"budgets": all_budgets_status(current_user)}


@router.get("/budget-vs-expense")
async def get_budget_vs_expense_report(
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> dict:
    return {"budgets": budget_vs_expense_report(current_user, start_date=start_date, end_date=end_date)}


@router.get("/expense-by-account")
async def get_expense_by_account_report(
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> dict:
    return {
        "accounts": expense_breakdown_by_account(
            current_user,
            start_date=start_date,
            end_date=end_date,
        )
    }


@router.get("/recurring-transactions")
async def get_recurring_transactions_report(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    return {"recurring_transactions": recurring_transactions_report(current_user)}


@router.post("/custom-sql")
async def run_custom_sql_report(
    payload: dict,
    _: User = Depends(get_current_active_user),
) -> dict:
    """
    Run a read-only custom SELECT query.

    Payload:
      { "query": "SELECT ... " }
    """
    query = payload.get("query")
    if not query or not isinstance(query, str):
        raise HTTPException(status_code=400, detail="Missing or invalid 'query' field")

    try:
        return run_custom_sql(query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


