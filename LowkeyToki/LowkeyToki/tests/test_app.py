"""Smoke tests that run the real Streamlit script headlessly."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def run():
    at = AppTest.from_file(APP, default_timeout=30)
    return at.run()


def click(at, key):
    next(b for b in at.button if b.key == key).click()
    return at.run()


def test_every_page_renders_empty_and_with_demo():
    at = run()
    assert not at.exception
    for key in ["nav_use_first", "nav_add", "nav_products", "nav_categories", "nav_overview"]:
        at = click(at, key)
        assert not at.exception, key
    at = click(at, "ov_demo_empty")
    assert not at.exception
    for key in ["nav_use_first", "nav_add", "nav_products", "nav_categories", "nav_overview"]:
        at = click(at, key)
        assert not at.exception, key


def test_add_flow_validation_and_save():
    from lowkeytoki import db
    at = run()
    at = click(at, "nav_add")
    at = click(at, "add_save")                       # empty name -> error, nothing saved
    assert any("name" in e.value.lower() for e in at.error)
    assert db.list_products() == []
    next(t for t in at.text_input if t.key == "add_name").set_value("Retinol Serum")
    at = at.run()
    at = click(at, "add_save")
    assert not at.exception
    assert [p.name for p in db.list_products()] == ["Retinol Serum"]


def test_used_button_removes_from_active():
    from lowkeytoki import db
    db.add_demo_data()
    at = run()
    n = len(db.list_products())
    key = next(b.key for b in at.button if b.key and b.key.startswith("used_"))
    at = click(at, key)
    assert not at.exception
    assert len(db.list_products()) == n - 1
