"""Reading files produced by the app (downloads) and expected-result files."""

from __future__ import annotations

import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    """Exact text, BOM and line endings preserved."""
    return path.read_bytes().decode("utf-8")
