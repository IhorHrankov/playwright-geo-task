"""Import of GeoJSON / CSV files and the demo sample: happy paths, malformed files, data validation."""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import expect

from framework.components import PointCard
from framework.data.builders import (
    CSV_HEADER,
    make_point,
    point_csv_row,
    points_to_csv,
    points_to_geojson,
    write_file,
)
from framework.data.fields import FIELDS, FIELDS_BY_ID
from framework.data.models import PointType
from framework.pages import FieldsGisPage
from framework.storage import read_points
from framework.utils.geo import is_valid_lat_lng, point_in_polygon, to_mgrs
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]

TEST_DATA = Path(__file__).resolve().parents[2] / "test_data"


def _import(gis: FieldsGisPage, path: Path) -> None:
    gis.data_menu.import_file(path)
    expect(gis.toast.root).to_be_visible()


# ---------- happy paths ----------


@pytest.mark.smoke
@pytest.mark.parametrize("fmt", ["geojson", "csv"])
def test_import_valid_file(empty_gis_page: FieldsGisPage, tmp_path: Path, fmt: str) -> None:
    points = [make_point(FIELDS[i], point_type=t) for i, t in enumerate(PointType)]
    content = points_to_geojson(points) if fmt == "geojson" else points_to_csv(map(point_csv_row, points))
    file = write_file(tmp_path, f"valid.{fmt}", content)

    _import(empty_gis_page, file)

    expect(empty_gis_page.toast.root).to_contain_text(f'Успішно імпортовано {len(points)} точ')
    expect(empty_gis_page.toast.root).to_contain_text(f'"valid.{fmt}"')
    expect(empty_gis_page.points.cards).to_have_count(len(points))
    expect(empty_gis_page.map.markers).to_have_count(len(points))
    stored = {p["id"]: p for p in read_points(empty_gis_page.page)}
    for p in points:
        assert stored[p.id]["fieldId"] == p.field_id
        assert stored[p.id]["type"] == p.type


def test_import_csv_with_comma_delimiter_and_english_headers(empty_gis_page: FieldsGisPage, tmp_path: Path) -> None:
    p = make_point(FIELDS[1])
    content = points_to_csv(
        [[p.id, p.field_id, "pests", p.coordinates.lat, p.coordinates.lng, "", "comma file", p.created_at]],
        header=["id", "fieldId", "type", "lat", "lng", "mgrs", "description", "date"],
        delimiter=",",
    )
    _import(empty_gis_page, write_file(tmp_path, "comma.csv", content))

    expect(empty_gis_page.points.cards).to_have_count(1)
    stored = read_points(empty_gis_page.page)[0]
    assert stored["fieldId"] == FIELDS[1].id
    assert stored["type"] == PointType.PESTS.value
    assert stored["mgrs"] == to_mgrs(p.coordinates.lat, p.coordinates.lng)  # computed when absent


def test_load_demo_sample(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.load_demo()

    expect(empty_gis_page.toast.root).to_contain_text("Завантажено 6 точок з еталонного мок-файлу!")
    expect(empty_gis_page.points.cards).to_have_count(6)


def test_roundtrip_export_then_import_into_clean_storage(
    gis_page: FieldsGisPage, standard_points, tmp_path: Path
) -> None:
    exported = gis_page.data_menu.export_geojson(tmp_path)
    gis_page.page.evaluate("localStorage.setItem('agtech_monitoring_points_v1', '[]')")
    gis_page.reload()
    expect(gis_page.points.cards).to_have_count(0)

    _import(gis_page, exported)

    stored = {p["id"]: p for p in read_points(gis_page.page)}
    assert set(stored) == {p.id for p in standard_points}
    for p in standard_points:
        assert stored[p.id]["mgrs"] == p.mgrs
        assert stored[p.id]["createdAt"] == p.created_at


# ---------- malformed files ----------


@pytest.mark.parametrize(
    ("name", "content", "error"),
    [
        pytest.param("broken.geojson", '{"type": "FeatureCollection", "features": [',
                     "Помилка синтаксису JSON під час парсингу файлу.", id="invalid-json"),
        pytest.param("not-a-collection.geojson", '{"type": "Feature"}',
                     "Некоректний формат GeoJSON: очікується FeatureCollection з масивом features.",
                     id="not-feature-collection"),
        pytest.param("no-points.geojson",
                     '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":'
                     '{"type":"Polygon","coordinates":[]},"properties":{}}]}',
                     "У GeoJSON файлі не знайдено валідних точок моніторингу.", id="no-point-features"),
        pytest.param("header-only.csv", ";".join(CSV_HEADER),
                     "CSV файл повинен містити рядок заголовків та щонайменше один рядок даних.",
                     id="csv-header-only"),
        pytest.param("no-coords.csv", "id;type;description\r\na;Інше;x",
                     "У CSV не знайдено обов’язкових колонок широти (Lat) та довготи (Lng).",
                     id="csv-without-lat-lng"),
        pytest.param("bad-coords.csv", "lat;lng\r\nabc;def",
                     "У CSV файлі не знайдено валідних рядків з координатами.", id="csv-non-numeric"),
    ],
)
def test_malformed_file_is_rejected(
    gis_page: FieldsGisPage, standard_points, tmp_path: Path, name: str, content: str, error: str
) -> None:
    _import(gis_page, write_file(tmp_path, name, content))

    expect(gis_page.toast.root).to_have_text(error)
    expect(gis_page.points.cards).to_have_count(len(standard_points))


# ---------- data validation (documented defects) ----------


@known_bug("BUG-01")
@pytest.mark.parametrize(
    "file_name", ["outside_fields.csv", "outside_fields.geojson", "field_mismatch.csv"]
)
def test_points_outside_their_field_are_rejected(empty_gis_page: FieldsGisPage, file_name: str) -> None:
    _import(empty_gis_page, TEST_DATA / "import" / file_name)

    for p in read_points(empty_gis_page.page):
        field = FIELDS_BY_ID[p["fieldId"]]
        assert point_in_polygon(p["coordinates"]["lat"], p["coordinates"]["lng"], field.corners), (
            f"{p['id']} stored in {field.id} but lies outside it"
        )


@known_bug("BUG-02")
def test_out_of_range_coordinates_are_rejected(empty_gis_page: FieldsGisPage) -> None:
    _import(empty_gis_page, TEST_DATA / "import" / "invalid_coordinates.csv")

    assert all(is_valid_lat_lng(p["coordinates"]["lat"], p["coordinates"]["lng"])
               for p in read_points(empty_gis_page.page))


@known_bug("BUG-03")
def test_duplicate_ids_inside_file_are_made_unique(empty_gis_page: FieldsGisPage) -> None:
    _import(empty_gis_page, TEST_DATA / "import" / "duplicate_ids.csv")

    ids = [p["id"] for p in read_points(empty_gis_page.page)]
    assert len(ids) == len(set(ids)), f"duplicate ids stored: {ids}"


def test_duplicate_ids_corrupt_list_and_delete(empty_gis_page: FieldsGisPage) -> None:
    """Characterises the visible impact of BUG-03 (kept green on purpose: documents current behaviour)."""
    _import(empty_gis_page, TEST_DATA / "import" / "duplicate_ids.csv")
    expect(empty_gis_page.points.heading).to_contain_text("(2)")

    PointCard(empty_gis_page.points.cards.filter(has_text="QA dup B").first).delete()

    # Deleting ONE card removed BOTH points that share the id.
    assert read_points(empty_gis_page.page) == []


@known_bug("BUG-04")
def test_invalid_created_at_is_rejected(empty_gis_page: FieldsGisPage) -> None:
    _import(empty_gis_page, TEST_DATA / "import" / "invalid_date.csv")

    expect(empty_gis_page.points.cards.locator("time")).not_to_have_text("not-a-date")


@known_bug("BUG-05")
def test_imported_mgrs_is_recalculated(empty_gis_page: FieldsGisPage) -> None:
    _import(empty_gis_page, TEST_DATA / "import" / "fake_mgrs.csv")

    for p in read_points(empty_gis_page.page):
        assert p["mgrs"] == to_mgrs(p["coordinates"]["lat"], p["coordinates"]["lng"])


@known_bug("BUG-06")
def test_reimport_of_exported_file_does_not_duplicate(gis_page: FieldsGisPage, standard_points, tmp_path) -> None:
    exported = gis_page.data_menu.export_csv(tmp_path)

    _import(gis_page, exported)

    expect(gis_page.points.cards).to_have_count(len(standard_points))


@known_bug("BUG-06")
def test_loading_demo_twice_does_not_duplicate(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.load_demo()
    expect(empty_gis_page.points.cards).to_have_count(6)

    empty_gis_page.data_menu.load_demo()

    expect(empty_gis_page.points.cards).to_have_count(6)


@known_bug("BUG-13")
def test_toast_uses_correct_plural_for_one_point(empty_gis_page: FieldsGisPage, tmp_path: Path) -> None:
    file = write_file(tmp_path, "one.geojson", points_to_geojson([make_point()]))

    _import(empty_gis_page, file)

    expect(empty_gis_page.toast.root).to_have_text('Успішно імпортовано 1 точку з файлу "one.geojson"!')
