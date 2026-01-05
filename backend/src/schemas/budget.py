from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel


class BudgetBase(BaseModel):
    category_id: UUID
    amount: float
    period_type: str  # monthly, quarterly, yearly
    period_start: date
    period_end: date
    rollover_enabled: bool = False
    rollover_amount: float | None = None
    alert_threshold: float | None = None


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    category_id: UUID | None = None
    amount: float | None = None
    period_type: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    rollover_enabled: bool | None = None
    rollover_amount: float | None = None
    alert_threshold: float | None = None


class BudgetRead(BudgetBase):
    id: UUID


