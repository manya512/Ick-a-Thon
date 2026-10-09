"""Zero-dependency local HTTP server and REST API for LowkeyToki.
Runs with standard Python library: python server.py
Serves index.html at http://localhost:8000 and connects with data/lowkeytoki.db (SQLite).
"""
import http.server
import json
import os
import sqlite3
import sys
import urllib.parse
from datetime import date, datetime, timedelta
from pathlib import Path

PORT = 8000
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "lowkeytoki.db"

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

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        # Check if table has rows
        row = conn.execute("SELECT COUNT(*) FROM products WHERE state = 'active'").fetchone()
        if row[0] == 0:
            seed_demo_data(conn)

def seed_demo_data(conn):
    today = date.today()
    demo_items = [
        ("Greek Yogurt Tub (500g)", "food", -2, 1, "Fridge", "Opened 4 days ago"),
        ("Organic Spinach Bag", "food", -1, 1, "Fridge", "Leaves wilting"),
        ("Oat Milk Barista Edition", "food", 0, 2, "Fridge", "Use for latte prep"),
        ("Almond Milk", "food", 1, 1, "Fridge", "Unsweetened"),
        ("Vitamin C Glow Serum", "cosmetics", 2, 1, "Bathroom cabinet", "15% active serum"),
        ("Avocado Hass Pack", "food", 3, 4, "Kitchen", "Ripe & ready"),
        ("SPF 50 Daily Sunscreen", "cosmetics", 3, 1, "Bathroom cabinet", "Broad spectrum"),
        ("Eye Drops Lubricant", "medicine", 4, 1, "Medicine box", "Sterile vials"),
        ("Sourdough Bread", "food", 6, 1, "Pantry", "Artisan loaf"),
        ("Pain Relief Ibuprofen", "medicine", 8, 1, "Medicine box", "200mg capsules"),
        ("Fresh Strawberries (400g)", "food", 4, 1, "Fridge", "Organic farm fresh"),
        ("Blueberries Organic", "food", 5, 2, "Fridge", "Snack bowl ready"),
        ("Cold Brew Concentrate", "food", 7, 1, "Fridge", "Nitro infused"),
        ("Tofu Extra Firm", "food", 10, 1, "Fridge", "Non-GMO"),
        ("Free Range Eggs 12pk", "food", 14, 1, "Fridge", "Grade A Large"),
        ("Cheddar Cheese Block", "food", 25, 1, "Fridge", "Sharp aged"),
        ("Hyaluronic Acid Hydrator", "cosmetics", 30, 1, "Bathroom cabinet", "2% + B5"),
        ("Salicylic Acid Cleanser", "cosmetics", 45, 1, "Bathroom cabinet", "Gentle exfoliating"),
        ("Retinol 0.5% Night Cream", "cosmetics", 90, 1, "Bathroom cabinet", "Store away from light"),
        ("Paracetamol 500mg", "medicine", 60, 2, "Medicine box", "Fever relief"),
        ("Antihistamine Allergy Tabs", "medicine", 120, 1, "Medicine box", "Non-drowsy"),
        ("Eco Dishwashing Liquid", "household", 120, 1, "Kitchen", "Plant-based citrus"),
        ("All-Purpose Counter Spray", "household", 180, 1, "Pantry", "Lavender scent"),
        ("Matcha Powder Ceremonial", "food", 180, 1, "Pantry", "First harvest Uji"),
    ]
    now = datetime.now().isoformat(timespec="seconds")
    for name, cat, offset, qty, loc, notes in demo_items:
        exp = (today + timedelta(days=offset)).isoformat()
        conn.execute(
            """INSERT INTO products (name, category, expiry_date, quantity, notes,
               storage_location, purchase_date, state, is_demo, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, NULL, 'active', 1, ?, ?)""",
            (name, cat, exp, qty, notes, loc, now, now)
        )
    conn.commit()

class LowkeyTokiHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(BASE_DIR / "index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        if parsed.path == "/api/products":
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("SELECT * FROM products WHERE state = 'active' ORDER BY expiry_date ASC, name ASC").fetchall()
                products = [
                    {
                        "id": r["id"],
                        "name": r["name"],
                        "category": r["category"],
                        "expiryDate": r["expiry_date"],
                        "quantity": r["quantity"],
                        "location": r["storage_location"],
                        "notes": r["notes"],
                        "purchaseDate": r["purchase_date"],
                        "isDemo": bool(r["is_demo"]),
                    }
                    for r in rows
                ]
            self._send_json(products)
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if parsed.path == "/api/products":
            now = datetime.now().isoformat(timespec="seconds")
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.execute(
                    """INSERT INTO products (name, category, expiry_date, quantity, notes,
                       storage_location, purchase_date, state, is_demo, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'active', 0, ?, ?)""",
                    (
                        payload.get("name", "Product"),
                        payload.get("category", "food"),
                        payload.get("expiryDate", date.today().isoformat()),
                        int(payload.get("quantity", 1)),
                        payload.get("notes", ""),
                        payload.get("location", ""),
                        payload.get("purchaseDate"),
                        now, now
                    )
                )
                pid = cur.lastrowid
                conn.commit()
            self._send_json({"ok": True, "id": pid})
            return

        if parsed.path == "/api/reset":
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("DELETE FROM products")
                seed_demo_data(conn)
            self._send_json({"ok": True, "message": "Reset to 24 demo products."})
            return

        if parsed.path.startswith("/api/products/") and parsed.path.endswith("/consume"):
            pid = int(parsed.path.split("/")[3])
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE products SET state = 'used' WHERE id = ?", (pid,))
                conn.commit()
            self._send_json({"ok": True})
            return

        self.send_error(404, "Not Found")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/products/"):
            pid = int(parsed.path.split("/")[3])
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE products SET state = 'tossed' WHERE id = ?", (pid,))
                conn.commit()
            self._send_json({"ok": True})
            return
        self.send_error(404, "Not Found")

    def _send_json(self, data, code=200):
        out = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(out)

if __name__ == "__main__":
    init_db()
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), LowkeyTokiHandler)
    print(f"LowkeyToki server running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()
