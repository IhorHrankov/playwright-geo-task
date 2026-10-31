"""Список точок: порядок, пошук, фільтр, видалення, скидання, «Показати на карті» (TC-04, TC-07, TC-08)."""

import pytest
from playwright.sync_api import expect

from framework.data.fields import FIELD_1, FIELD_2
from framework.data.models import PointType
from framework.data.test_data import (
    DISEASE_FIELD_2,
    OTHER_FIELD_3,
    PESTS_FIELD_1,
    PESTS_FIELD_4,
    SOIL_SAMPLE_FIELD_1,
    STANDARD_DESCRIPTIONS_NEWEST_FIRST,
    STANDARD_DESCRIPTIONS_OLDEST_FIRST,
)
from framework.data.ui_texts import UI
from framework.pages import FieldsGisPage
from framework.storage import StoredPoints
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


# ---------------------------------------------------------------- порядок


@pytest.mark.smoke
def test_list_shows_all_points_newest_first(gis_page: FieldsGisPage) -> None:
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=5))
    expect(gis_page.points.sort_button).to_have_text(UI.fields_gis.points.sort_newest)
    expect(gis_page.points.descriptions).to_have_text(STANDARD_DESCRIPTIONS_NEWEST_FIRST)


def test_sort_toggle_shows_oldest_first(gis_page: FieldsGisPage) -> None:
    gis_page.points.toggle_sort()

    expect(gis_page.points.sort_button).to_have_text(UI.fields_gis.points.sort_oldest)
    expect(gis_page.points.descriptions).to_have_text(STANDARD_DESCRIPTIONS_OLDEST_FIRST)


def test_second_sort_toggle_returns_newest_first(gis_page: FieldsGisPage) -> None:
    gis_page.points.toggle_sort()

    gis_page.points.toggle_sort()

    expect(gis_page.points.descriptions).to_have_text(STANDARD_DESCRIPTIONS_NEWEST_FIRST)


# ---------------------------------------------------------------- пошук


@pytest.mark.parametrize(
    ("query", "expected_descriptions"),
    [
        (UI.fields_gis.points.search.by_description, [PESTS_FIELD_1.description]),
        (UI.fields_gis.points.search.by_description_uppercase, [PESTS_FIELD_1.description]),
        (UI.fields_gis.points.search.with_surrounding_spaces, [DISEASE_FIELD_2.description]),
        (UI.fields_gis.points.search.by_field_crop, [DISEASE_FIELD_2.description]),
        ("36U UA 22882 89519", [OTHER_FIELD_3.description]),
        (
            UI.fields_gis.points.search.by_type_lowercase,
            [PESTS_FIELD_4.description, PESTS_FIELD_1.description],
        ),
    ],
    ids=["by-description", "case-insensitive", "trims-spaces", "by-field-name", "by-mgrs", "by-type-label"],
)
def test_search_finds_points(gis_page: FieldsGisPage, query: str, expected_descriptions: list[str]) -> None:
    gis_page.points.search(query)

    expect(gis_page.points.descriptions).to_have_text(expected_descriptions)


def test_search_without_matches_shows_empty_state(gis_page: FieldsGisPage) -> None:
    gis_page.points.search(UI.fields_gis.points.search.without_matches)

    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=0))
    expect(gis_page.points.empty_state).to_have_text(UI.fields_gis.points.no_points_found)


def test_reset_filters_button_clears_search(gis_page: FieldsGisPage) -> None:
    gis_page.points.search(UI.fields_gis.points.search.without_matches)

    gis_page.points.reset_filters_button.click()

    expect(gis_page.points.search_input).to_have_value("")
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=5))


# ---------------------------------------------------------------- фільтр за типом


@pytest.mark.parametrize(
    ("point_type", "expected_badges"),
    [
        (PointType.SOIL_SAMPLE, [UI.fields_gis.point_types.soil_sample]),
        (PointType.PESTS, [UI.fields_gis.point_types.pests, UI.fields_gis.point_types.pests]),
        (PointType.PLANT_DISEASE, [UI.fields_gis.point_types.plant_disease]),
        (PointType.OTHER, [UI.fields_gis.point_types.other]),
    ],
    ids=["soil-sample", "pests", "plant-disease", "other"],
)
def test_type_filter_keeps_only_that_type(
    gis_page: FieldsGisPage, point_type: PointType, expected_badges: list[str]
) -> None:
    gis_page.points.filter_by_type(point_type)

    expect(gis_page.points.type_filter(point_type)).to_have_attribute("aria-pressed", "true")
    expect(gis_page.points.type_badges).to_have_text(expected_badges)


def test_type_filter_and_search_are_combined(gis_page: FieldsGisPage) -> None:
    gis_page.points.filter_by_type(PointType.PESTS)

    gis_page.points.search(UI.fields_gis.points.search.combined_with_filter)

    expect(gis_page.points.descriptions).to_have_text([PESTS_FIELD_4.description])


@known_bug("BUG-11")
def test_type_filter_is_applied_to_map_markers(gis_page: FieldsGisPage) -> None:
    gis_page.points.filter_by_type(PointType.PLANT_DISEASE)

    expect(gis_page.map.markers).to_have_count(1, timeout=2_000)


# ---------------------------------------------------------------- видалення


def test_deleting_point_removes_it_from_list(gis_page: FieldsGisPage) -> None:
    gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).delete()

    expect(gis_page.toast.root).to_have_text(UI.fields_gis.points.point_deleted)
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=4))
    expect(gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).root).to_have_count(0)


def test_deleting_point_removes_its_marker_and_updates_field_counter(gis_page: FieldsGisPage) -> None:
    gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).delete()

    expect(gis_page.map.markers).to_have_count(4)
    expect(gis_page.fields.card(FIELD_1).points_badge).to_have_text("1")


def test_deleting_point_removes_it_from_storage(gis_page: FieldsGisPage) -> None:
    gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).delete()
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=4))

    assert StoredPoints(gis_page.page).ids() == ["std-2", "std-3", "std-4", "std-5"]


def test_deleting_point_from_map_popup(gis_page: FieldsGisPage) -> None:
    gis_page.map.markers.first.click()

    gis_page.map.popup.get_by_role("button", name=UI.fields_gis.points.delete_button).click()

    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=4))


@known_bug("BUG-14")
def test_deleting_point_offers_undo(gis_page: FieldsGisPage) -> None:
    gis_page.points.first_card.delete()

    expect(gis_page.toast.root.get_by_role("button", name=UI.fields_gis.points.undo_button)).to_be_visible(
        timeout=1_000
    )


# ---------------------------------------------------------------- скидання


def test_reset_data_restores_three_builtin_points(gis_page: FieldsGisPage) -> None:
    gis_page.points.reset_data()

    expect(gis_page.toast.root).to_have_text(UI.fields_gis.points.data_reset)
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=3))


def test_cancelled_reset_keeps_points(gis_page: FieldsGisPage) -> None:
    gis_page.points.reset_data_but_cancel()

    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=5))


def test_empty_storage_shows_empty_list_and_map(empty_gis_page: FieldsGisPage) -> None:
    expect(empty_gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=0))
    expect(empty_gis_page.points.empty_state).to_be_visible()
    expect(empty_gis_page.map.markers).to_have_count(0)


# ---------------------------------------------------------------- показати на карті


def test_show_on_map_activates_point_field(gis_page: FieldsGisPage) -> None:
    gis_page.points.card(DISEASE_FIELD_2.description).show_on_map()

    expect(gis_page.fields.card(FIELD_2).root).to_have_attribute("aria-pressed", "true")


def test_show_on_map_centres_map_on_point(gis_page: FieldsGisPage) -> None:
    gis_page.points.card(DISEASE_FIELD_2.description).show_on_map()

    assert gis_page.map.is_a_marker_centered()


@known_bug("BUG-10")
def test_show_on_map_again_after_panning_recentres_map(gis_page: FieldsGisPage) -> None:
    point = gis_page.points.card(OTHER_FIELD_3.description)
    point.show_on_map()
    gis_page.map.drag_by(-400, 250)

    point.show_on_map()

    assert gis_page.map.is_a_marker_centered()
