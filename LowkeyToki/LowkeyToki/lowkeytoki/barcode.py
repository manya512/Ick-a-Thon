"""Barcode decoding via zxing-cpp and product metadata lookup via Open Food Facts."""
from __future__ import annotations

import io
from typing import Any, Optional

from PIL import Image
import requests
import zxingcpp

USER_AGENT = "LowkeyToki/1.0 (hackathon expiry tracker; contact: lowkeytoki@example.com)"
TIMEOUT_SECONDS = 5.0

APIS = [
    ("https://world.openfoodfacts.org/api/v2/product/{code}.json", "food"),
    ("https://world.openbeautyfacts.org/api/v2/product/{code}.json", "cosmetics"),
    ("https://world.openproductsfacts.org/api/v2/product/{code}.json", "other"),
]

# Track last lookup outcome for user messages: None, 'network', or 'not_found'
LAST_ERROR: Optional[str] = None


def decode_barcode(image_bytes: Any) -> str | None:
    """Decode barcode text from image bytes or a file-like object using zxing-cpp."""
    if not image_bytes:
        return None
    try:
        if isinstance(image_bytes, bytes):
            image = Image.open(io.BytesIO(image_bytes))
        elif hasattr(image_bytes, "read"):
            if hasattr(image_bytes, "seek"):
                image_bytes.seek(0)
            data = image_bytes.read()
            if hasattr(image_bytes, "seek"):
                image_bytes.seek(0)
            image = Image.open(io.BytesIO(data))
        else:
            image = Image.open(image_bytes)

        if image.mode not in ("L", "RGB"):
            image = image.convert("RGB")

        barcodes = zxingcpp.read_barcodes(image)
        if barcodes:
            text = barcodes[0].text.strip()
            return text if text else None
        return None
    except Exception:
        return None


def _guess_category(product_data: dict, default_category: str = "food") -> str:
    """Infer one of ('food', 'medicine', 'cosmetics', 'household', 'other')."""
    tags = product_data.get("categories_tags", [])
    if isinstance(tags, list):
        tags_str = " ".join(tags).lower()
    else:
        tags_str = str(tags).lower()

    name = str(product_data.get("product_name") or "").lower()
    categories = str(product_data.get("categories") or "").lower()
    combined = f"{tags_str} {categories} {name}"

    if default_category == "cosmetics":
        if any(k in combined for k in ["medicine", "medication", "drug", "prescription", "pharma"]):
            return "medicine"
        return "cosmetics"

    if any(k in combined for k in [
        "cosmetic", "beauty", "skincare", "skin-care", "cream", "serum", "lotion",
        "shampoo", "sunscreen", "cleanser", "hyaluronic", "retinol", "perfume", "deodorant", "makeup"
    ]):
        return "cosmetics"

    if any(k in combined for k in [
        "medicine", "medication", "drug", "pharma", "tablet", "capsule",
        "pain relief", "paracetamol", "ibuprofen", "vitamin", "supplement"
    ]):
        return "medicine"

    if any(k in combined for k in [
        "household", "cleaning", "detergent", "dishwash", "laundry",
        "cleaner", "soap", "disinfectant", "bleach", "spray"
    ]):
        return "household"

    if any(k in combined for k in [
        "food", "beverage", "grocery", "snack", "drink", "dairy",
        "bakery", "produce", "fruit", "milk", "bread", "cereal", "meat", "pasta", "tea", "coffee"
    ]):
        return "food"

    return default_category


def lookup_product(code: str) -> dict | None:
    """Query Open Food Facts (with fallbacks to Open Beauty Facts and Open Products Facts).

    Returns a dict with 'name', 'brand', and 'category' on success, or None on failure.
    Sets LAST_ERROR to 'network' on network/timeout errors, or 'not_found' if unlisted.
    """
    global LAST_ERROR
    LAST_ERROR = None

    cleaned_code = str(code).strip()
    if not cleaned_code:
        return None

    headers = {"User-Agent": USER_AGENT}
    saw_network_error = False

    for url_tmpl, default_cat in APIS:
        url = url_tmpl.format(code=cleaned_code)
        try:
            resp = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == 1 and "product" in data:
                    prod = data["product"]
                    name = (
                        prod.get("product_name")
                        or prod.get("product_name_en")
                        or prod.get("generic_name")
                        or prod.get("generic_name_en")
                        or ""
                    ).strip()
                    brand = (prod.get("brands") or "").strip()
                    if not name and brand:
                        name = brand
                    if name:
                        category = _guess_category(prod, default_category=default_cat)
                        LAST_ERROR = None
                        return {
                            "name": name,
                            "brand": brand,
                            "category": category,
                        }
        except (requests.RequestException, requests.Timeout, requests.ConnectionError):
            saw_network_error = True
            continue
        except Exception:
            continue

    if saw_network_error:
        LAST_ERROR = "network"
    else:
        LAST_ERROR = "not_found"
    return None
