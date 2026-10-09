"""Tiny helpers around st.session_state for navigation and flash messages."""
from __future__ import annotations

import streamlit as st

PAGES = ["overview", "use_first", "add", "products", "categories"]
PAGE_TITLES = {
    "overview": "Overview", "use_first": "Use First", "add": "Add Item",
    "products": "Products", "categories": "Categories",
}


def init_state() -> None:
    st.session_state.setdefault("page", "overview")


def go(page: str, prefill: dict | None = None) -> None:
    """Callback-safe navigation. `prefill` seeds widget keys on the target page."""
    st.session_state["page"] = page
    if prefill:
        st.session_state["_prefill"] = prefill


def apply_prefill() -> None:
    """Call at the top of a page, BEFORE its widgets are created."""
    for key, value in st.session_state.pop("_prefill", {}).items():
        st.session_state[key] = value


def flash(message: str) -> None:
    st.session_state["_flash"] = message


def show_flash() -> None:
    msg = st.session_state.pop("_flash", None)
    if msg:
        st.toast(msg)
