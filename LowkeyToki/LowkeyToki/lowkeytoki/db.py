"""SQLite persistence. Every query is parameterised."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterator, Optional

from .models import STATE_ACTIVE, Product

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "lowkeytoki.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL CHECK (length(trim(name)) > 0),
    category         TEXT    NOT NULL,
    expiry_date      TEXT    NOT NULL,
    quantity         INTEGER NOT NULL DEFAULT 1 CHECK (quantity >= 1),
    notes            TEXT    NOT NULL DEFAULT '',
    storage_location TEXT    NOT NULL DEFAULT '',
    purchase_date    TEXT,
    state            TEXT    NOT NULL DEFAULT 'active',
    is_demo          INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT    NOT NULL,
    updated_at       TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_products_state_expiry ON products (state, expiry_date);
"""
# expiry_date / purchase_date are ISO yyyy-mm-dd text; state is active | used | tossed.


def db_path() -> Path:
    """LOWKEYTOKI_DB overrides the location (used by tests)."""
    override = os.environ.get("LOWKEYTOKI_DB")
    return Path(override) if override else DEFAULT_DB


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _row_to_product(row: sqlite3.Row) -> Product:
    return Product(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        expiry_date=date.fromisoformat(row["expiry_date"]),
        quantity=row["quantity"],
        notes=row["notes"] or "",
        storage_location=row["storage_location"] or "",
        purchase_date=date.fromisoformat(row["purchase_date"]) if row["purchase_date"] else None,
        state=row["state"],
        is_demo=bool(row["is_demo"]),
    )


def _iso(d: Optional[date]) -> Optional[str]:
    return d.isoformat() if d else None


def add_product(data: dict, is_demo: bool = False) -> int:
    now = _now()
    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO products
               (name, category, expiry_date, quantity, notes, storage_location,
                purchase_date, state, is_demo, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)""",
            (
                data["name"], data["category"], _iso(data["expiry_date"]), data["quantity"],
                data.get("notes", ""), data.get("storage_location", ""),
                _iso(data.get("purchase_date")), int(is_demo), now, now,
            ),
        )
        return int(cur.lastrowid)


def update_product(product_id: int, data: dict) -> bool:
    with connect() as conn:
        cur = conn.execute(
            """UPDATE products SET name=?, category=?, expiry_date=?, quantity=?, notes=?,
               storage_location=?, purchase_date=?, updated_at=? WHERE id=?""",
            (
                data["name"], data["category"], _iso(data["expiry_date"]), data["quantity"],
                data.get("notes", ""), data.get("storage_location", ""),
                _iso(data.get("purchase_date")), _now(), product_id,
            ),
        )
        return cur.rowcount == 1


def delete_product(product_id: int) -> bool:
    with connect() as conn:
        cur = conn.execute("DELETE FROM products WHERE id=?", (product_id,))
        return cur.rowcount == 1


def set_state(product_id: int, state: str) -> bool:
    """Mark a product 'used' or 'tossed' (kept in the DB but hidden from active lists)."""
    if state not in ("active", "used", "tossed"):
        raise ValueError(f"Unknown state: {state}")
    with connect() as conn:
        cur = conn.execute(
            "UPDATE products SET state=?, updated_at=? WHERE id=?", (state, _now(), product_id)
        )
        return cur.rowcount == 1


def get_product(product_id: int) -> Optional[Product]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    return _row_to_product(row) if row else None


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_products(
    state: str = STATE_ACTIVE,
    search: str = "",
    category: Optional[str] = None,
) -> list[Product]:
    sql = "SELECT * FROM products WHERE state = ?"
    params: list = [state]
    search = (search or "").strip()
    if search:
        sql += " AND (name LIKE ? ESCAPE '\\' OR notes LIKE ? ESCAPE '\\')"
        like = f"%{_escape_like(search)}%"
        params += [like, like]
    if category and category != "all":
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY expiry_date ASC, name COLLATE NOCASE ASC"
    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_row_to_product(r) for r in rows]


def has_demo_data() -> bool:
    with connect() as conn:
        row = conn.execute("SELECT 1 FROM products WHERE is_demo = 1 LIMIT 1").fetchone()
    return row is not None


def clear_demo_data() -> int:
    with connect() as conn:
        cur = conn.execute("DELETE FROM products WHERE is_demo = 1")
        return cur.rowcount


# (name, category, days from today, quantity, location)
_DEMO = [
    ("Greek Yogurt Tub (500g)", "food", -2, 1, "Fridge"),
    ("Organic Spinach Bag", "food", -1, 1, "Fridge"),
    ("Oat Milk Barista Edition", "food", 0, 2, "Fridge"),
    ("Vitamin C Glow Serum", "cosmetics", 2, 1, "Bathroom cabinet"),
    ("Avocado Hass Pack", "food", 3, 4, "Kitchen"),
    ("Eye Drops Lubricant", "medicine", 5, 1, "Medicine box"),
    ("Sourdough Bread", "food", 6, 1, "Pantry"),
    ("Pain Relief Ibuprofen", "medicine", 21, 1, "Medicine box"),
    ("Salicylic Acid Cleanser", "cosmetics", 45, 1, "Bathroom cabinet"),
    ("Eco Dishwashing Liquid", "household", 120, 1, "Kitchen"),
    ("Matcha Powder Ceremonial", "food", 180, 1, "Pantry"),
]


def add_demo_data(today: Optional[date] = None) -> int:
    """Insert clearly-flagged demo rows with dates relative to today."""
    today = today or date.today()
    for name, cat, offset, qty, loc in _DEMO:
        add_product(
            {
                "name": name, "category": cat, "expiry_date": today + timedelta(days=offset),
                "quantity": qty, "notes": "", "storage_location": loc, "purchase_date": None,
            },
            is_demo=True,
        )
    return len(_DEMO)
