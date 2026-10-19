"""Tests for optical character recognition and expiry date parsing."""
from datetime import date
from PIL import Image, ImageDraw

from lowkeytoki import ocr


def test_parse_expiry_date_formats():
    assert ocr.parse_expiry_date("EXP: 2026-10-24") == date(2026, 10, 24)
    assert ocr.parse_expiry_date("BEST BEFORE 24/10/2026") == date(2026, 10, 24)
    assert ocr.parse_expiry_date("BB 15 NOV 2026") == date(2026, 11, 15)
    assert ocr.parse_expiry_date("USE BY 12.05.2027") == date(2027, 5, 12)
    assert ocr.parse_expiry_date("24 OCT 26") == date(2026, 10, 24)
    assert ocr.parse_expiry_date("EXP 05/27") == date(2027, 5, 31)
    assert ocr.parse_expiry_date("EXP 11/2028") == date(2028, 11, 30)
    assert ocr.parse_expiry_date("OCT 24, 2026") == date(2026, 10, 24)
    assert ocr.parse_expiry_date("random text with no date") is None
    assert ocr.parse_expiry_date("") is None


def test_scan_expiry_date_synthetic_image():
    img = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 30), "EXP 2026-12-15", fill="black")

    raw_text, detected = ocr.scan_expiry_date(img)
    if ocr._HAS_WINOCR:
        assert detected == date(2026, 12, 15)
        assert "2026" in raw_text
    else:
        # If winocr not available in CI, verify graceful return
        assert isinstance(raw_text, str)

