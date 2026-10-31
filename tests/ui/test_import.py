"""Імпорт GeoJSON / CSV і демо-зразок (TC-05, TC-06). Вхідні файли: test_data/import/."""

from pathlib import Path

import pytest
from playwright.sync_api import expect

from framework.data.test_data import (
    COMMA_ENGLISH_HEADERS_CSV,
    DUPLICATE_IDS_CSV,
    FAKE_MGRS_CSV,
    FIELD_MISMATCH_CSV,
    HEADER_ONLY_CSV,
    INVALID_COORDINATES_CSV,
    INVALID_DATE_CSV,
    INVALID_JSON_GEOJSON,
    NO_POINT_FEATURES_GEOJSON,
    NON_NUMERIC_COORDINATES_CSV,
    NOT_FEATURE_COLLECTION_GEOJSON,
    ONE_POINT_GEOJSON,
    OUTSIDE_FIELDS_CSV,
    OUTSIDE_FIELDS_GEOJSON,
    STANDARD_DESCRIPTIONS_NEWEST_FIRST,
    VALID_POINTS_CSV,
    VALID_POINTS_GEOJSON,
    WITHOUT_LAT_LNG_CSV,
)
from framework.data.ui_texts import UI
from framework.pages import FieldsGisPage
from framework.storage import StoredPoints
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


# ---------------------------------------------------------------- валідні файли


@pytest.mark.smoke
@pytest.mark.parametrize("file", [VALID_POINTS_GEOJSON, VALID_POINTS_CSV], ids=["geojson", "csv"])
def test_valid_file_is_imported(empty_gis_page: FieldsGisPage, file: Path) -> None:
    empty_gis_page.data_menu.import_file(file)

    expect(empty_gis_page.toast.root).to_contain_text(UI.fields_gis.data_menu.import_success_start(count=4))
    expect(empty_gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=4))
    expect(empty_gis_page.map.markers).to_have_count(4)


@pytest.mark.parametrize(
    ("file", "ids_in_file_order"),
    [
        (VALID_POINTS_GEOJSON, ["std-1", "std-2", "std-3", "std-4"]),
        (VALID_POINTS_CSV, ["std-4", "std-3", "std-2", "std-1"]),
    ],
    ids=["geojson", "csv"],
)
def test_imported_points_keep_ids_fields_and_types(
    empty_gis_page: FieldsGisPage, file: Path, ids_in_file_order: list[str]
) -> None:
    empty_gis_page.data_menu.import_file(file)
    expect(empty_gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=4))

    stored = StoredPoints(empty_gis_page.page)

    assert stored.ids() == ids_in_file_order
    assert stored.by_id("std-3").field_id == "field-2"
    assert stored.by_id("std-3").type == "PLANT_DISEASE"


def test_csv_with_commas_and_english_headers_is_imported(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.import_file(COMMA_ENGLISH_HEADERS_CSV)
    expect(empty_gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=1))

    point = StoredPoints(empty_gis_page.page).by_id("qa-comma")

    assert point.field_id == "field-2"
    assert point.type == "PESTS"
    assert point.mgrs == "36U UA 23666 88391"  # у файлі немає MGRS, застосунок обчислює його


def test_demo_sample_is_loaded(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.load_demo()

    expect(empty_gis_page.toast.root).to_have_text(UI.fields_gis.data_menu.demo_loaded)
    expect(empty_gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=6))


def test_export_then_import_into_empty_storage_restores_points(
    gis_page: FieldsGisPage, tmp_path: Path
) -> None:
    exported = gis_page.data_menu.export_geojson(tmp_path)
    StoredPoints.clear(gis_page.page)
    gis_page.reload()

    gis_page.data_menu.import_file(exported)

    expect(gis_page.points.descriptions).to_have_text(STANDARD_DESCRIPTIONS_NEWEST_FIRST)


# ---------------------------------------------------------------- пошкоджені файли


@pytest.mark.parametrize(
    ("file", "error"),
    [
        (INVALID_JSON_GEOJSON, UI.fields_gis.data_menu.import_errors.invalid_json),
        (NOT_FEATURE_COLLECTION_GEOJSON, UI.fields_gis.data_menu.import_errors.not_feature_collection),
        (NO_POINT_FEATURES_GEOJSON, UI.fields_gis.data_menu.import_errors.no_point_features),
        (HEADER_ONLY_CSV, UI.fields_gis.data_menu.import_errors.csv_header_only),
        (WITHOUT_LAT_LNG_CSV, UI.fields_gis.data_menu.import_errors.csv_no_lat_lng),
        (NON_NUMERIC_COORDINATES_CSV, UI.fields_gis.data_menu.import_errors.csv_no_valid_rows),
    ],
    ids=[
        "invalid-json",
        "not-feature-collection",
        "no-point-features",
        "csv-header-only",
        "csv-without-lat-lng",
        "csv-non-numeric",
    ],
)
def test_malformed_file_is_rejected_with_message(gis_page: FieldsGisPage, file: Path, error: str) -> None:
    gis_page.data_menu.import_file(file)

    expect(gis_page.toast.root).to_have_text(error)
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=5))


# ---------------------------------------------------------------- невалідні дані (відомі дефекти)


@known_bug("BUG-01")
@pytest.mark.parametrize(
    "file",
    [OUTSIDE_FIELDS_CSV, OUTSIDE_FIELDS_GEOJSON, FIELD_MISMATCH_CSV],
    ids=["csv-outside-all-fields", "geojson-in-paris", "csv-wrong-field"],
)
def test_point_outside_its_field_is_not_imported(empty_gis_page: FieldsGisPage, file: Path) -> None:
    empty_gis_page.data_menu.import_file(file)
    expect(empty_gis_page.toast.root).to_be_visible()

    assert StoredPoints(empty_gis_page.page).outside_their_field() == []


@known_bug("BUG-02")
def test_out_of_range_coordinates_are_not_imported(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.import_file(INVALID_COORDINATES_CSV)
    expect(empty_gis_page.toast.root).to_be_visible()

    assert StoredPoints(empty_gis_page.page).with_invalid_coordinates() == []


@known_bug("BUG-03")
def test_duplicate_ids_in_file_are_made_unique(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.import_file(DUPLICATE_IDS_CSV)
    expect(empty_gis_page.toast.root).to_be_visible()

    assert StoredPoints(empty_gis_page.page).duplicate_ids() == []


@known_bug("BUG-03")
def test_deleting_one_of_duplicated_points_keeps_the_other(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.import_file(DUPLICATE_IDS_CSV)
    expect(empty_gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=2))

    empty_gis_page.points.card(UI.fields_gis.data_menu.duplicate_point_description).delete()

    expect(empty_gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=1), timeout=1_000)


@known_bug("BUG-04")
def test_invalid_creation_date_is_not_imported(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.import_file(INVALID_DATE_CSV)

    expect(empty_gis_page.points.first_card.created_at).not_to_have_text("not-a-date", timeout=1_000)


@known_bug("BUG-05")
def test_imported_mgrs_is_recalculated_from_coordinates(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.import_file(FAKE_MGRS_CSV)

    expect(empty_gis_page.points.first_card.mgrs).to_have_text("36U UA 22034 87773", timeout=1_000)


@known_bug("BUG-06")
def test_reimporting_exported_file_does_not_duplicate_points(gis_page: FieldsGisPage, tmp_path: Path) -> None:
    exported = gis_page.data_menu.export_csv(tmp_path)
    gis_page.toast.close()

    gis_page.data_menu.import_file(exported)
    expect(gis_page.toast.root).to_be_visible()  # імпорт завершено

    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=5), timeout=1_000)


@known_bug("BUG-06")
def test_loading_demo_twice_does_not_duplicate_points(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.load_demo()
    expect(empty_gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=6))
    empty_gis_page.toast.close()

    empty_gis_page.data_menu.load_demo()
    expect(empty_gis_page.toast.root).to_be_visible()  # завантаження завершено

    expect(empty_gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=6), timeout=1_000)


@known_bug("BUG-13")
def test_import_toast_uses_singular_for_one_point(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.import_file(ONE_POINT_GEOJSON)

    expect(empty_gis_page.toast.root).to_have_text(
        UI.fields_gis.data_menu.import_success_one_point(file="one_point.geojson")
    )
