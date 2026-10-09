"""LowkeyToki - run with:  streamlit run app.py"""
import streamlit as st

from lowkeytoki import db, views
from lowkeytoki.components import top_bar
from lowkeytoki.models import STATUS_EXPIRED, compute_stats
from lowkeytoki.state import PAGE_TITLES, go, init_state, show_flash
from lowkeytoki.styles import inject_css

st.set_page_config(page_title="LowkeyToki", page_icon="🦠", layout="centered")

db.init_db()
init_state()
inject_css()
show_flash()

page = st.session_state["page"]
ick = compute_stats(db.list_products())[STATUS_EXPIRED]
st.markdown(top_bar(PAGE_TITLES[page], ick), unsafe_allow_html=True)

PAGE_FUNCS = {
    "overview": views.overview,
    "use_first": views.use_first,
    "add": views.add_item,
    "products": views.products_page,
    "categories": views.categories_page,
}
PAGE_FUNCS[page]()

# Bottom navigation (fixed to the bottom of the screen via CSS in styles.py)
NAV = [
    ("overview", "Overview", ":material/grid_view:"),
    ("use_first", "Use First", ":material/local_fire_department:"),
    ("add", "+", None),
    ("products", "Products", ":material/inventory_2:"),
    ("categories", "Categories", ":material/category:"),
]
with st.container(key="nav"):
    cols = st.columns(len(NAV))
    for col, (key, label, icon) in zip(cols, NAV):
        with col:
            st.button(
                label, key="nav_add" if key == "add" else f"nav_{key}", icon=icon,
                type="primary" if page == key and key != "add" else "secondary",
                on_click=go, args=(key,), use_container_width=True,
            )
