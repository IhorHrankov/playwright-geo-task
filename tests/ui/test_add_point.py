"""Adding monitoring points by clicking on the map."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from framework.data.fields import DEFAULT_ACTIVE_FIELD, FIELDS
from framework.data.models import POINT_TYPE_LABELS, PointType
from framework.pages import FieldsGisPage
from framework.storage import read_points
from framework.utils.geo import mgrs_close, point_in_polygon, to_mgrs

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
@pytest.mark.parametrize("field", [FIELDS[0], FIELDS[2]], ids=lambda f: f.id)
def test_add_point_inside_active_field(gis_page: FieldsGisPage, field) -> None:
    points_before = gis_page.points.counter()
    field_points_before = gis_page.fields.card(field).points_count()

    gis_page.open_add_point_modal(field)
    lat, lng = gis_page.add_point_modal.lat_lng()
    # The modal shows the clicked position and its MGRS (checked against an independent converter).
    modal_mgrs = gis_page.add_point_modal.mgrs_text.inner_text()
    assert mgrs_close(modal_mgrs, to_mgrs(lat, lng)), f"{modal_mgrs} != {to_mgrs(lat, lng)}"
    assert point_in_polygon(lat, lng, field.corners)

    gis_page.add_point_modal.add(PointType.PESTS, "QA: новий осередок шкідників")

    expect(gis_page.add_point_modal.root).to_be_hidden()
    expect(gis_page.points.heading).to_contain_text(f"({points_before + 1})")
    expect(gis_page.fields.card(field).points_badge).to_have_text(str(field_points_before + 1))
    newest = gis_page.points.card_at(0)  # default sort: newest first
    expect(newest.description).to_have_text("QA: новий осередок шкідників")
    expect(newest.type_badge).to_have_text(PointType.PESTS.label)
    expect(newest.mgrs).to_have_text(modal_mgrs)
    expect(newest.root).to_contain_text(field.name)

    stored = read_points(gis_page.page)[0]
    assert stored["fieldId"] == field.id
    assert stored["type"] == PointType.PESTS.value
    assert stored["coordinates"]["lat"] == pytest.approx(lat, abs=1e-5)
    assert stored["coordinates"]["lng"] == pytest.approx(lng, abs=1e-5)


def test_added_point_persists_after_reload(gis_page: FieldsGisPage) -> None:
    gis_page.open_add_point_modal(DEFAULT_ACTIVE_FIELD)
    gis_page.add_point_modal.add(PointType.OTHER, "QA: перевірка збереження")
    expect(gis_page.points.card_by_description("QA: перевірка збереження").root).to_be_visible()

    gis_page.reload()

    expect(gis_page.points.card_by_description("QA: перевірка збереження").root).to_be_visible()


def test_added_point_appears_on_map(empty_gis_page: FieldsGisPage) -> None:
    expect(empty_gis_page.map.markers).to_have_count(0)

    empty_gis_page.open_add_point_modal(DEFAULT_ACTIVE_FIELD)
    empty_gis_page.add_point_modal.add(PointType.SOIL_SAMPLE)

    expect(empty_gis_page.map.markers).to_have_count(1)


def test_click_outside_active_field_is_rejected(gis_page: FieldsGisPage) -> None:
    gis_page.map.click_outside_fields(DEFAULT_ACTIVE_FIELD)

    expect(gis_page.add_point_modal.root).to_be_hidden()
    expect(gis_page.toast.root).to_have_text(
        f'Точка повинна бути в межах обраного поля "{DEFAULT_ACTIVE_FIELD.name}".'
    )


def test_modal_offers_all_point_types_with_soil_sample_default(gis_page: FieldsGisPage) -> None:
    gis_page.open_add_point_modal(DEFAULT_ACTIVE_FIELD)

    options = gis_page.add_point_modal.type_select.locator("option")
    expect(options).to_have_text(list(POINT_TYPE_LABELS.values()))
    expect(gis_page.add_point_modal.type_select).to_have_value(PointType.SOIL_SAMPLE.value)


@pytest.mark.parametrize("close_via", ["cancel", "close_button", "escape"])
def test_closing_modal_does_not_create_point(gis_page: FieldsGisPage, close_via: str) -> None:
    before = gis_page.points.counter()
    gis_page.open_add_point_modal(DEFAULT_ACTIVE_FIELD)
    gis_page.add_point_modal.description_input.fill("не має зберегтися")

    modal = gis_page.add_point_modal
    {"cancel": modal.cancel_button.click, "close_button": modal.close_button.click,
     "escape": lambda: gis_page.page.keyboard.press("Escape")}[close_via]()

    expect(modal.root).to_be_hidden()
    expect(gis_page.points.heading).to_contain_text(f"({before})")
    assert len(read_points(gis_page.page)) == before


@pytest.mark.parametrize(("length", "accepted"), [(250, True), (251, False)])
def test_description_length_limit(gis_page: FieldsGisPage, length: int, accepted: bool) -> None:
    before = gis_page.points.counter()
    gis_page.open_add_point_modal(DEFAULT_ACTIVE_FIELD)

    gis_page.add_point_modal.add(PointType.OTHER, "щ" * length)

    if accepted:
        expect(gis_page.add_point_modal.root).to_be_hidden()
        expect(gis_page.points.heading).to_contain_text(f"({before + 1})")
    else:
        expect(gis_page.add_point_modal.error_message).to_have_text(
            "Опис не повинен перевищувати 250 символів"
        )
        expect(gis_page.add_point_modal.description_input).to_have_attribute("aria-invalid", "true")
        assert len(read_points(gis_page.page)) == before


def test_description_is_optional_and_trimmed(empty_gis_page: FieldsGisPage) -> None:
    empty_gis_page.open_add_point_modal(DEFAULT_ACTIVE_FIELD)
    empty_gis_page.add_point_modal.add(PointType.OTHER, "   ")

    stored = read_points(empty_gis_page.page)
    assert len(stored) == 1
    assert "description" not in stored[0]  # whitespace-only description is dropped
