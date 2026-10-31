"""Map: basemaps, markers, focus control, popups."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, Response, expect

from framework.data.builders import make_point
from framework.data.fields import DEFAULT_ACTIVE_FIELD, FIELDS
from framework.data.models import PointType
from framework.pages import FieldsGisPage
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_map_renders_fields_and_markers(gis_page: FieldsGisPage, standard_points) -> None:
    expect(gis_page.app_title).to_be_visible()
    expect(gis_page.map.field_polygons).to_have_count(len(FIELDS))
    expect(gis_page.map.markers).to_have_count(len(standard_points))
    expect(gis_page.map.hint).to_be_visible()


def test_streets_basemap_is_default(gis_page: FieldsGisPage) -> None:
    assert gis_page.map.active_basemap_is("streets")
    assert all("basemaps.cartocdn.com" in src for src in gis_page.map.tile_sources())


def test_switch_to_satellite_and_back(gis_page: FieldsGisPage) -> None:
    gis_page.map.select_basemap("satellite")
    gis_page.page.wait_for_function(
        "() => [...document.querySelectorAll('img.leaflet-tile')].some(i => i.src.includes('arcgisonline'))"
    )
    assert gis_page.map.active_basemap_is("satellite")

    gis_page.map.select_basemap("streets")
    gis_page.page.wait_for_function(
        "() => [...document.querySelectorAll('img.leaflet-tile')].some(i => i.src.includes('cartocdn'))"
    )
    assert gis_page.map.active_basemap_is("streets")


@known_bug("BUG-07")
def test_streets_basemap_tiles_are_real_map_images(page: Page, gis_page: FieldsGisPage) -> None:
    """CARTO returns one identical 'API KEY REQUIRED' PNG for every tile; real tiles differ."""
    responses: list[Response] = []
    page.on("response", lambda r: responses.append(r) if "cartocdn.com" in r.url else None)
    gis_page.map.zoom_out()
    gis_page.page.wait_for_load_state("networkidle")

    bodies = {r.body() for r in responses if r.ok}
    assert len(responses) > 1, "no streets tiles were requested"
    assert len(bodies) > 1, "every streets tile is the same image (placeholder)"


def test_focus_button_returns_to_active_field(gis_page: FieldsGisPage) -> None:
    before = gis_page.map.polygon(DEFAULT_ACTIVE_FIELD).bounding_box()
    gis_page.map.drag_by(-500, 300)
    assert gis_page.map.polygon(DEFAULT_ACTIVE_FIELD).bounding_box() != before

    gis_page.map.focus_active_field()

    after = gis_page.map.polygon(DEFAULT_ACTIVE_FIELD).bounding_box()
    assert after == pytest.approx(before, abs=2)


def test_marker_popup_shows_point_details(open_gis) -> None:
    point = make_point(DEFAULT_ACTIVE_FIELD, point_type=PointType.PLANT_DISEASE, description="Фузаріоз")
    gis = open_gis([point])

    gis.map.markers.first.click()

    expect(gis.map.popup).to_contain_text(PointType.PLANT_DISEASE.label)
    expect(gis.map.popup).to_contain_text(DEFAULT_ACTIVE_FIELD.name)
    expect(gis.map.popup).to_contain_text("Фузаріоз")
    expect(gis.map.popup).to_contain_text(point.mgrs)
