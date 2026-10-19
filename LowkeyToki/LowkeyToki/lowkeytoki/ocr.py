"""Optical Character Recognition (OCR) module for packaging expiry dates.
Uses native Windows OCR (winocr) when running on Windows for fast, offline,
hardware-accelerated OCR. Falls back gracefully if unavailable.
"""
from __future__ import annotations

import asyncio
import io
import re
from datetime import date
from typing import BinaryIO

from PIL import Image

MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

_HAS_WINOCR = False
try:
    import winocr
    _HAS_WINOCR = True
except Exception:
    _HAS_WINOCR = False


def normalize_ocr_text(text: str) -> str:
    """Clean up common OCR quirks: joined letter/numbers, bullets, unusual dashes."""
    if not text:
        return ""
    # Separate joined letters and digits (e.g. 'EXP2026' -> 'EXP 2026', '24OCT' -> '24 OCT')
    s = re.sub(r"([A-Za-z])(\d)", r"\1 \2", text)
    s = re.sub(r"(\d)([A-Za-z])", r"\1 \2", s)
    # Replace unicode bullets, symbols, and alternate dashes with standard hyphen
    s = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u2010-\u2015\u2212\ufffd_]+", "-", s)
    return s.upper()


def parse_expiry_date(text: str) -> date | None:
    """Extract a sensible expiry date from raw OCR text.
    Handles YYYY-MM-DD, DD/MM/YYYY, DD MMM YYYY, MM/YY, and prefix keywords (EXP, BB, USE BY).
    """
    if not text:
        return None
    cleaned = normalize_ocr_text(text).replace("\n", " ").replace("\r", " ")

    # 1. YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD
    m = re.search(r"\b(20\d\d)[-/. ](0[1-9]|1[0-2])[-/. ](0[1-9]|[12]\d|3[01])\b", cleaned)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # 2. DD-MM-YYYY or DD/MM/YYYY or DD.MM.YYYY
    m = re.search(r"\b(0[1-9]|[12]\d|3[01])[-/. ](0[1-9]|1[0-2])[-/. ](20\d\d)\b", cleaned)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass

    # 3. DD-MM-YY or DD/MM/YY or DD.MM.YY
    m = re.search(r"\b(0[1-9]|[12]\d|3[01])[-/. ](0[1-9]|1[0-2])[-/. ](\d\d)\b", cleaned)
    if m:
        try:
            year = 2000 + int(m.group(3))
            return date(year, int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass

    # 4. DD MMM YYYY or DD MMM YY (e.g. 24 OCT 2026 or 24-OCT-26)
    m = re.search(r"\b(0?[1-9]|[12]\d|3[01])[\s\-/]+([A-Z]{3,9})[\s\-/]+(20\d\d|\d\d)\b", cleaned)
    if m:
        mo_str = m.group(2).lower()
        if mo_str in MONTHS:
            mo = MONTHS[mo_str]
            d = int(m.group(1))
            y_str = m.group(3)
            y = int(y_str) if len(y_str) == 4 else 2000 + int(y_str)
            try:
                return date(y, mo, d)
            except ValueError:
                pass

    # 5. MMM DD, YYYY or MMM DD YYYY (e.g. OCT 24, 2026)
    m = re.search(r"\b([A-Z]{3,9})[\s\-/]+(0?[1-9]|[12]\d|3[01])(?:,|\s)+?(20\d\d|\d\d)\b", cleaned)
    if m:
        mo_str = m.group(1).lower()
        if mo_str in MONTHS:
            mo = MONTHS[mo_str]
            d = int(m.group(2))
            y_str = m.group(3)
            y = int(y_str) if len(y_str) == 4 else 2000 + int(y_str)
            try:
                return date(y, mo, d)
            except ValueError:
                pass

    # 6. MM/YYYY or MM-YYYY
    m = re.search(r"\b(0[1-9]|1[0-2])[-/. ](20\d\d)\b", cleaned)
    if m:
        mo = int(m.group(1))
        y = int(m.group(2))
        try:
            day = 31 if mo in (1, 3, 5, 7, 8, 10, 12) else (30 if mo != 2 else 28)
            return date(y, mo, day)
        except ValueError:
            pass

    # 7. MM/YY with optional prefix (EXP 05/27, BB 11/26)
    m = re.search(r"(?:EXP|BB|BEST|USE|BEFORE|BY)?\s*[:.]?\s*\b(0[1-9]|1[0-2])[-/. ](\d\d)\b", cleaned)
    if m:
        mo = int(m.group(1))
        y = 2000 + int(m.group(2))
        try:
            day = 31 if mo in (1, 3, 5, 7, 8, 10, 12) else (30 if mo != 2 else 28)
            return date(y, mo, day)
        except ValueError:
            pass

    return None


def recognize_text(image_input: bytes | BinaryIO | Image.Image) -> str:
    """Perform OCR on an image and return recognized plain text."""
    pil_img: Image.Image
    if isinstance(image_input, Image.Image):
        pil_img = image_input
    elif isinstance(image_input, bytes):
        pil_img = Image.open(io.BytesIO(image_input))
    elif hasattr(image_input, "read"):
        data = image_input.read()
        pil_img = Image.open(io.BytesIO(data))
    else:
        return ""

    if _HAS_WINOCR:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(winocr.recognize_pil(pil_img, "en"))
            loop.close()
            return res.text if res else ""
        except Exception:
            pass

    return ""


def scan_expiry_date(image_input: bytes | BinaryIO | Image.Image) -> tuple[str, date | None]:
    """Recognize text from an image and parse an expiry date."""
    text = recognize_text(image_input)
    parsed = parse_expiry_date(text)
    return text, parsed

