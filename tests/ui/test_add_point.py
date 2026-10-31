"""Додавання моніторингових точок кліком по карті (TC-01, TC-02, TC-03)."""

import re

import pytest
from playwright.sync_api import expect

from framework.data.fields import FIELD_1, FIELD_3
from framework.data.models import PointType
from framework.data.test_data import DESCRIPTION_250_CHARS, DESCRIPTION_251_CHARS
from framework.data.ui_texts import UI
from framework.pages import FieldsGisPage
from framework.storage import StoredPoints

pytestmark = [pytest.mark.ui, pytest.mark.regression]

FIELD_1_CENTRE = re.compile(r"^50\.41\d{3}, 30\.49\d{3}$")  # центр Поля №1 ≈ 50.416, 30.496
MGRS_FORMAT = re.compile(r"^36U UA \d{5} \d{5}$")


def test_click_inside_active_field_opens_modal_with_coordinates(gis_page: FieldsGisPage) -> None:
    gis_page.open_add_point_modal(FIELD_1)

    expect(gis_page.add_point_modal.coordinates_text).to_have_text(FIELD_1_CENTRE)
    expect(gis_page.add_point_modal.mgrs_text).to_have_text(MGRS_FORMAT)


def test_modal_mgrs_corresponds_to_shown_coordinates(gis_page: FieldsGisPage) -> None:
    gis_page.open_add_point_modal(FIELD_1)

    assert gis_page.add_point_modal.shows_mgrs_of_shown_coordinates()


def test_modal_offers_all_point_types_with_soil_sample_selected(gis_page: FieldsGisPage) -> None:
    gis_page.open_add_point_modal(FIELD_1)

    expect(gis_page.add_point_modal.type_options).to_have_text(
        [
            UI.fields_gis.point_types.soil_sample,
            UI.fields_gis.point_types.pests,
            UI.fields_gis.point_types.plant_disease,
            UI.fields_gis.point_types.other,
        ]
    )
    expect(gis_page.add_point_modal.type_select).to_have_value("SOIL_SAMPLE")


@pytest.mark.smoke
def test_saved_point_is_listed_first_with_its_details(gis_page: FieldsGisPage) -> None:
    gis_page.add_point(FIELD_1, PointType.PESTS, UI.fields_gis.add_point.inputs.pests_description)

    expect(gis_page.add_point_modal.root).to_be_hidden()
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=6))
    expect(gis_page.points.first_card.description).to_have_text(
        UI.fields_gis.add_point.inputs.pests_description
    )
    expect(gis_page.points.first_card.type_badge).to_have_text(UI.fields_gis.point_types.pests)
    expect(gis_page.points.first_card.field_name).to_have_text(UI.fields_gis.points.field_1_caption)
    expect(gis_page.points.first_card.mgrs).to_have_text(MGRS_FORMAT)


def test_saved_point_increments_field_counter(gis_page: FieldsGisPage) -> None:
    gis_page.add_point(FIELD_3, PointType.OTHER)

    expect(gis_page.fields.card(FIELD_3).points_badge).to_have_text("2")


def test_saved_point_appears_on_map(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.add_point(FIELD_1, PointType.SOIL_SAMPLE)

    expect(empty_gis_page.map.markers).to_have_count(1)


def test_saved_point_is_stored_in_its_field(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.add_point(
        FIELD_3, PointType.PLANT_DISEASE, UI.fields_gis.add_point.inputs.stored_description
    )
    expect(empty_gis_page.points.cards).to_have_count(1)

    stored = StoredPoints(empty_gis_page.page).newest()

    assert stored.field_id == "field-3"
    assert stored.type == "PLANT_DISEASE"
    assert stored.description == UI.fields_gis.add_point.inputs.stored_description


def test_saved_point_survives_page_reload(gis_page: FieldsGisPage) -> None:
    gis_page.add_point(FIELD_1, PointType.OTHER, UI.fields_gis.add_point.inputs.reloaded_description)
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=6))

    gis_page.reload()

    expect(gis_page.points.card(UI.fields_gis.add_point.inputs.reloaded_description).root).to_be_visible()


def test_whitespace_only_description_is_not_saved(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.add_point(FIELD_1, PointType.OTHER, "   ")
    expect(empty_gis_page.points.cards).to_have_count(1)

    stored = StoredPoints(empty_gis_page.page).newest()

    assert stored.description is None


def test_click_outside_active_field_shows_error_instead_of_modal(gis_page: FieldsGisPage) -> None:
    gis_page.map.click_outside_fields(FIELD_1)

    expect(gis_page.toast.root).to_have_text(UI.fields_gis.add_point.point_outside_field_1)
    expect(gis_page.add_point_modal.root).to_be_hidden()


def test_cancel_button_closes_modal_without_saving(gis_page: FieldsGisPage) -> None:
    gis_page.open_add_point_modal(FIELD_1)

    gis_page.add_point_modal.cancel()

    expect(gis_page.add_point_modal.root).to_be_hidden()
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=5))


def test_close_icon_closes_modal_without_saving(gis_page: FieldsGisPage) -> None:
    gis_page.open_add_point_modal(FIELD_1)

    gis_page.add_point_modal.close()

    expect(gis_page.add_point_modal.root).to_be_hidden()
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=5))


def test_escape_closes_modal_without_saving(gis_page: FieldsGisPage) -> None:
    gis_page.open_add_point_modal(FIELD_1)

    gis_page.add_point_modal.press_escape()

    expect(gis_page.add_point_modal.root).to_be_hidden()
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=5))


def test_description_of_250_characters_is_accepted(gis_page: FieldsGisPage) -> None:
    gis_page.add_point(FIELD_1, PointType.OTHER, DESCRIPTION_250_CHARS)

    expect(gis_page.add_point_modal.root).to_be_hidden()
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=6))


def test_description_of_251_characters_is_rejected(gis_page: FieldsGisPage) -> None:
    gis_page.add_point(FIELD_1, PointType.OTHER, DESCRIPTION_251_CHARS)

    expect(gis_page.add_point_modal.error_message).to_have_text(UI.fields_gis.add_point.description_too_long)
    expect(gis_page.add_point_modal.description_input).to_have_attribute("aria-invalid", "true")
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=5))
