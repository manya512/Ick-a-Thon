import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Every test gets its own empty database."""
    monkeypatch.setenv("LOWKEYTOKI_DB", str(tmp_path / "test.db"))
    from lowkeytoki import db
    db.init_db()
    yield
