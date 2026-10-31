"""Monitoring points as data: seeding localStorage and domain checks over a set of points.

Checks answer domain questions ("which points lie outside their field?") and return the
offending ids, so a test asserts ``== []`` instead of looping over raw records.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from datetime import datetime

from playwright.sync_api import BrowserContext, Page

from framework.data.fields import FIELDS_BY_ID
from framework.data.models import POINT_TYPE_LABELS, STORAGE_KEY, MonitoringPoint, PointType
from framework.utils.geo import is_valid_lat_lng, point_in_polygon, to_mgrs

# Seeds once per tab: sessionStorage survives reloads, so a reload keeps what the app saved.
_SEED_SCRIPT = """
(([key, value]) => {
  if (!window.sessionStorage.getItem('__qa_seeded')) {
    window.localStorage.setItem(key, value);
    window.sessionStorage.setItem('__qa_seeded', '1');
  }
})(%s);
"""


def seed_points(context: BrowserContext, points: Iterable[MonitoringPoint]) -> None:
    """Must be called before the first navigation of the page under test."""
    payload = json.dumps([p.to_storage() for p in points], ensure_ascii=False)
    context.add_init_script(_SEED_SCRIPT % json.dumps([STORAGE_KEY, payload], ensure_ascii=False))


class PointRecords:
    """A set of points in the app's storage shape (``id, fieldId, coordinates{lat,lng}, mgrs, type, ...``)."""

    def __init__(self, records: list[dict]) -> None:
        self.records = records

    @classmethod
    def from_geojson(cls, collection: dict) -> PointRecords:
        return cls([
            {
                **feature["properties"],
                "coordinates": {"lat": feature["geometry"]["coordinates"][1],
                                "lng": feature["geometry"]["coordinates"][0]},
            }
            for feature in collection["features"]
        ])

    # --- plain views ---
    def ids(self) -> list[str]:
        return [p["id"] for p in self.records]

    def newest(self) -> MonitoringPoint:
        return MonitoringPoint.model_validate(self.records[0])

    def by_id(self, point_id: str) -> MonitoringPoint:
        return MonitoringPoint.model_validate(next(p for p in self.records if p["id"] == point_id))

    # --- integrity checks: each returns offending ids, [] means "all good" ---
    def outside_their_field(self) -> list[str]:
        return [p["id"] for p in self.records if not _inside_own_field(p)]

    def with_invalid_coordinates(self) -> list[str]:
        return [p["id"] for p in self.records
                if not is_valid_lat_lng(p["coordinates"]["lat"], p["coordinates"]["lng"])]

    def with_wrong_mgrs(self) -> list[str]:
        return [p["id"] for p in self.records if p["mgrs"] != _expected_mgrs(p)]

    def with_wrong_field_name(self) -> list[str]:
        return [p["id"] for p in self.records
                if p["fieldId"] not in FIELDS_BY_ID or p.get("fieldName") != FIELDS_BY_ID[p["fieldId"]].name]

    def with_wrong_type_label(self) -> list[str]:
        return [p["id"] for p in self.records
                if p.get("typeLabel") != POINT_TYPE_LABELS.get(PointType(p["type"]))]

    def created_in_future_or_invalid(self) -> list[str]:
        return [p["id"] for p in self.records if not _is_past_iso_datetime(p["createdAt"])]

    def duplicate_ids(self) -> list[str]:
        return [point_id for point_id, n in Counter(self.ids()).items() if n > 1]


class StoredPoints(PointRecords):
    """Snapshot of the app's localStorage at the moment of the call."""

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


def _expected_mgrs(point: dict) -> str | None:
    try:
        return to_mgrs(point["coordinates"]["lat"], point["coordinates"]["lng"])
    except ValueError:
        return None


def _is_past_iso_datetime(value: str) -> bool:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")) < datetime.now().astimezone()
    except ValueError:
        return False
