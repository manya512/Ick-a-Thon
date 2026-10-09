"""Tests for barcode decoding and product lookup."""
import io
from unittest.mock import MagicMock

from PIL import Image
import pytest
import requests

from lowkeytoki import barcode


def _dummy_image_bytes():
    img = Image.new("RGB", (50, 50), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_decode_barcode_none_and_invalid():
    assert barcode.decode_barcode(None) is None
    assert barcode.decode_barcode(b"") is None
    assert barcode.decode_barcode(b"not an image bytes") is None


def test_decode_barcode_success(monkeypatch):
    mock_result = MagicMock()
    mock_result.text = "7394376616037"
    monkeypatch.setattr(barcode.zxingcpp, "read_barcodes", lambda img: [mock_result])

    code = barcode.decode_barcode(_dummy_image_bytes())
    assert code == "7394376616037"


def test_decode_barcode_not_found(monkeypatch):
    monkeypatch.setattr(barcode.zxingcpp, "read_barcodes", lambda img: [])
    code = barcode.decode_barcode(_dummy_image_bytes())
    assert code is None


def test_lookup_empty_code():
    assert barcode.lookup_product("") is None
    assert barcode.lookup_product("   ") is None


def test_lookup_product_open_food_facts_success(monkeypatch):
    calls = []

    def mock_get(url, headers=None, timeout=None):
        calls.append(url)
        assert headers and "User-Agent" in headers
        assert timeout == 5.0
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Oat Milk Barista Edition",
                "brands": "Oatly",
                "categories_tags": ["en:plant-based-foods", "en:milks"],
            },
        }
        return resp

    monkeypatch.setattr(requests, "get", mock_get)

    result = barcode.lookup_product("7394376616037")
    assert result == {
        "name": "Oat Milk Barista Edition",
        "brand": "Oatly",
        "category": "food",
    }
    assert len(calls) == 1
    assert "openfoodfacts.org" in calls[0]
    assert barcode.LAST_ERROR is None


def test_lookup_product_fallback_to_beauty_facts(monkeypatch):
    calls = []

    def mock_get(url, headers=None, timeout=None):
        calls.append(url)
        resp = MagicMock()
        if "openfoodfacts.org" in url:
            resp.status_code = 404
            resp.json.return_value = {"status": 0}
        elif "openbeautyfacts.org" in url:
            resp.status_code = 200
            resp.json.return_value = {
                "status": 1,
                "product": {
                    "product_name": "Vitamin C Glow Serum",
                    "brands": "Glow Lab",
                    "categories_tags": ["en:skin-care", "en:face-serums"],
                },
            }
        else:
            resp.status_code = 404
            resp.json.return_value = {"status": 0}
        return resp

    monkeypatch.setattr(requests, "get", mock_get)

    result = barcode.lookup_product("123456789012")
    assert result == {
        "name": "Vitamin C Glow Serum",
        "brand": "Glow Lab",
        "category": "cosmetics",
    }
    assert len(calls) == 2
    assert "openfoodfacts.org" in calls[0]
    assert "openbeautyfacts.org" in calls[1]
    assert barcode.LAST_ERROR is None


def test_lookup_product_fallback_to_products_facts(monkeypatch):
    calls = []

    def mock_get(url, headers=None, timeout=None):
        calls.append(url)
        resp = MagicMock()
        if "openproductsfacts.org" in url:
            resp.status_code = 200
            resp.json.return_value = {
                "status": 1,
                "product": {
                    "product_name": "Eco Laundry Detergent",
                    "brands": "CleanEco",
                    "categories": "Household cleaning supplies, laundry",
                },
            }
        else:
            resp.status_code = 404
            resp.json.return_value = {"status": 0}
        return resp

    monkeypatch.setattr(requests, "get", mock_get)

    result = barcode.lookup_product("987654321098")
    assert result == {
        "name": "Eco Laundry Detergent",
        "brand": "CleanEco",
        "category": "household",
    }
    assert len(calls) == 3
    assert barcode.LAST_ERROR is None


def test_lookup_product_not_found(monkeypatch):
    def mock_get(url, headers=None, timeout=None):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"status": 0, "status_verbose": "product not found"}
        return resp

    monkeypatch.setattr(requests, "get", mock_get)

    result = barcode.lookup_product("0000000000000")
    assert result is None
    assert barcode.LAST_ERROR == "not_found"


def test_lookup_product_network_error(monkeypatch):
    def mock_get(url, headers=None, timeout=None):
        raise requests.ConnectionError("Network connection failed")

    monkeypatch.setattr(requests, "get", mock_get)

    result = barcode.lookup_product("7394376616037")
    assert result is None
    assert barcode.LAST_ERROR == "network"


def test_category_guessing():
    assert barcode._guess_category({"product_name": "Paracetamol 500mg"}) == "medicine"
    assert barcode._guess_category({"categories_tags": ["en:dietary-supplements"]}) == "medicine"
    assert barcode._guess_category({"product_name": "Moisturizing Face Cream"}) == "cosmetics"
    assert barcode._guess_category({"categories": "Dishwashing liquid"}) == "household"
    assert barcode._guess_category({"product_name": "Whole Milk"}) == "food"
    assert barcode._guess_category({"product_name": "Unknown Widget"}, default_category="other") == "other"

