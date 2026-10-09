# LowkeyToki 🦠

A cute, slightly icky expiry tracker. Built for the 3-hour **Ick-a-thon** with Python, Streamlit and SQLite.
It tracks food, medicine, cosmetics/skincare, household products and anything else with an expiry date.

The UI follows the exported Google Stitch screens (Overview, Use First, Add Item, Products), plus a Categories page.
Fonts: Quicksand (brand and headings) and DM Sans (everything else). Palette: cream, matcha, lilac, charcoal.

## Run the App

### Option 1: Pixel-Perfect Google Stitch UI (Instant, 0 dependencies!)

Runs immediately with Python's standard library:

```powershell
python server.py
```
Open **http://localhost:8000** in your browser!

You can also simply double-click or open `index.html` directly in any web browser.

### Option 2: Streamlit App

```powershell
pip install -r requirements.txt
streamlit run app.py
```
Open **http://localhost:8501**.

Run the tests (optional):

```powershell
pip install pytest
python -m pytest -q
```

## Data

- Stored in `data/lowkeytoki.db` (SQLite, created automatically on first run, git-ignored).
- To start fresh, stop the app and delete that file.
- No API keys, accounts or paid services are used.
- On the Overview page, **Demo data** can load fake sample products (each flagged `DEMO`) and remove them again.

## Expiry rules (`lowkeytoki/models.py`)

| Days left | Status |
|---|---|
| less than 0 | Expired, shown as **The Ick Zone** |
| 0 to 3 (today included) | **Expiring soon** |
| more than 3 | **Fresh** |

An item that expires **today** is *not* expired yet; it counts as expiring soon.
Change `SOON_DAYS` in `models.py` to adjust the window.

## Completed features

- Add, edit (dialog) and delete (with confirmation) products
- Name, category, expiry date, quantity, optional notes, storage location and purchase date
- Barcode scanning on Add Product (camera or manual entry via `zxing-cpp` and Open Food Facts / Beauty / Products lookup) to prefill name and category; expiry date is never auto-filled
- Automatic expiry status, with correct handling of items expiring today
- Overview dashboard: stat cards, Shelf Health Pulse bar, top three Use First items
- Use First page: Ick Zone, Expiring soon and Upcoming sections, sorted by nearest expiry
- "Used" and "Toss" actions (hide an item from active lists without deleting it)
- Products page: search (name and notes), category filter, status filter, sorting
- Categories page with per-category counts and a Browse shortcut
- Validation messages, a past-date warning, and empty states on every page
- Quick expiry presets (+3 days, +1 week, +1 month, +6 months)
- Parameterised SQL everywhere, HTML-escaped user text
- Automated tests for logic, database, barcode decoding/lookup, and page rendering (`tests/`)

## Not built yet

- **Expiry-date scanning (OCR):** the Stitch "Scan" card is shown as *Coming soon* and does nothing. Barcode scanning fills product details only; expiry-date OCR is still not built. Manual entry is the way to add dates.
- **Reminders / push notifications:** not implemented. The notification bell and "remind me 3 days before" text from the Stitch design were left out or marked as not built.
- Product photo upload and photo thumbnails: not implemented.
- **History view** for used/tossed items (they are stored with `state = 'used'/'tossed'` but no page shows them yet).
- Categories are fixed in code (`CATEGORIES` in `models.py`); there is no category editor.
- Stitch's "Edit" inline row actions and swipe gestures are replaced by buttons under each card.

## Known limitations

- Fonts load from Google Fonts, so they need internet. Offline, the app falls back to system fonts and still works.
- The fixed bottom navigation is built with CSS on Streamlit buttons. It was written against Streamlit 1.65 but not checked in a real browser; if Streamlit changes its internal markup, adjust the `.st-key-nav` rules in `lowkeytoki/styles.py`.

## Project layout

```
app.py                  entry point: page config, top bar, routing, bottom nav
lowkeytoki/
  barcode.py            barcode decoding (zxing-cpp) and Open Food Facts lookup
  models.py             categories, Product, expiry status logic
  validation.py         form validation (errors + warnings)
  db.py                 SQLite schema, CRUD, search, demo data
  styles.py             global CSS (Stitch look, fonts, bottom nav)
  components.py         HTML snippets (cards, stat grid, empty states)
  views.py              one function per page + edit/delete dialogs
  state.py              navigation and flash-message helpers
tests/                  pytest: logic, database, barcode, headless page runs
.streamlit/config.toml  theme colours
data/                   SQLite file lives here (git-ignored)
```

## Ideas for next steps

1. A "History" page listing used/tossed items.
2. Reminders: a daily summary (email or desktop notification) built on `db.list_products()`.
3. Expiry-date OCR (for example with `pytesseract`), with manual entry kept as the fallback.
4. Editable categories and a CSV export.
