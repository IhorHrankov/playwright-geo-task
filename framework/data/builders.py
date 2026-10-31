"""Test-data builders: valid monitoring points and import files (CSV / GeoJSON) in the app's formats."""

from __future__ import annotations

import csv
import io
import itertools
import json
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

from framework.data.fields import DEFAULT_ACTIVE_FIELD, FIELDS_BY_ID, Field
from framework.data.models import Coordinates, MonitoringPoint, PointType
from framework.utils.geo import to_mgrs

CSV_HEADER = ("ID", "Поле", "Тип", "Широта (Lat)", "Довгота (Lng)", "MGRS", "Опис", "Дата створення")
_counter = itertools.count(1)


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def make_point(
    field: Field = DEFAULT_ACTIVE_FIELD,
    *,
    u: float = 0.5,
    v: float = 0.5,
    point_type: PointType = PointType.SOIL_SAMPLE,
    description: str | None = None,
    created_at: datetime | None = None,
    point_id: str | None = None,
) -> MonitoringPoint:
    """A valid point located inside ``field`` (u/v pick the spot within the quad)."""
    lat, lng = field.interior_point(u, v)
    n = next(_counter)
    return MonitoringPoint(
        id=point_id or f"qa-point-{n}",
        fieldId=field.id,
        coordinates=Coordinates(lat=lat, lng=lng),
        mgrs=to_mgrs(lat, lng),
        type=point_type,
        description=description if description is not None else f"QA точка {n}",
        createdAt=iso(created_at or datetime.now(UTC) - timedelta(days=n)),
    )


def points_to_csv(rows: Iterable[Sequence[object]], header: Sequence[str] = CSV_HEADER, delimiter: str = ";") -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writerow(header)
    writer.writerows(rows)
    return "﻿" + buf.getvalue()


def point_csv_row(p: MonitoringPoint) -> list[object]:
    field = FIELDS_BY_ID.get(p.field_id)
    return [
        p.id,
        field.name if field else "",
        PointType(p.type).label,
        p.coordinates.lat,
        p.coordinates.lng,
        p.mgrs,
        p.description or "",
        p.created_at,
    ]


def points_to_geojson(points: Iterable[MonitoringPoint]) -> str:
    features = []
    for p in points:
        field = FIELDS_BY_ID.get(p.field_id)
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [p.coordinates.lng, p.coordinates.lat]},
                "properties": {
                    "id": p.id,
                    "fieldId": p.field_id,
                    "fieldName": field.name if field else "",
                    "type": PointType(p.type).value,
                    "typeLabel": PointType(p.type).label,
                    "mgrs": p.mgrs,
                    "description": p.description or "",
                    "createdAt": p.created_at,
                },
            }
        )
    return json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=2)


def write_file(directory: Path, name: str, content: str) -> Path:
    path = directory / name
    path.write_text(content, encoding="utf-8")
    return path


def read_exported_csv(path: Path) -> tuple[str, list[str], list[list[str]]]:
    """Return (raw_text, header, rows) of a CSV produced by the app."""
    raw = path.read_text(encoding="utf-8")
    rows = list(csv.reader(io.StringIO(raw.lstrip("﻿")), delimiter=";"))
    return raw, rows[0], rows[1:]
