"""One render function per page."""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from . import components as ui
from . import db
from .models import (
    CATEGORIES, LOCATIONS, SOON_DAYS, STATE_TOSSED, STATE_USED, STATUS_EXPIRED, STATUS_FRESH,
    STATUS_SOON, UPCOMING_DAYS, Product, category_emoji, category_label, compute_stats,
    sort_nearest_expiry,
)
from .state import apply_prefill, flash, go
from .validation import MAX_DATE, MAX_NAME, MAX_NOTES, MAX_QTY, MIN_DATE, validate_product

NO_LOCATION = "(none)"
STATUS_FILTERS = {"all": "All status", STATUS_EXPIRED: "Ick Zone", STATUS_SOON: "Expiring", STATUS_FRESH: "Fresh"}
SORTS = {"expiry": "Nearest expiry", "name": "Name A-Z", "added": "Recently added"}


# ----------------------------------------------------------------- actions
def _mark(product_id: int, state: str, message: str) -> None:
    db.set_state(product_id, state)
    flash(message)


def _load_demo() -> None:
    n = db.add_demo_data()
    flash(f"Loaded {n} demo products (marked DEMO).")


def _clear_demo() -> None:
    n = db.clear_demo_data()
    flash(f"Removed {n} demo products.")


def _use_toss_buttons(p: Product) -> None:
    c1, c2, _ = st.columns([1, 1, 1.4])
    c1.button("Used", key=f"used_{p.id}", icon=":material/done_all:", on_click=_mark,
              args=(p.id, STATE_USED, f"Marked used: {p.name}"), type="primary")
    c2.button("Toss", key=f"toss_{p.id}", icon=":material/delete:", on_click=_mark,
              args=(p.id, STATE_TOSSED, f"Tossed: {p.name}"))


# ----------------------------------------------------------------- shared form
def _product_fields(prefix: str, pid_label: str = "") -> dict:
    """Render the shared product fields; widget state lives in session_state[prefix_*]."""
    name = st.text_input("Product name *", key=f"{prefix}_name", max_chars=MAX_NAME,
                         placeholder="e.g., Oat Milk, Retinol Serum, Ibuprofen")
    category = st.pills("Category", options=list(CATEGORIES), key=f"{prefix}_cat",
                        format_func=lambda k: f"{category_emoji(k)} {category_label(k)}",
                        selection_mode="single")
    expiry = st.date_input("Expiry date *", key=f"{prefix}_expiry", min_value=MIN_DATE, max_value=MAX_DATE)
    qty = st.number_input("Quantity", key=f"{prefix}_qty", min_value=1, max_value=MAX_QTY, step=1)
    with st.expander("More details (optional)"):
        loc = st.selectbox("Storage location", [NO_LOCATION] + LOCATIONS, key=f"{prefix}_loc")
        has_purchase = st.checkbox("I know the purchase date", key=f"{prefix}_haspurchase")
        purchase = None
        if has_purchase:
            purchase = st.date_input("Purchase date", key=f"{prefix}_purchase", min_value=MIN_DATE, max_value=MAX_DATE)
        notes = st.text_area("Notes", key=f"{prefix}_notes", max_chars=MAX_NOTES, height=80,
                             placeholder="e.g., opened on Monday, store in a cool place")
    return {
        "name": name, "category": category or "", "expiry_date": expiry, "quantity": qty,
        "notes": notes, "storage_location": "" if loc == NO_LOCATION else loc, "purchase_date": purchase,
    }


def _seed_form(prefix: str, p: Product | None = None) -> None:
    """Set default widget values (must run before the widgets are created)."""
    ss = st.session_state
    ss[f"{prefix}_name"] = p.name if p else ""
    ss[f"{prefix}_cat"] = p.category if p else "food"
    ss[f"{prefix}_expiry"] = p.expiry_date if p else date.today() + timedelta(days=7)
    ss[f"{prefix}_qty"] = p.quantity if p else 1
    ss[f"{prefix}_loc"] = (p.storage_location if p and p.storage_location in LOCATIONS else NO_LOCATION)
    ss[f"{prefix}_haspurchase"] = bool(p and p.purchase_date)
    ss[f"{prefix}_purchase"] = (p.purchase_date if p and p.purchase_date else date.today())
    ss[f"{prefix}_notes"] = p.notes if p else ""


def _show_messages(errors: list[str], warnings: list[str]) -> None:
    for e in errors:
        st.error(e, icon=":material/error:")
    for w in warnings:
        st.warning(w, icon=":material/warning:")


# ----------------------------------------------------------------- dialogs
@st.dialog("Edit product")
def edit_dialog(product_id: int) -> None:
    p = db.get_product(product_id)
    if p is None:
        st.error("That product no longer exists.")
        return
    prefix = f"edit{product_id}"
    if f"{prefix}_name" not in st.session_state:
        _seed_form(prefix, p)
    data = _product_fields(prefix)
    c1, c2 = st.columns(2)
    if c1.button("Save changes", type="primary", key=f"{prefix}_save", use_container_width=True):
        clean, errors, warnings = validate_product(**data)
        if errors:
            _show_messages(errors, warnings)
        else:
            db.update_product(product_id, clean)
            for k in [k for k in st.session_state if k.startswith(prefix)]:
                del st.session_state[k]
            flash(f"Saved changes to {clean['name']}.")
            st.rerun()
    if c2.button("Cancel", key=f"{prefix}_cancel", use_container_width=True):
        for k in [k for k in st.session_state if k.startswith(prefix)]:
            del st.session_state[k]
        st.rerun()


@st.dialog("Delete product?")
def delete_dialog(product_id: int) -> None:
    p = db.get_product(product_id)
    if p is None:
        st.info("Already gone.")
        return
    st.markdown(f"**{p.name}** will be removed for good. Use *Used* or *Toss* instead if you just want it off your lists.")
    c1, c2 = st.columns(2)
    if c1.button("Delete", type="primary", key=f"del_confirm_{product_id}", use_container_width=True):
        db.delete_product(product_id)
        flash(f"Deleted {p.name}.")
        st.rerun()
    if c2.button("Keep it", key=f"del_cancel_{product_id}", use_container_width=True):
        st.rerun()


# ----------------------------------------------------------------- pages
def overview() -> None:
    products = db.list_products()
    stats = compute_stats(products)
    st.markdown("<div class='lt-hero-title'>Let's deal with the ick. 🦠</div>"
                "<div class='lt-hero-sub'>Know what's expiring before it becomes a problem.</div>",
                unsafe_allow_html=True)

    def _search_cb() -> None:
        q = st.session_state.get("overview_search", "")
        if q.strip():
            go("products", {"prod_search": q.strip()})

    st.text_input("Search", key="overview_search", placeholder="Search products...",
                  label_visibility="collapsed", on_change=_search_cb)
    st.button("Add product", key="ov_add", icon=":material/add_circle:", type="primary",
              use_container_width=True, on_click=go, args=("add",))

    if stats["total"] == 0:
        st.markdown(ui.empty_state("🍓", "Nothing tracked yet",
                                   "Add your first product and LowkeyToki will watch its expiry date."),
                    unsafe_allow_html=True)
        st.button("Load demo data", key="ov_demo_empty", on_click=_load_demo, use_container_width=True)
        st.markdown(ui.micro("Your fridge called. It wants organisation."), unsafe_allow_html=True)
        return

    st.markdown(ui.stat_grid(stats), unsafe_allow_html=True)
    st.markdown(ui.health_pulse(stats), unsafe_allow_html=True)

    queue = sort_nearest_expiry([p for p in products if p.status() != STATUS_FRESH or p.days_left() <= UPCOMING_DAYS])[:3]
    h1, h2 = st.columns([2, 1])
    h1.markdown("<h2 style='margin:0;font-size:24px'>Use First</h2><div class='lt-hero-sub'>Rescue them before it's too late</div>",
                unsafe_allow_html=True)
    h2.button("View all", key="ov_viewall", on_click=go, args=("use_first",), use_container_width=True)
    for p in queue:
        st.markdown(ui.product_row(p), unsafe_allow_html=True)
        _use_toss_buttons(p)

    if queue:
        first = queue[0]
        st.markdown(ui.tip_card("🍽️", "Use this one first", f"{first.name}: {first.expiry_date.strftime('%d %b')}."),
                    unsafe_allow_html=True)
    st.markdown(ui.micro("Your fridge called. It wants organisation."), unsafe_allow_html=True)
    st.markdown(ui.note("Expiry dates are guidelines. Always check food, medicine and skincare before using."),
                unsafe_allow_html=True)

    with st.expander("Demo data"):
        st.caption("Demo products are fake sample items, flagged DEMO, with dates relative to today.")
        c1, c2 = st.columns(2)
        c1.button("Load demo data", key="ov_demo", on_click=_load_demo, use_container_width=True)
        c2.button("Clear demo data", key="ov_demo_clear", on_click=_clear_demo, use_container_width=True,
                  disabled=not db.has_demo_data())


def use_first() -> None:
    products = sort_nearest_expiry(db.list_products())
    expired = [p for p in products if p.status() == STATUS_EXPIRED]
    soon = [p for p in products if p.status() == STATUS_SOON]
    upcoming = [p for p in products if p.status() == STATUS_FRESH and p.days_left() <= UPCOMING_DAYS]
    later = len(products) - len(expired) - len(soon) - len(upcoming)

    st.markdown(ui.banner("Don't let them turn into science experiments! 🧪", "Rescue them before it's too late.",
                          "Your nearest expiry dates, all in one place."), unsafe_allow_html=True)
    if not products:
        st.markdown(ui.empty_state("🌱", "Nothing to rescue", "Add products and the ones expiring first will show up here."),
                    unsafe_allow_html=True)
        st.button("Add product", key="uf_add", type="primary", on_click=go, args=("add",), use_container_width=True)
        return
    if not (expired or soon or upcoming):
        st.markdown(ui.empty_state("✨", "All calm", f"Nothing expires in the next {UPCOMING_DAYS} days."),
                    unsafe_allow_html=True)

    sections = [
        ("Expired: The Ick Zone 🦠", expired, "ick", f"{len(expired)} urgent"),
        ("Expiring soon 🚨", soon, "soon", f"{len(soon)} items"),
        (f"Upcoming (next {UPCOMING_DAYS} days) 👀", upcoming, "fresh", f"{len(upcoming)} items"),
    ]
    for title, items, kind, count_text in sections:
        if not items:
            continue
        st.markdown(ui.section_head(title, count_text, kind), unsafe_allow_html=True)
        for p in items:
            st.markdown(ui.product_row(p), unsafe_allow_html=True)
            _use_toss_buttons(p)
    if later:
        st.caption(f"{later} more item{'s' if later != 1 else ''} expire later than {UPCOMING_DAYS} days. See Products.")
    st.markdown(ui.note("Recorded expiry dates are guidelines. Always inspect food condition before consuming."),
                unsafe_allow_html=True)


def add_item() -> None:
    ss = st.session_state
    if ss.pop("_reset_add", False) or "add_name" not in ss:
        _seed_form("add")

    def _preset(days: int) -> None:
        ss["add_expiry"] = date.today() + timedelta(days=days)

    st.markdown(ui.banner("Freshness Lab", "Add new product", "Track it before it develops a personality. 🍓", "🍓"),
                unsafe_allow_html=True)

    st.markdown("<div class='lt-soon-card'><span style='font-size:26px'>📷</span><div>"
                "<div class='t'>Scan expiry date <span class='lt-chipnote'>COMING SOON</span></div>"
                "<div class='d'>Scanning isn't built yet. Type the date below.</div></div></div>",
                unsafe_allow_html=True)

    st.caption("Quick expiry presets")
    cols = st.columns(4)
    for col, (label, days) in zip(cols, [("+3 days", 3), ("+1 week", 7), ("+1 month", 30), ("+6 months", 180)]):
        col.button(label, key=f"preset_{days}", on_click=_preset, args=(days,), use_container_width=True)

    data = _product_fields("add")
    st.markdown(ui.note("Reminders are not built yet. Check the Use First tab to see what's expiring.", "🔔"),
                unsafe_allow_html=True)

    if st.button("Save product", key="add_save", icon=":material/check_circle:", type="primary", use_container_width=True):
        clean, errors, warnings = validate_product(**data)
        if errors:
            _show_messages(errors, warnings)
        else:
            db.add_product(clean)
            flash(f"Saved {clean['name']}." + (" It's already expired." if warnings else ""))
            ss["_reset_add"] = True
            st.rerun()
    st.button("Cancel", key="add_cancel", on_click=go, args=("overview",), use_container_width=True)


def _sort_products(products: list[Product], sort_key: str) -> list[Product]:
    if sort_key == "name":
        return sorted(products, key=lambda p: p.name.lower())
    if sort_key == "added":
        return sorted(products, key=lambda p: p.id, reverse=True)
    return sort_nearest_expiry(products)


def products_page() -> None:
    apply_prefill()
    ss = st.session_state
    ss.setdefault("prod_cat", "all")
    ss.setdefault("prod_status", "all")
    ss.setdefault("prod_sort", "expiry")

    everything = db.list_products()
    st.markdown("<div class='lt-hero-title'>Product inventory</div>"
                f"<div class='lt-hero-sub'>{len(everything)} tracked product{'s' if len(everything) != 1 else ''}</div>",
                unsafe_allow_html=True)
    if not everything:
        st.markdown(ui.empty_state("🍓", "No products yet", "Add your first one to start tracking."),
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.button("Add product", key="pr_add_empty", type="primary", on_click=go, args=("add",), use_container_width=True)
        c2.button("Load demo data", key="pr_demo_empty", on_click=_load_demo, use_container_width=True)
        return

    search = st.text_input("Search", key="prod_search", placeholder="Search by name or notes...",
                           label_visibility="collapsed")
    counts = {"all": len(everything)}
    for k in CATEGORIES:
        counts[k] = sum(1 for p in everything if p.category == k)
    st.pills("Category", ["all"] + list(CATEGORIES), key="prod_cat", label_visibility="collapsed",
             format_func=lambda k: f"All ({counts['all']})" if k == "all"
             else f"{category_emoji(k)} {category_label(k).split(' &')[0]} ({counts[k]})")
    c1, c2 = st.columns([3, 2])
    c1.pills("Status", list(STATUS_FILTERS), key="prod_status", label_visibility="collapsed",
             format_func=STATUS_FILTERS.get)
    c2.selectbox("Sort", list(SORTS), key="prod_sort", format_func=SORTS.get, label_visibility="collapsed")

    category = ss.get("prod_cat") or "all"
    status = ss.get("prod_status") or "all"
    items = db.list_products(search=search, category=category)
    if status != "all":
        items = [p for p in items if p.status() == status]
    items = _sort_products(items, ss.get("prod_sort") or "expiry")

    if not items:
        st.markdown(ui.empty_state("🔍", "No matching goodies!", "Try different search words or reset the filters."),
                    unsafe_allow_html=True)

        def _reset() -> None:
            ss["prod_search"], ss["prod_cat"], ss["prod_status"] = "", "all", "all"
        st.button("Reset filters", key="pr_reset", on_click=_reset, use_container_width=True)
        return

    st.caption(f"Showing {len(items)} of {len(everything)}")
    for p in items:
        st.markdown(ui.product_row(p), unsafe_allow_html=True)
        if p.notes:
            st.caption(f"📝 {p.notes}")
        c1, c2, _ = st.columns([1, 1, 1.4])
        if c1.button("Edit", key=f"edit_{p.id}", icon=":material/edit:"):
            edit_dialog(p.id)
        if c2.button("Delete", key=f"delete_{p.id}", icon=":material/delete:"):
            delete_dialog(p.id)


def categories_page() -> None:
    products = db.list_products()
    st.markdown("<div class='lt-hero-title'>Categories</div><div class='lt-hero-sub'>Tap one to see what's inside.</div>",
                unsafe_allow_html=True)
    if not products:
        st.markdown(ui.empty_state("📦", "Categories are empty", "They fill up as you add products."),
                    unsafe_allow_html=True)
        st.button("Add product", key="cat_add", type="primary", on_click=go, args=("add",), use_container_width=True)
        return
    for key, (label, emoji, _icon) in CATEGORIES.items():
        mine = [p for p in products if p.category == key]
        stats = compute_stats(mine)
        detail = f"{stats['total']} item{'s' if stats['total'] != 1 else ''}"
        if stats[STATUS_EXPIRED]:
            detail += f" • {stats[STATUS_EXPIRED]} in the Ick Zone"
        if stats[STATUS_SOON]:
            detail += f" • {stats[STATUS_SOON]} expiring soon"
        badge_cls = "ick" if stats[STATUS_EXPIRED] else ("soon" if stats[STATUS_SOON] else "fresh")
        badge = "Needs attention" if stats[STATUS_EXPIRED] else ("Check soon" if stats[STATUS_SOON] else "All good")
        st.markdown(ui.one_line(
            f'<div class="lt-item"><div class="left"><div class="lt-avatar">{emoji}</div><div style="min-width:0">'
            f'<div class="lt-name">{label}</div><div class="lt-meta">{detail}</div></div></div>'
            f'<span class="lt-badge {badge_cls}">{badge}</span></div>'), unsafe_allow_html=True)
        st.button(f"Browse {label.split(' &')[0].lower()}", key=f"cat_{key}", on_click=go,
                  args=("products", {"prod_cat": key, "prod_status": "all", "prod_search": ""}),
                  disabled=not mine)
