from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .utils.database import db
from .api import (
    auth,
    accounts,
    transactions,
    categories,
    budgets,
    reports,
    recurring_transactions,
    chart_of_accounts,
    custom_reports,
)


app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    if db.is_closed():
        db.connect(reuse_if_open=True)


@app.on_event("shutdown")
def on_shutdown() -> None:
    if not db.is_closed():
        db.close()


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"])
app.include_router(recurring_transactions.router, prefix="/api/recurring-transactions", tags=["recurring-transactions"])
app.include_router(chart_of_accounts.router, prefix="/api/chart-of-accounts", tags=["chart-of-accounts"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(custom_reports.router, prefix="/api/custom-reports", tags=["custom-reports"])


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}


