"""Експорт у GeoJSON і CSV. Завантаження порівнюються з еталонами в test_data/expected/."""

import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

from framework.data.test_data import (
    EXPECTED_STANDARD_CSV,
    EXPECTED_STANDARD_GEOJSON,
    POINT_WITH_FORMULA,
    POINT_WITH_QUOTES,
)
from framework.data.ui_texts import UI
from framework.files import read_json, read_text
from framework.pages import FieldsGisPage
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]

EXPORT_FILE_NAME = re.compile(r"^monitoring-points-\d{4}-\d{2}-\d{2}\.(geojson|csv)$")


@pytest.mark.smoke
def test_geojson_export_matches_expected_file(gis_page: FieldsGisPage, tmp_path: Path) -> None:
    exported = gis_page.data_menu.export_geojson(tmp_path)

    assert read_json(exported) == read_json(EXPECTED_STANDARD_GEOJSON)


@pytest.mark.smoke
def test_csv_export_matches_expected_file(gis_page: FieldsGisPage, tmp_path: Path) -> None:
    exported = gis_page.data_menu.export_csv(tmp_path)

    assert read_text(exported) == read_text(EXPECTED_STANDARD_CSV)


def test_export_file_names_contain_date(gis_page: FieldsGisPage, tmp_path: Path) -> None:
    geojson = gis_page.data_menu.export_geojson(tmp_path)
    csv = gis_page.data_menu.export_csv(tmp_path)

    assert EXPORT_FILE_NAME.match(geojson.name)
    assert EXPORT_FILE_NAME.match(csv.name)


def test_export_shows_confirmation(gis_page: FieldsGisPage, tmp_path: Path) -> None:
    gis_page.data_menu.export_geojson(tmp_path)

    expect(gis_page.toast.root).to_have_text(UI.fields_gis.data_menu.exported_5_to_geojson)


def test_csv_export_escapes_quotes_and_semicolons(open_gis_with, tmp_path: Path) -> None:
    gis = open_gis_with([POINT_WITH_QUOTES])

    exported = gis.data_menu.export_csv(tmp_path)

    assert UI.fields_gis.data_menu.csv_escaped_description in read_text(exported)


def test_export_is_disabled_without_points(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.data_menu.open()

    expect(empty_gis_page.data_menu.export_caption).to_have_text(
        UI.fields_gis.data_menu.export_caption(count=0)
    )
    expect(empty_gis_page.data_menu.export_geojson_item).to_be_disabled()
    expect(empty_gis_page.data_menu.export_csv_item).to_be_disabled()


@known_bug("BUG-09")
def test_csv_export_neutralises_spreadsheet_formulas(open_gis_with, tmp_path: Path) -> None:
    gis = open_gis_with([POINT_WITH_FORMULA])

    exported = gis.data_menu.export_csv(tmp_path)

    assert '"=HYPERLINK(' not in read_text(exported)


@known_bug("BUG-12")
def test_export_contains_all_points_even_when_list_is_filtered(
    gis_page: FieldsGisPage, tmp_path: Path
) -> None:
    gis_page.points.search(UI.fields_gis.points.search.by_description)

    exported = gis_page.data_menu.export_geojson(tmp_path)

    assert read_json(exported) == read_json(EXPECTED_STANDARD_GEOJSON)
