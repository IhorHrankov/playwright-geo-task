"""Points list: search, type filter, sorting, delete, reset, 'show on map'."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from framework.data import datasets
from framework.data.fields import FIELDS_BY_ID
from framework.data.models import MonitoringPoint, PointType
from framework.pages import FieldsGisPage
from framework.storage import read_points
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


def _by_newest(points: list[MonitoringPoint]) -> list[MonitoringPoint]:
    return sorted(points, key=lambda p: p.created_at, reverse=True)


@pytest.mark.smoke
def test_list_shows_all_points_newest_first(gis_page: FieldsGisPage, standard_points) -> None:
    expect(gis_page.points.heading).to_contain_text(f"({len(standard_points)})")
    expect(gis_page.points.cards).to_have_count(len(standard_points))
    assert gis_page.points.sort_is_newest_first()
    assert gis_page.points.descriptions() == [p.description for p in _by_newest(standard_points)]


def test_sort_toggle_switches_to_oldest_first_and_back(gis_page: FieldsGisPage, standard_points) -> None:
    gis_page.points.toggle_sort()
    expect(gis_page.points.sort_button).to_contain_text("Старі")
    assert gis_page.points.descriptions() == [p.description for p in reversed(_by_newest(standard_points))]

    gis_page.points.toggle_sort()
    expect(gis_page.points.sort_button).to_contain_text("Нові")
    assert gis_page.points.descriptions() == [p.description for p in _by_newest(standard_points)]


@pytest.mark.parametrize(
    ("query", "expected_ids"),
    [
        pytest.param("черепашки", {"std-2"}, id="by-description"),
        pytest.param("ЧЕРЕПАШКИ", {"std-2"}, id="case-insensitive"),
        pytest.param("Соняшник", {"std-3"}, id="by-field-name"),
        pytest.param("шкідники", {"std-2", "std-5"}, id="by-type-label"),
        pytest.param("  гнилі  ", {"std-3"}, id="trimmed"),
    ],
)
def test_search(gis_page: FieldsGisPage, standard_points, query: str, expected_ids: set[str]) -> None:
    expected = [p.description for p in _by_newest(standard_points) if p.id in expected_ids]

    gis_page.points.search(query)

    expect(gis_page.points.heading).to_contain_text(f"({len(expected)})")
    assert gis_page.points.descriptions() == expected


def test_search_by_mgrs(gis_page: FieldsGisPage, standard_points) -> None:
    target = standard_points[3]
    gis_page.points.search(target.mgrs)

    expect(gis_page.points.cards).to_have_count(1)
    expect(gis_page.points.card_at(0).mgrs).to_have_text(target.mgrs)


def test_search_without_results_offers_filter_reset(gis_page: FieldsGisPage, standard_points) -> None:
    gis_page.points.search("такого опису немає")

    expect(gis_page.points.cards).to_have_count(0)
    expect(gis_page.points.empty_state).to_be_visible()

    gis_page.points.reset_filters_button.click()

    expect(gis_page.points.search_input).to_have_value("")
    expect(gis_page.points.cards).to_have_count(len(standard_points))


@pytest.mark.parametrize("point_type", list(PointType), ids=lambda t: t.value)
def test_filter_by_type(gis_page: FieldsGisPage, standard_points, point_type: PointType) -> None:
    expected = [p for p in standard_points if p.type == point_type.value]

    gis_page.points.filter_by_type(point_type)

    expect(gis_page.points.type_filter_button(point_type)).to_have_attribute("aria-pressed", "true")
    expect(gis_page.points.cards).to_have_count(len(expected))
    for i in range(len(expected)):
        expect(gis_page.points.card_at(i).type_badge).to_have_text(point_type.label)


def test_filter_and_search_combine(gis_page: FieldsGisPage) -> None:
    gis_page.points.filter_by_type(PointType.PESTS)
    gis_page.points.search("Ріпак")

    expect(gis_page.points.cards).to_have_count(1)
    expect(gis_page.points.card_at(0).description).to_have_text("Пастки на ріпакового квіткоїда")


def test_delete_point_from_list(gis_page: FieldsGisPage, standard_points) -> None:
    victim = standard_points[0]
    field_card = gis_page.fields.card(FIELDS_BY_ID[victim.field_id])
    field_count = field_card.points_count()

    gis_page.points.card_by_description(victim.description).delete()

    expect(gis_page.toast.root).to_have_text("Точку моніторингу видалено")
    expect(gis_page.points.card_by_description(victim.description).root).to_have_count(0)
    expect(gis_page.points.heading).to_contain_text(f"({len(standard_points) - 1})")
    expect(gis_page.map.markers).to_have_count(len(standard_points) - 1)
    expect(field_card.points_badge).to_have_text(str(field_count - 1))
    assert victim.id not in {p["id"] for p in read_points(gis_page.page)}


def test_delete_point_from_map_popup(gis_page: FieldsGisPage, standard_points) -> None:
    gis_page.map.markers.first.click()
    expect(gis_page.map.popup).to_be_visible()

    gis_page.map.popup.get_by_role("button", name="Видалити моніторингову точку").click()

    expect(gis_page.points.cards).to_have_count(len(standard_points) - 1)


@known_bug("BUG-14")
def test_delete_asks_for_confirmation(gis_page: FieldsGisPage, standard_points) -> None:
    dialogs: list[str] = []
    gis_page.page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))

    gis_page.points.card_at(0).delete()

    undo = gis_page.toast.root.get_by_role("button", name="Скасувати")
    assert dialogs or undo.is_visible(), "point was deleted with neither confirmation nor undo"


def test_reset_data_restores_builtin_points(gis_page: FieldsGisPage) -> None:
    gis_page.points.reset_data(accept=True)

    expect(gis_page.toast.root).to_have_text("Дані успішно скинуто до початкових демо-точок")
    expect(gis_page.points.cards).to_have_count(3)  # three built-in default points
    assert {p["id"] for p in read_points(gis_page.page)} == {"point-1", "point-2", "point-3"}


def test_reset_data_cancelled_keeps_points(gis_page: FieldsGisPage, standard_points) -> None:
    gis_page.points.reset_data(accept=False)

    expect(gis_page.points.cards).to_have_count(len(standard_points))


def test_show_on_map_activates_field_and_centres_point(gis_page: FieldsGisPage, standard_points) -> None:
    target = standard_points[2]  # lives in field-2, which is not active initially

    gis_page.points.card_by_description(target.description).show_on_map()

    expect(gis_page.fields.card(FIELDS_BY_ID[target.field_id]).root).to_have_attribute("aria-pressed", "true")
    assert gis_page.map.has_marker_at_center()


@known_bug("BUG-10")
def test_show_on_map_twice_recentres_after_pan(gis_page: FieldsGisPage, standard_points) -> None:
    card = gis_page.points.card_by_description(standard_points[2].description)
    card.show_on_map()
    assert gis_page.map.has_marker_at_center()

    gis_page.map.drag_by(-400, 250)
    assert not gis_page.map.has_marker_at_center(timeout_ms=500)

    card.show_on_map()
    assert gis_page.map.has_marker_at_center()


@known_bug("BUG-11")
def test_type_filter_is_applied_to_map_markers(gis_page: FieldsGisPage, standard_points) -> None:
    gis_page.points.filter_by_type(PointType.PLANT_DISEASE)
    expect(gis_page.points.cards).to_have_count(1)

    expect(gis_page.map.markers).to_have_count(1, timeout=2_000)


def test_empty_storage_shows_empty_list(open_gis) -> None:
    gis = open_gis(datasets.empty())

    expect(gis.points.heading).to_contain_text("(0)")
    expect(gis.points.empty_state).to_be_visible()
    expect(gis.map.markers).to_have_count(0)
