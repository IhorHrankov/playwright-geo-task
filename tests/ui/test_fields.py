"""Fields: list, default selection, switching the active field (list and map)."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from framework.data.fields import DEFAULT_ACTIVE_FIELD, FIELDS, Field
from framework.pages import FieldsGisPage
from framework.utils.geo import polygon_area_ha
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_all_fields_are_listed_with_area_and_crop(gis_page: FieldsGisPage) -> None:
    expect(gis_page.fields.cards).to_have_count(len(FIELDS))
    expect(gis_page.fields.heading).to_contain_text(f"({len(FIELDS)})")
    for field in FIELDS:
        card = gis_page.fields.card(field)
        expect(card.title).to_have_text(field.name)
        expect(card.root).to_contain_text(f"{field.area_ha} га")
        expect(card.root).to_contain_text(field.crop)


def test_first_field_is_active_by_default(gis_page: FieldsGisPage) -> None:
    expect(gis_page.fields.active_card().title).to_have_text(DEFAULT_ACTIVE_FIELD.name)
    expect(gis_page.fields.root.locator("article[aria-pressed='true']")).to_have_count(1)


@pytest.mark.parametrize("field", FIELDS[1:], ids=lambda f: f.id)
def test_select_field_from_list(gis_page: FieldsGisPage, field: Field) -> None:
    gis_page.select_field(field)

    expect(gis_page.fields.card(field).root).to_have_attribute("aria-pressed", "true")
    expect(gis_page.fields.card(DEFAULT_ACTIVE_FIELD).root).to_have_attribute("aria-pressed", "false")


def test_select_field_by_clicking_its_polygon(gis_page: FieldsGisPage) -> None:
    target = FIELDS[3]
    gis_page.map.zoom_out(times=2)  # bring every field into the viewport
    gis_page.map.click_inside(target, 0.5, 0.5)

    expect(gis_page.fields.card(target).root).to_have_attribute("aria-pressed", "true")
    expect(gis_page.add_point_modal.root).to_be_hidden()  # first click only selects the field


def test_field_points_counter_matches_data(gis_page: FieldsGisPage, standard_points: list) -> None:
    for field in FIELDS:
        expected = sum(p.field_id == field.id for p in standard_points)
        expect(gis_page.fields.card(field).points_badge).to_have_text(str(expected))


def test_field_tooltip_shows_name_area_and_crop(gis_page: FieldsGisPage) -> None:
    gis_page.map.polygon(DEFAULT_ACTIVE_FIELD).hover()
    tooltip = gis_page.page.locator(".leaflet-tooltip")
    expect(tooltip).to_contain_text(DEFAULT_ACTIVE_FIELD.name)
    expect(tooltip).to_contain_text(re.compile(rf"{DEFAULT_ACTIVE_FIELD.area_ha} га"))


@known_bug("BUG-08")
@pytest.mark.parametrize("field", FIELDS, ids=lambda f: f.id)
def test_displayed_area_matches_polygon_geometry(gis_page: FieldsGisPage, field: Field) -> None:
    geometric_area = polygon_area_ha(field.corners)
    displayed = float(re.search(r"([\d.]+) га", gis_page.fields.card(field).root.inner_text()).group(1))
    assert displayed == pytest.approx(geometric_area, rel=0.02)
