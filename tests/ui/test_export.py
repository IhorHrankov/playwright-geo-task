"""Export of monitoring points to GeoJSON and CSV (files are captured via Playwright downloads)."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pytest
from playwright.sync_api import expect

from framework.data.builders import CSV_HEADER, make_point
from framework.data.fields import FIELDS_BY_ID
from framework.data.models import PointFeatureCollection, PointType
from framework.pages import FieldsGisPage
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_export_geojson(gis_page: FieldsGisPage, standard_points, tmp_path: Path) -> None:
    file = gis_page.data_menu.export_geojson(tmp_path)

    # the app stamps the file name with the UTC date (toISOString)
    assert file.name == f"monitoring-points-{datetime.now(UTC).date().isoformat()}.geojson"
    collection = PointFeatureCollection.model_validate(json.loads(file.read_text(encoding="utf-8")))
    exported = {f.properties.id: f for f in collection.features}
    assert set(exported) == {p.id for p in standard_points}
    for p in standard_points:
        feature = exported[p.id]
        assert feature.geometry.coordinates == (p.coordinates.lng, p.coordinates.lat)  # GeoJSON order
        assert feature.properties.fieldId == p.field_id
        assert feature.properties.fieldName == FIELDS_BY_ID[p.field_id].name
        assert feature.properties.type == p.type
        assert feature.properties.typeLabel == PointType(p.type).label
        assert feature.properties.mgrs == p.mgrs
        assert feature.properties.description == p.description
        assert feature.properties.createdAt == p.created_at
    expect(gis_page.toast.root).to_have_text(f"Експортовано {len(standard_points)} точок у GeoJSON")


@pytest.mark.smoke
def test_export_csv(gis_page: FieldsGisPage, standard_points, tmp_path: Path) -> None:
    file = gis_page.data_menu.export_csv(tmp_path)
    raw = file.read_text(encoding="utf-8")

    assert file.suffix == ".csv"
    assert raw.startswith("﻿"), "UTF-8 BOM is required for Excel"
    lines = raw.lstrip("﻿").split("\r\n")
    assert lines[0] == ";".join(CSV_HEADER)
    assert len(lines) == len(standard_points) + 1
    first = standard_points[-1]  # list order = newest first
    assert lines[1].split(";")[0] == f'"{first.id}"'
    assert f'"{FIELDS_BY_ID[first.field_id].name}"' in lines[1]


def test_csv_escapes_quotes_and_delimiters(open_gis, tmp_path: Path) -> None:
    point = make_point(description='Опис з "лапками"; крапкою з комою')
    gis = open_gis([point])

    raw = gis.data_menu.export_csv(tmp_path).read_text(encoding="utf-8")

    assert '"Опис з ""лапками""; крапкою з комою"' in raw


def test_export_disabled_without_points(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.open()

    expect(empty_gis_page.data_menu.export_caption).to_have_text("Експорт даних (0)")
    expect(empty_gis_page.data_menu.export_geojson_item).to_be_disabled()
    expect(empty_gis_page.data_menu.export_csv_item).to_be_disabled()


@known_bug("BUG-09")
@pytest.mark.parametrize("payload", ["=HYPERLINK(\"http://example.com\",\"x\")", "+1+1", "-2+3", "@SUM(1,1)"])
def test_csv_neutralises_formulas(open_gis, tmp_path: Path, payload: str) -> None:
    gis = open_gis([make_point(description=payload)])

    _, row = gis.data_menu.export_csv(tmp_path).read_text(encoding="utf-8").split("\r\n")[:2]
    description_cell = row.split(";")[6].strip('"')

    assert not re.match(r"^[=+\-@]", description_cell), f"formula is exported as is: {description_cell}"


@known_bug("BUG-12")
def test_export_contains_all_points_even_when_list_is_filtered(
    gis_page: FieldsGisPage, standard_points, tmp_path: Path
) -> None:
    gis_page.points.search("черепашки")
    expect(gis_page.points.cards).to_have_count(1)

    collection = json.loads(gis_page.data_menu.export_geojson(tmp_path).read_text(encoding="utf-8"))

    assert len(collection["features"]) == len(standard_points)
