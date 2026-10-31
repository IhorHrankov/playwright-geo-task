"""Моніторингові точки як дані: засівання localStorage і доменні перевірки набору точок.

Перевірки відповідають на доменні питання («які точки лежать поза своїм полем?») і повертають
id порушників, тож тест перевіряє ``== []``, а не перебирає сирі записи в циклі.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable

from playwright.sync_api import BrowserContext, Page

from framework.data.fields import FIELDS_BY_ID
from framework.data.models import STORAGE_KEY, MonitoringPoint
from framework.utils.geo import is_valid_lat_lng, point_in_polygon

# Засіває один раз на вкладку: sessionStorage переживає reload, тож reload не стирає збережене застосунком.
_SEED_SCRIPT = """
(([key, value]) => {
  if (!window.sessionStorage.getItem('__qa_seeded')) {
    window.localStorage.setItem(key, value);
    window.sessionStorage.setItem('__qa_seeded', '1');
  }
})(%s);
"""


def seed_points(context: BrowserContext, points: Iterable[MonitoringPoint]) -> None:
    """Викликати до першої навігації сторінки, що тестується."""
    payload = json.dumps([p.to_storage() for p in points], ensure_ascii=False)
    context.add_init_script(_SEED_SCRIPT % json.dumps([STORAGE_KEY, payload], ensure_ascii=False))


class PointRecords:
    """Набір точок у форматі сховища застосунку (``id, fieldId, coordinates{lat,lng}, mgrs, type, ...``)."""

    def __init__(self, records: list[dict]) -> None:
        self.records = records

    # --- прості подання ---
    def ids(self) -> list[str]:
        return [p["id"] for p in self.records]

    def newest(self) -> MonitoringPoint:
        return MonitoringPoint.model_validate(self.records[0])

    def by_id(self, point_id: str) -> MonitoringPoint:
        return MonitoringPoint.model_validate(next(p for p in self.records if p["id"] == point_id))

    # --- перевірки цілісності: кожна повертає id порушників, [] означає «усе добре» ---
    def outside_their_field(self) -> list[str]:
        return [p["id"] for p in self.records if not _inside_own_field(p)]

    def with_invalid_coordinates(self) -> list[str]:
        return [
            p["id"]
            for p in self.records
            if not is_valid_lat_lng(p["coordinates"]["lat"], p["coordinates"]["lng"])
        ]

    def duplicate_ids(self) -> list[str]:
        return [point_id for point_id, n in Counter(self.ids()).items() if n > 1]


class StoredPoints(PointRecords):
    """Знімок localStorage застосунку на момент виклику."""

    def __init__(self, page: Page) -> None:
        raw = page.evaluate("key => window.localStorage.getItem(key)", STORAGE_KEY)
        super().__init__(json.loads(raw) if raw else [])

    @staticmethod
    def clear(page: Page) -> None:
        page.evaluate("key => window.localStorage.setItem(key, '[]')", STORAGE_KEY)


def _inside_own_field(point: dict) -> bool:
    field = FIELDS_BY_ID.get(point["fieldId"])
    lat, lng = point["coordinates"]["lat"], point["coordinates"]["lng"]
    return bool(field) and point_in_polygon(lat, lng, field.corners)
