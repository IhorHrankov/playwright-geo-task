"""Поля: список, вибір за замовчуванням, перемикання активного поля."""

import pytest
from playwright.sync_api import expect

from framework.data.fields import FIELD_1, FIELD_2, FIELD_3, FIELD_4
from framework.data.ui_texts import UI
from framework.pages import FieldsGisPage
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_fields_list_shows_four_fields(gis_page: FieldsGisPage) -> None:
    expect(gis_page.fields.heading).to_have_text(UI.fields_gis.fields.heading(count=4))
    expect(gis_page.fields.titles).to_have_text(
        [
            UI.fields_gis.fields.field_1.name,
            UI.fields_gis.fields.field_2.name,
            UI.fields_gis.fields.field_3.name,
            UI.fields_gis.fields.field_4.name,
        ]
    )


@pytest.mark.parametrize(
    ("field", "area", "crop"),
    [
        (FIELD_1, UI.fields_gis.fields.field_1.area, UI.fields_gis.fields.field_1.crop),
        (FIELD_2, UI.fields_gis.fields.field_2.area, UI.fields_gis.fields.field_2.crop),
        (FIELD_3, UI.fields_gis.fields.field_3.area, UI.fields_gis.fields.field_3.crop),
        (FIELD_4, UI.fields_gis.fields.field_4.area, UI.fields_gis.fields.field_4.crop),
    ],
    ids=["field-1", "field-2", "field-3", "field-4"],
)
def test_field_card_shows_area_and_crop(gis_page: FieldsGisPage, field, area: str, crop: str) -> None:
    card = gis_page.fields.card(field)

    expect(card.root).to_contain_text(area)
    expect(card.root).to_contain_text(crop)


@pytest.mark.parametrize(
    ("field", "points_count"),
    [(FIELD_1, "2"), (FIELD_2, "1"), (FIELD_3, "1"), (FIELD_4, "1")],
    ids=["field-1", "field-2", "field-3", "field-4"],
)
def test_field_card_counts_its_points(gis_page: FieldsGisPage, field, points_count: str) -> None:
    expect(gis_page.fields.card(field).points_badge).to_have_text(points_count)


def test_first_field_is_active_by_default(gis_page: FieldsGisPage) -> None:
    expect(gis_page.fields.active_cards).to_have_count(1)
    expect(gis_page.fields.card(FIELD_1).root).to_have_attribute("aria-pressed", "true")


def test_selecting_field_in_list_makes_it_the_only_active_one(gis_page: FieldsGisPage) -> None:
    gis_page.select_field(FIELD_3)

    expect(gis_page.fields.card(FIELD_3).root).to_have_attribute("aria-pressed", "true")
    expect(gis_page.fields.card(FIELD_1).root).to_have_attribute("aria-pressed", "false")
    expect(gis_page.fields.active_cards).to_have_count(1)


def test_clicking_inactive_field_on_map_selects_it_without_adding_point(gis_page: FieldsGisPage) -> None:
    gis_page.map.zoom_out(times=2)

    gis_page.map.click_inside(FIELD_4)

    expect(gis_page.fields.card(FIELD_4).root).to_have_attribute("aria-pressed", "true")
    expect(gis_page.add_point_modal.root).to_be_hidden()


def test_hovering_field_shows_tooltip_with_name_area_and_crop(gis_page: FieldsGisPage) -> None:
    gis_page.map.polygon(FIELD_1).hover()

    expect(gis_page.page.locator(".leaflet-tooltip")).to_contain_text(UI.fields_gis.fields.field_1.name)
    expect(gis_page.page.locator(".leaflet-tooltip")).to_contain_text(
        UI.fields_gis.fields.field_1.tooltip_details
    )


@known_bug("BUG-08")
@pytest.mark.parametrize(
    ("field", "area_by_geometry"),
    [
        (FIELD_1, UI.fields_gis.fields.field_1.area_by_geometry),
        (FIELD_2, UI.fields_gis.fields.field_2.area_by_geometry),
        (FIELD_3, UI.fields_gis.fields.field_3.area_by_geometry),
        (FIELD_4, UI.fields_gis.fields.field_4.area_by_geometry),
    ],
    ids=["field-1", "field-2", "field-3", "field-4"],
)
def test_field_area_matches_polygon_geometry(gis_page: FieldsGisPage, field, area_by_geometry: str) -> None:
    expect(gis_page.fields.card(field).root).to_contain_text(area_by_geometry, timeout=1_000)
