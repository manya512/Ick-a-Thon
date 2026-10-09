"""Domain model + expiry status logic (no Streamlit or SQLite in here)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

# Products with 0..SOON_DAYS days left count as "expiring soon" (Stitch: "next 72 hours").
SOON_DAYS = 3
# "Use First" shows non-expired items up to this many days ahead in its Upcoming section.
UPCOMING_DAYS = 30

STATUS_EXPIRED = "expired"      # shown as "The Ick Zone"
STATUS_SOON = "soon"            # expiring today .. SOON_DAYS
STATUS_FRESH = "fresh"

STATE_ACTIVE = "active"
STATE_USED = "used"
STATE_TOSSED = "tossed"

# key -> (label, emoji, material icon name)
CATEGORIES: dict[str, tuple[str, str, str]] = {
    "food": ("Food & Groceries", "🥗", "nutrition"),
    "medicine": ("Medicine", "💊", "medication"),
    "cosmetics": ("Cosmetics & Skincare", "✨", "sanitizer"),
    "household": ("Household", "🧼", "soap"),
    "other": ("Other", "📦", "inventory_2"),
}

LOCATIONS = ["Fridge", "Pantry", "Bathroom cabinet", "Medicine box", "Kitchen", "Other"]


def category_label(key: str) -> str:
    return CATEGORIES.get(key, CATEGORIES["other"])[0]


def category_emoji(key: str) -> str:
    return CATEGORIES.get(key, CATEGORIES["other"])[1]


@dataclass
class Product:
    id: int
    name: str
    category: str
    expiry_date: date
    quantity: int = 1
    notes: str = ""
    storage_location: str = ""
    purchase_date: Optional[date] = None
    state: str = STATE_ACTIVE
    is_demo: bool = False

    def days_left(self, today: Optional[date] = None) -> int:
        return days_until(self.expiry_date, today)

    def status(self, today: Optional[date] = None) -> str:
        return status_for_days(self.days_left(today))


def days_until(expiry: date, today: Optional[date] = None) -> int:
    """Whole calendar days from today to expiry. 0 = expires today, negative = expired."""
    today = today or date.today()
    return (expiry - today).days


def status_for_days(days_left: int) -> str:
    """Expired only when the expiry date is strictly before today; today is still usable."""
    if days_left < 0:
        return STATUS_EXPIRED
    if days_left <= SOON_DAYS:
        return STATUS_SOON
    return STATUS_FRESH


def describe_days(days_left: int) -> str:
    if days_left < -1:
        return f"Expired {-days_left} days ago"
    if days_left == -1:
        return "Expired yesterday"
    if days_left == 0:
        return "Expires today"
    if days_left == 1:
        return "Expires tomorrow"
    if days_left < 60:
        return f"Expires in {days_left} days"
    return f"Expires in {round(days_left / 30)} months"


def short_badge(days_left: int) -> str:
    if days_left < -1:
        return f"{-days_left} days over"
    if days_left == -1:
        return "1 day over"
    if days_left == 0:
        return "Today!"
    if days_left == 1:
        return "1 day left"
    if days_left < 60:
        return f"{days_left} days left"
    return f"{round(days_left / 30)} mo left"


def sort_nearest_expiry(products: list[Product]) -> list[Product]:
    """Nearest (or most overdue) expiry first; name breaks ties."""
    return sorted(products, key=lambda p: (p.expiry_date, p.name.lower()))


def compute_stats(products: list[Product], today: Optional[date] = None) -> dict[str, int]:
    stats = {"total": 0, STATUS_EXPIRED: 0, STATUS_SOON: 0, STATUS_FRESH: 0}
    for p in products:
        stats["total"] += 1
        stats[p.status(today)] += 1
    return stats
