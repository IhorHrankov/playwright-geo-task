"""Map: polygons, markers, basemaps, focus control, popup."""

import pytest
from playwright.sync_api import expect

from framework.data.fields import FIELD_1
from framework.data.test_data import DISEASE_WITH_DETAILS
from framework.pages import FieldsGisPage
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_map_shows_four_fields_and_five_markers(gis_page: FieldsGisPage) -> None:
    expect(gis_page.map.field_polygons).to_have_count(4)
    expect(gis_page.map.markers).to_have_count(5)
    expect(gis_page.map.hint).to_be_visible()


def test_streets_basemap_is_loaded_by_default(gis_page: FieldsGisPage) -> None:
    expect(gis_page.map.tiles_from("basemaps.cartocdn.com").first).to_be_visible()
    expect(gis_page.map.tiles_from("arcgisonline.com")).to_have_count(0)


def test_satellite_basemap_loads_satellite_tiles(gis_page: FieldsGisPage) -> None:
    gis_page.map.select_basemap("satellite")

    expect(gis_page.map.tiles_from("arcgisonline.com").first).to_be_visible()


def test_switching_back_to_streets_loads_street_tiles(gis_page: FieldsGisPage) -> None:
    gis_page.map.select_basemap("satellite")

    gis_page.map.select_basemap("streets")

    expect(gis_page.map.tiles_from("basemaps.cartocdn.com").first).to_be_visible()


def test_focus_button_returns_map_to_active_field(gis_page: FieldsGisPage) -> None:
    initial_position = gis_page.map.polygon_position(FIELD_1)
    gis_page.map.drag_by(-500, 300)

    gis_page.map.focus_active_field()

    assert gis_page.map.polygon_position(FIELD_1) == pytest.approx(initial_position, abs=2)


def test_marker_popup_shows_point_details(open_gis_with) -> None:
    gis = open_gis_with([DISEASE_WITH_DETAILS])

    gis.map.markers.first.click()

    expect(gis.map.popup).to_contain_text("Хвороби рослин")
    expect(gis.map.popup).to_contain_text("Поле №1 - Озима пшениця")
    expect(gis.map.popup).to_contain_text("Фузаріоз колосу")
    expect(gis.map.popup).to_contain_text("36U UA 21639 87558")


@known_bug("BUG-07")
def test_streets_basemap_does_not_show_api_key_placeholder(gis_page: FieldsGisPage) -> None:
    gis_page.map.zoom_out()

    assert gis_page.map.loaded_street_tiles_are_distinct()
