from __future__ import annotations

import csv
from io import StringIO
from typing import Dict, Iterable, List


def parse_transactions_csv(csv_text: str, bank_format: str | None = None) -> List[Dict]:
    """
    Parse a CSV of bank transactions into a list of dicts with
    normalized keys: date, amount, description.

    This is intentionally simple for now; bank_format can be used later to
    apply bank-specific mappings. For the MVP, we try to auto-detect common
    column names.
    """
    reader = csv.DictReader(StringIO(csv_text))
    rows: List[Dict] = []

    for row in reader:
        # Try to find likely column names
        lower = {k.lower(): v for k, v in row.items()}

        date_val = (
            lower.get("date")
            or lower.get("transaction date")
            or lower.get("posted date")
        )
        amount_val = (
            lower.get("amount")
            or lower.get("transaction amount")
            or lower.get("amt")
        )
        desc_val = (
            lower.get("description")
            or lower.get("memo")
            or lower.get("details")
            or lower.get("transaction description")
        )

        if date_val is None or amount_val is None:
            # Skip rows we cannot interpret
            continue

        rows.append(
            {
                "date": date_val,
                "amount": amount_val,
                "description": desc_val or "",
                "raw": row,
            }
        )

    return rows


