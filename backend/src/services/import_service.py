from __future__ import annotations

import base64
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple

from dateutil.parser import parse as parse_date

from .integrations.csv_parser import parse_transactions_csv
from ..models.account import Account
from ..models.category import Category
from ..models.transaction import Transaction
from ..models.transaction_import import TransactionImport
from ..models.user import User


def _parse_amount(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).replace(",", "").strip()
    return float(s)


def import_transactions_from_json(
    user: User,
    payload: Dict[str, Any],
) -> TransactionImport:
    """
    Import transactions from a JSON payload.

    Payload supports two modes:
      1) \"transactions\": [ { account_id, amount, date, description, ... }, ... ]
      2) \"csv_base64\": \"...\", optionally with \"bank_format\": \"chase\" etc.
    """
    filename = payload.get("filename") or "api-import"
    bank_format = payload.get("bank_format")

    ti = TransactionImport.create(
        user=user,
        filename=filename,
        import_date=datetime.utcnow(),
        status="pending",
        records_imported=0,
        errors=None,
        bank_format=bank_format,
    )

    errors: List[str] = []
    created_count = 0

    try:
        if "transactions" in payload:
            created_count, errors = _import_structured_transactions(user, payload["transactions"])
        elif "csv_base64" in payload:
            created_count, errors = _import_csv_base64(user, payload["csv_base64"], bank_format)
        else:
            errors.append("No transactions or csv_base64 field in payload")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Unhandled import error: {exc!r}")

    ti.records_imported = created_count
    if errors:
        import json

        ti.status = "failed" if created_count == 0 else "completed_with_errors"
        ti.errors = json.dumps(errors)
    else:
        ti.status = "completed"
    ti.save()

    return ti


def _import_structured_transactions(
    user: User,
    txs: Iterable[Dict[str, Any]],
) -> Tuple[int, List[str]]:
    errors: List[str] = []
    created = 0

    for idx, tx in enumerate(txs):
        try:
            account = Account.get(Account.id == tx["account_id"], Account.user == user)
        except Exception:  # noqa: BLE001
            errors.append(f"[{idx}] invalid account_id")
            continue

        category = None
        if tx.get("category_id"):
            try:
                category = Category.get(Category.id == tx["category_id"])
            except Exception:  # noqa: BLE001
                errors.append(f"[{idx}] invalid category_id")
                continue

        try:
            amount = _parse_amount(tx["amount"])
            tx_date = (
                tx["transaction_date"]
                if isinstance(tx["transaction_date"], datetime)
                else parse_date(str(tx["transaction_date"])).date()
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"[{idx}] invalid amount/date: {exc!r}")
            continue

        Transaction.create(
            user=user,
            account=account,
            category=category,
            amount=amount,
            description=tx.get("description") or "",
            transaction_date=tx_date,
            transaction_type=tx.get("transaction_type") or "expense",
            transfer_to_account=None,
            is_recurring=False,
            recurring_template_id=None,
        )
        created += 1

    return created, errors


def _import_csv_base64(
    user: User,
    csv_b64: str,
    bank_format: str | None = None,
) -> Tuple[int, List[str]]:
    errors: List[str] = []
    created = 0

    try:
        decoded = base64.b64decode(csv_b64).decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Could not decode csv_base64: {exc!r}")
        return 0, errors

    rows = parse_transactions_csv(decoded, bank_format=bank_format)

    # For now, require an account_id in the payload; multi-account CSVs can be
    # split by the client.
    default_account_id = payload_account_id = None  # type: ignore[assignment]
    # This is intentionally simple for now; the API endpoint will pass in an
    # account_id when using csv mode.

    # In this MVP implementation we skip automatic CSV -> account/category
    # mapping and instead only store basic transaction details.
    for idx, row in enumerate(rows):
        try:
            amount = _parse_amount(row["amount"])
            tx_date = parse_date(str(row["date"])).date()
        except Exception as exc:  # noqa: BLE001
            errors.append(f"[{idx}] invalid amount/date: {exc!r}")
            continue

        # Caller must provide account_id via payload; we will override this
        # later from the API endpoint where we know the account.
        if default_account_id is None:
            errors.append("[global] No account_id provided for CSV import")
            break

    # For now we don't create rows here; the API endpoint will handle a more
    # guided CSV import where it passes account/category explicitly.
    return created, errors


