"""Доступ до текстів із ui_texts.json: сторінка → компонент → ключ.

``UI.fields_gis.points.heading(count=6)`` підставляє значення у шаблон, а ``{@шлях.до.ключа}``
у JSON посилається на інший текст файлу. Посилання розгортаються під час завантаження, тому
помилка в них видна одразу, а неіснуючий ключ у тесті дає зрозумілий AttributeError.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_TEXTS_FILE = Path(__file__).with_name("ui_texts.json")
_REFERENCE = re.compile(r"\{@([\w.]+)\}")


class Text(str):
    """Текст інтерфейсу; виклик підставляє значення у плейсхолдери шаблону."""

    def __call__(self, **values: object) -> str:
        return self.format(**values)


class Section:
    """Вузол JSON із доступом до ключів через атрибути."""

    def __init__(self, path: str, content: dict) -> None:
        self._path = path
        self._content = content

    def __getattr__(self, key: str) -> Section | Text:
        path = f"{self._path}.{key}" if self._path else key
        if key not in self._content:
            raise AttributeError(f"У {_TEXTS_FILE.name} немає ключа «{path}»")
        value = self._content[key]
        return Section(path, value) if isinstance(value, dict) else Text(value)


def _lookup(root: dict, path: str) -> str:
    value = root
    for key in path.split("."):
        value = value[key]
    return _expand(root, value)


def _expand(root: dict, value: str) -> str:
    return _REFERENCE.sub(lambda match: _lookup(root, match[1]), value)


def _expand_all(root: dict, node: dict) -> dict:
    return {
        key: _expand_all(root, value) if isinstance(value, dict) else _expand(root, value)
        for key, value in node.items()
    }


def _load() -> Section:
    raw = json.loads(_TEXTS_FILE.read_text(encoding="utf-8"))
    return Section("", _expand_all(raw, raw))


UI = _load()
