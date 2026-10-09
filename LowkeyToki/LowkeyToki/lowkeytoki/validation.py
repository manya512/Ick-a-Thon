"""Input validation for product forms. Returns clean values plus readable messages."""
from __future__ import annotations

from datetime import date
from typing import Optional

from .models import CATEGORIES

MAX_NAME = 80
MAX_NOTES = 500
MAX_QTY = 999
MIN_DATE = date(2000, 1, 1)
MAX_DATE = date(2100, 12, 31)


def validate_product(
    name: str,
    category: str,
    expiry_date: Optional[date],
    quantity,
    notes: str = "",
    storage_location: str = "",
    purchase_date: Optional[date] = None,
    today: Optional[date] = None,
) -> tuple[dict, list[str], list[str]]:
    """Return (clean_data, errors, warnings). Save only when errors is empty."""
    today = today or date.today()
    errors: list[str] = []
    warnings: list[str] = []

    name = (name or "").strip()
    if not name:
        errors.append("Give the product a name.")
    elif len(name) > MAX_NAME:
        errors.append(f"Keep the name under {MAX_NAME} characters.")

    if category not in CATEGORIES:
        errors.append("Pick a category.")

    if expiry_date is None:
        errors.append("Pick an expiry date.")
    elif not (MIN_DATE <= expiry_date <= MAX_DATE):
        errors.append("That expiry date looks off. Use a date between 2000 and 2100.")
    elif expiry_date < today:
        warnings.append("This expiry date is already in the past, so it will land in the Ick Zone.")

    try:
        qty = int(quantity)
    except (TypeError, ValueError):
        qty = 0
        errors.append("Quantity must be a whole number.")
    else:
        if qty < 1 or qty > MAX_QTY:
            errors.append(f"Quantity must be between 1 and {MAX_QTY}.")

    notes = (notes or "").strip()
    if len(notes) > MAX_NOTES:
        errors.append(f"Keep notes under {MAX_NOTES} characters.")

    if purchase_date is not None and expiry_date is not None and purchase_date > expiry_date:
        errors.append("The purchase date can't be after the expiry date.")

    clean = {
        "name": name,
        "category": category,
        "expiry_date": expiry_date,
        "quantity": qty,
        "notes": notes,
        "storage_location": (storage_location or "").strip(),
        "purchase_date": purchase_date,
    }
    return clean, errors, warnings
