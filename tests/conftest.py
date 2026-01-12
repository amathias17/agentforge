from __future__ import annotations

from pathlib import Path
import os


def pytest_configure() -> None:
    base = Path(__file__).resolve().parent / ".tmp"
    base.mkdir(parents=True, exist_ok=True)
    os.environ["TMPDIR"] = str(base)
    os.environ["TEMP"] = str(base)
    os.environ["TMP"] = str(base)
