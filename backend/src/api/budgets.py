from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from peewee import DoesNotExist

from ..models.budget import Budget
from ..models.category import Category
from ..models.user import User
from ..schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from ..services.auth_service import get_current_active_user
from ..services.budget_service import calculate_budget_status


router = APIRouter()


@router.get("/", response_model=List[BudgetRead])
async def list_budgets(current_user: User = Depends(get_current_active_user)) -> List[BudgetRead]:
    qs = Budget.select().where(Budget.user == current_user)
    return [_budget_to_read(b) for b in qs]


@router.post("/", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_in: BudgetCreate,
    current_user: User = Depends(get_current_active_user),
) -> BudgetRead:
    try:
        category = Category.get(Category.id == budget_in.category_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category_id")

    budget = Budget.create(
        user=current_user,
        category=category,
        amount=budget_in.amount,
        period_type=budget_in.period_type,
        period_start=budget_in.period_start,
        period_end=budget_in.period_end,
        rollover_enabled=budget_in.rollover_enabled,
        rollover_amount=budget_in.rollover_amount,
        alert_threshold=budget_in.alert_threshold,
    )

    return _budget_to_read(budget)


@router.get("/{budget_id}", response_model=BudgetRead)
async def get_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> BudgetRead:
    try:
        budget = Budget.get(Budget.id == budget_id, Budget.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    return _budget_to_read(budget)


@router.put("/{budget_id}", response_model=BudgetRead)
async def update_budget(
    budget_id: UUID,
    budget_in: BudgetUpdate,
    current_user: User = Depends(get_current_active_user),
) -> BudgetRead:
    try:
        budget = Budget.get(Budget.id == budget_id, Budget.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    update_data = budget_in.dict(exclude_unset=True)

    if "category_id" in update_data:
        if update_data["category_id"] is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category_id cannot be null")
        try:
            category = Category.get(Category.id == update_data["category_id"])
        except DoesNotExist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category_id")
        budget.category = category
        update_data.pop("category_id")

    for field, value in update_data.items():
        setattr(budget, field, value)
    budget.save()

    return _budget_to_read(budget)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> None:
    try:
        budget = Budget.get(Budget.id == budget_id, Budget.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    budget.delete_instance()
    return None


@router.get("/{budget_id}/status")
async def get_budget_status(
    budget_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> dict:
    try:
        budget = Budget.get(Budget.id == budget_id, Budget.user == current_user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    return calculate_budget_status(budget, current_user)


def _budget_to_read(budget: Budget) -> BudgetRead:
    return BudgetRead(
        id=budget.id,
        category_id=budget.category.id,
        amount=float(budget.amount),
        period_type=budget.period_type,
        period_start=budget.period_start,
        period_end=budget.period_end,
        rollover_enabled=budget.rollover_enabled,
        rollover_amount=float(budget.rollover_amount) if budget.rollover_amount is not None else None,
        alert_threshold=float(budget.alert_threshold) if budget.alert_threshold is not None else None,
    )


