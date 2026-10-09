from datetime import date, timedelta

from lowkeytoki import db
from lowkeytoki.models import (
    STATUS_EXPIRED, STATUS_FRESH, STATUS_SOON, Product, compute_stats, describe_days,
    sort_nearest_expiry, status_for_days,
)
from lowkeytoki.validation import validate_product

TODAY = date(2026, 10, 9)


def test_status_boundaries():
    assert status_for_days(-1) == STATUS_EXPIRED
    assert status_for_days(0) == STATUS_SOON      # expires today is NOT expired
    assert status_for_days(3) == STATUS_SOON
    assert status_for_days(4) == STATUS_FRESH


def test_describe_days():
    assert describe_days(0) == "Expires today"
    assert describe_days(1) == "Expires tomorrow"
    assert describe_days(-1) == "Expired yesterday"
    assert describe_days(-5) == "Expired 5 days ago"


def test_sort_and_stats():
    mk = lambda i, d: Product(i, f"p{i}", "food", TODAY + timedelta(days=d))
    ps = [mk(1, 10), mk(2, -2), mk(3, 0), mk(4, 2)]
    assert [p.id for p in sort_nearest_expiry(ps)] == [2, 3, 4, 1]
    s = compute_stats(ps, TODAY)
    assert (s["total"], s[STATUS_EXPIRED], s[STATUS_SOON], s[STATUS_FRESH]) == (4, 1, 2, 1)


def test_validation_ok_and_errors():
    clean, errors, warnings = validate_product(" Milk ", "food", TODAY + timedelta(days=2), 2, today=TODAY)
    assert not errors and not warnings and clean["name"] == "Milk"
    _, errors, _ = validate_product("", "nope", None, 0, today=TODAY)
    assert len(errors) == 4
    _, errors, warnings = validate_product("Old", "food", TODAY - timedelta(days=1), 1, today=TODAY)
    assert not errors and warnings
    _, errors, _ = validate_product("X", "food", TODAY, 1, purchase_date=TODAY + timedelta(days=1), today=TODAY)
    assert errors


def _data(name="Milk", days=2, cat="food"):
    return {"name": name, "category": cat, "expiry_date": date.today() + timedelta(days=days), "quantity": 1}


def test_crud_roundtrip():
    pid = db.add_product(_data())
    assert db.get_product(pid).name == "Milk"
    d = _data("Oat Milk", 5)
    d["notes"] = "opened"
    assert db.update_product(pid, d)
    assert db.get_product(pid).notes == "opened"
    db.set_state(pid, "used")
    assert db.list_products() == []
    assert db.delete_product(pid)
    assert db.get_product(pid) is None


def test_search_filter_and_injection_safe():
    db.add_product(_data("Greek Yogurt"))
    db.add_product(_data("Serum", cat="cosmetics"))
    assert [p.name for p in db.list_products(search="yog")] == ["Greek Yogurt"]
    assert [p.name for p in db.list_products(category="cosmetics")] == ["Serum"]
    assert db.list_products(search="'; DROP TABLE products; --") == []
    assert db.list_products(search="%") == []          # wildcard is escaped
    assert len(db.list_products()) == 2


def test_demo_data():
    db.add_demo_data()
    assert db.has_demo_data()
    db.add_product(_data("Mine"))
    db.clear_demo_data()
    assert [p.name for p in db.list_products()] == ["Mine"]
