# LowkeyToki 🦠

LowkeyToki is a friendly smart expiry tracker for food, medicine, cosmetics, household supplies, and anything else with a date to watch. It turns expiry dates into a simple daily workflow: see what needs attention, use items before they go bad, and keep the rest of your inventory organised.

Built for the 3-hour **Ick-a-thon** with a zero-dependency Python server, a responsive single-page UI, and SQLite persistence.

## Run locally

Requirements: Python 3.9+ and a modern browser. No package installation is required.

```powershell
python server.py
```

Then open <http://localhost:8000/>.

The server serves [index.html](./index.html), creates `data/lowkeytoki.db` automatically, and exposes the small REST API used by the UI. Stop it with `Ctrl+C`.

## What you can do

- View an overview dashboard with total inventory, expiring-soon items, the Ick Zone, and fresh items.
- See the Shelf Health Pulse to understand the current mix of expired, urgent, and fresh products.
- Search products or categories from the overview.
- Add products with a name, category, expiry date, quantity, notes, storage location, and purchase date.
- Use quick expiry presets for 3 days, 1 week, 1 month, or 6 months.
- Scan a barcode or choose a sample barcode result to prefill product details.
- Browse the **Use First** page, grouped into expired, expiring soon, and upcoming items.
- Mark products as **Used** or **Tossed** so they leave the active inventory without being deleted from storage.
- Browse the Products page with search, category filters, status filters, and sorting.
- Browse category summaries and jump directly into a category.
- Reset the app to its 24-item demo inventory from the footer.

## Expiry status

Status is calculated from the number of days until the expiry date:

| Days remaining | Status | UI meaning |
| --- | --- | --- |
| Less than 0 | Expired | The Ick Zone |
| 0–3 | Expiring soon | Needs attention |
| More than 3 | Fresh | Safe for now |

An item expiring today is still **Expiring soon**, not expired.

## Data and API

Active products are stored in `data/lowkeytoki.db` in the `products` table. The database is created and seeded with demo data when the server starts with an empty active inventory.

The local API currently supports:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/products` | Return active products ordered by expiry date |
| `POST` | `/api/products` | Add a product |
| `POST` | `/api/products/{id}/consume` | Mark a product as used |
| `DELETE` | `/api/products/{id}` | Mark a product as tossed |
| `POST` | `/api/reset` | Replace the inventory with the 24 demo products |

Used and tossed products remain in the database with their state recorded, but the current UI only shows active products.

## Project layout

```text
index.html          Single-page browser UI, styles, views, and client-side behaviour
server.py           Zero-dependency HTTP server and SQLite REST API
data/
  lowkeytoki.db     Local runtime database (created automatically; ignored by Git)
LowkeyToki/         Earlier Streamlit prototype and supporting tests
```

## Current limitations

- The expiry-date scanner is a camera-style demo flow; it applies sample dates rather than performing production OCR.
- Barcode lookup is represented by the in-app scanner/sample results; it does not require an external service.
- The notification bell is a UI surface only. There are no push, email, or scheduled reminders.
- Product photos and thumbnails are not implemented.
- There is no history page for used or tossed products yet.
- Categories are fixed to Food, Medicine, Cosmetics, and Household.
- The app is designed for local use and does not include authentication, multi-user sync, or cloud storage.

## Design

LowkeyToki uses a soft cream, matcha, lilac, and charcoal palette with rounded cards and playful status language. The interface is optimised for a compact, mobile-friendly layout with bottom navigation for Overview, Use First, Add Product, Products, and Categories.

The page loads Google Fonts when internet access is available and falls back to system fonts offline.
