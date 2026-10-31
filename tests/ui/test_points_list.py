"""Points list: order, search, type filter, delete, reset, 'show on map' (TC-04, TC-07, TC-08)."""

import pytest
from playwright.sync_api import expect

from framework.data import messages
from framework.data.fields import FIELD_1, FIELD_2
from framework.data.models import PointType
from framework.data.test_data import (
    DISEASE_FIELD_2,
    OTHER_FIELD_3,
    SOIL_SAMPLE_FIELD_1,
    STANDARD_DESCRIPTIONS_NEWEST_FIRST,
    STANDARD_DESCRIPTIONS_OLDEST_FIRST,
)
from framework.pages import FieldsGisPage
from framework.storage import StoredPoints
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


# ---------------------------------------------------------------- order


@pytest.mark.smoke
def test_list_shows_all_points_newest_first(gis_page: FieldsGisPage) -> None:
    expect(gis_page.points.heading).to_have_text("Моніторингові точки (5)")
    expect(gis_page.points.sort_button).to_have_text("Нові")
    expect(gis_page.points.descriptions).to_have_text(STANDARD_DESCRIPTIONS_NEWEST_FIRST)


def test_sort_toggle_shows_oldest_first(gis_page: FieldsGisPage) -> None:
    gis_page.points.toggle_sort()

    expect(gis_page.points.sort_button).to_have_text("Старі")
    expect(gis_page.points.descriptions).to_have_text(STANDARD_DESCRIPTIONS_OLDEST_FIRST)


def test_second_sort_toggle_returns_newest_first(gis_page: FieldsGisPage) -> None:
    gis_page.points.toggle_sort()

    gis_page.points.toggle_sort()

    expect(gis_page.points.descriptions).to_have_text(STANDARD_DESCRIPTIONS_NEWEST_FIRST)


# ---------------------------------------------------------------- search


@pytest.mark.parametrize(
    ("query", "expected_descriptions"),
    [
        ("черепашки", ["Осередок клопа шкідливої черепашки"]),
        ("ЧЕРЕПАШКИ", ["Осередок клопа шкідливої черепашки"]),
        ("  гнилі  ", ["Ознаки білої гнилі на прикореневій шийці"]),
        ("Соняшник", ["Ознаки білої гнилі на прикореневій шийці"]),
        ("36U UA 22882 89519", ["Контрольна точка метеостанції"]),
        ("шкідники", ["Пастки на ріпакового квіткоїда", "Осередок клопа шкідливої черепашки"]),
    ],
    ids=["by-description", "case-insensitive", "trims-spaces", "by-field-name", "by-mgrs", "by-type-label"],
)
def test_search_finds_points(gis_page: FieldsGisPage, query: str, expected_descriptions: list[str]) -> None:
    gis_page.points.search(query)

    expect(gis_page.points.descriptions).to_have_text(expected_descriptions)


def test_search_without_matches_shows_empty_state(gis_page: FieldsGisPage) -> None:
    gis_page.points.search("такого опису немає")

    expect(gis_page.points.heading).to_have_text("Моніторингові точки (0)")
    expect(gis_page.points.empty_state).to_have_text(messages.NO_POINTS_FOUND)


def test_reset_filters_button_clears_search(gis_page: FieldsGisPage) -> None:
    gis_page.points.search("такого опису немає")

    gis_page.points.reset_filters_button.click()

    expect(gis_page.points.search_input).to_have_value("")
    expect(gis_page.points.heading).to_have_text("Моніторингові точки (5)")


# ---------------------------------------------------------------- type filter


@pytest.mark.parametrize(
    ("point_type", "expected_badges"),
    [
        (PointType.SOIL_SAMPLE, ["Проба ґрунту"]),
        (PointType.PESTS, ["Шкідники", "Шкідники"]),
        (PointType.PLANT_DISEASE, ["Хвороби рослин"]),
        (PointType.OTHER, ["Інше"]),
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

    gis_page.points.search("Ріпак")

    expect(gis_page.points.descriptions).to_have_text(["Пастки на ріпакового квіткоїда"])


@known_bug("BUG-11")
def test_type_filter_is_applied_to_map_markers(gis_page: FieldsGisPage) -> None:
    gis_page.points.filter_by_type(PointType.PLANT_DISEASE)

    expect(gis_page.map.markers).to_have_count(1, timeout=2_000)


# ---------------------------------------------------------------- delete


def test_deleting_point_removes_it_from_list(gis_page: FieldsGisPage) -> None:
    gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).delete()

    expect(gis_page.toast.root).to_have_text(messages.POINT_DELETED)
    expect(gis_page.points.heading).to_have_text("Моніторингові точки (4)")
    expect(gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).root).to_have_count(0)


def test_deleting_point_removes_its_marker_and_updates_field_counter(gis_page: FieldsGisPage) -> None:
    gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).delete()

    expect(gis_page.map.markers).to_have_count(4)
    expect(gis_page.fields.card(FIELD_1).points_badge).to_have_text("1")


def test_deleting_point_removes_it_from_storage(gis_page: FieldsGisPage) -> None:
    gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).delete()
    expect(gis_page.points.heading).to_have_text("Моніторингові точки (4)")

    assert StoredPoints(gis_page.page).ids() == ["std-2", "std-3", "std-4", "std-5"]


def test_deleting_point_from_map_popup(gis_page: FieldsGisPage) -> None:
    gis_page.map.markers.first.click()

    gis_page.map.popup.get_by_role("button", name="Видалити моніторингову точку").click()

    expect(gis_page.points.heading).to_have_text("Моніторингові точки (4)")


@known_bug("BUG-14")
def test_deleting_point_offers_undo(gis_page: FieldsGisPage) -> None:
    gis_page.points.first_card.delete()

    expect(gis_page.toast.root.get_by_role("button", name="Скасувати")).to_be_visible(timeout=1_000)


# ---------------------------------------------------------------- reset


def test_reset_data_restores_three_builtin_points(gis_page: FieldsGisPage) -> None:
    gis_page.points.reset_data()

    expect(gis_page.toast.root).to_have_text(messages.DATA_RESET)
    expect(gis_page.points.heading).to_have_text("Моніторингові точки (3)")


def test_cancelled_reset_keeps_points(gis_page: FieldsGisPage) -> None:
    gis_page.points.reset_data_but_cancel()

    expect(gis_page.points.heading).to_have_text("Моніторингові точки (5)")


def test_empty_storage_shows_empty_list_and_map(empty_gis_page: FieldsGisPage) -> None:
    expect(empty_gis_page.points.heading).to_have_text("Моніторингові точки (0)")
    expect(empty_gis_page.points.empty_state).to_be_visible()
    expect(empty_gis_page.map.markers).to_have_count(0)


# ---------------------------------------------------------------- show on map


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
