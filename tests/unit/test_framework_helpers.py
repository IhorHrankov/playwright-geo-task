"""Offline checks of the test oracle and data builders (no browser, no network)."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import pytest

from framework.data import datasets
from framework.data.builders import CSV_HEADER, make_point, point_csv_row, points_to_csv, points_to_geojson
from framework.data.fields import FIELDS
from framework.data.models import MonitoringPoint, PointFeatureCollection
from framework.utils.geo import is_valid_lat_lng, mgrs_close, point_in_polygon, polygon_area_ha, to_mgrs

pytestmark = pytest.mark.unit

TEST_DATA = Path(__file__).resolve().parents[2] / "test_data"

# Reference pairs taken from the application's own demo data (verified manually).
KNOWN_MGRS = [
    (50.437, 30.532, "36U UA 24744 90130"),
    (50.413, 30.492, "36U UA 21814 87557"),
    (50.435, 30.528, "36U UA 24452 89918"),
    (50.434, 30.501, "36U UA 22531 89870"),
    (50.418, 30.525, "36U UA 24176 88035"),
    (50.416, 30.498, "36U UA 22251 87877"),
    (50.41254, 30.50097, "36U UA 22449 87485"),
    (48.85, 2.35, "31U DQ 52314 10984"),
]


@pytest.mark.parametrize(("lat", "lng", "expected"), KNOWN_MGRS)
def test_to_mgrs_matches_reference(lat: float, lng: float, expected: str) -> None:
    assert to_mgrs(lat, lng) == expected


@pytest.mark.parametrize(("lat", "lng"), [(95, 30), (50, 200), (-85, 0)])
def test_to_mgrs_rejects_out_of_domain(lat: float, lng: float) -> None:
    with pytest.raises(ValueError, match="outside"):
        to_mgrs(lat, lng)


def test_mgrs_close_tolerates_one_metre() -> None:
    assert mgrs_close("36U UA 22449 87485", "36U UA 22450 87484")
    assert not mgrs_close("36U UA 22449 87485", "36U UA 22460 87485")
    assert not mgrs_close("FAKE MGRS", "36U UA 22449 87485")


@pytest.mark.parametrize("field", FIELDS, ids=lambda f: f.id)
def test_interior_points_are_inside_their_field(field) -> None:
    for u in (0.05, 0.5, 0.95):
        for v in (0.05, 0.5, 0.95):
            lat, lng = field.interior_point(u, v)
            assert point_in_polygon(lat, lng, field.corners)


def test_point_outside_is_detected() -> None:
    assert not point_in_polygon(48.0, 35.0, FIELDS[0].corners)
    assert not point_in_polygon(50.415, 30.495, FIELDS[1].corners)  # field-1 coordinates vs field-2


def test_polygon_area_differs_from_declared_area() -> None:
    """Evidence for BUG-08: geometry gives 144-193 ha while the app shows 41-85 ha."""
    areas = {f.id: round(polygon_area_ha(f.corners), 1) for f in FIELDS}
    assert areas == {"field-1": 176.1, "field-2": 149.2, "field-3": 192.6, "field-4": 143.7}


def test_coordinate_range_validation() -> None:
    assert is_valid_lat_lng(50.4, 30.5)
    assert not is_valid_lat_lng(95, 200)


def test_standard_dataset_is_consistent() -> None:
    points = datasets.standard_points()
    assert len({p.id for p in points}) == len(points)
    assert len({p.created_at for p in points}) == len(points), "dates must differ for sort checks"
    for p in points:
        field = next(f for f in FIELDS if f.id == p.field_id)
        assert point_in_polygon(p.coordinates.lat, p.coordinates.lng, field.corners)
        assert p.mgrs == to_mgrs(p.coordinates.lat, p.coordinates.lng)


def test_geojson_builder_produces_contract_valid_file() -> None:
    content = points_to_geojson([make_point(f) for f in FIELDS])
    collection = PointFeatureCollection.model_validate(json.loads(content))
    assert len(collection.features) == len(FIELDS)


def test_csv_builder_matches_app_export_format() -> None:
    content = points_to_csv([point_csv_row(make_point(description='з "лапками"; і ;'))])
    assert content.startswith("﻿")
    rows = list(csv.reader(io.StringIO(content.lstrip("﻿")), delimiter=";"))
    assert tuple(rows[0]) == CSV_HEADER
    assert rows[1][6] == 'з "лапками"; і ;'


def test_initial_state_fixture_is_valid() -> None:
    raw = json.loads((TEST_DATA / "state" / "initial_localstorage_demo.json").read_text(encoding="utf-8"))
    points = [MonitoringPoint.model_validate(p) for p in raw]
    assert len(points) == 6
    for p in points:
        assert p.mgrs == to_mgrs(p.coordinates.lat, p.coordinates.lng)


@pytest.mark.parametrize("path", sorted((TEST_DATA / "import").glob("*")), ids=lambda p: p.name)
def test_import_fixtures_are_readable(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".geojson":
        assert json.loads(text)["type"] == "FeatureCollection"
    else:
        header = next(csv.reader(io.StringIO(text.lstrip("﻿")), delimiter=";"))
        assert tuple(header) == CSV_HEADER
