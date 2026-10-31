"""Читання файлів, створених застосунком (завантаження), і файлів-еталонів."""

from __future__ import annotations

import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    """Точний текст зі збереженням BOM і кінців рядків."""
    return path.read_bytes().decode("utf-8")
