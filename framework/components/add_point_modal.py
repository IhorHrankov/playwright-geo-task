from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.components.base_component import BaseComponent
from framework.data.models import PointType
from framework.utils.geo import mgrs_close, point_in_polygon, to_mgrs


class AddPointModal(BaseComponent):
    """Dialog 'Додати моніторингову точку' opened by a click inside the active field."""

    def __init__(self, page: Page) -> None:
        super().__init__(page.get_by_role("dialog", name="Додати моніторингову точку"))

    # --- locators ---
    @property
    def coordinates_text(self) -> Locator:
        """'50.41254, 30.50097' (WGS 84, 5 decimals)."""
        return self.root.locator("section > div").nth(0).locator(":scope > span").nth(1)

    @property
    def mgrs_text(self) -> Locator:
        return self.root.locator("section > div").nth(1).locator(":scope > span").nth(1)

    @property
    def type_select(self) -> Locator:
        return self.root.get_by_label("Тип моніторингу")

    @property
    def type_options(self) -> Locator:
        return self.type_select.locator("option")

    @property
    def description_input(self) -> Locator:
        return self.root.get_by_label("Опис (опціонально)")

    @property
    def error_message(self) -> Locator:
        return self.root.get_by_role("alert")

    # --- actions ---
    def add(self, point_type: PointType, description: str = "") -> None:
        self.type_select.select_option(point_type.value)
        self.description_input.fill(description)
        self.root.get_by_role("button", name="Зберегти точку").click()

    def type_description(self, text: str) -> None:
        self.description_input.fill(text)

    def cancel(self) -> None:
        self.root.get_by_role("button", name="Скасувати").click()

    def close(self) -> None:
        self.root.get_by_role("button", name="Закрити модальне вікно").click()

    def press_escape(self) -> None:
        self.page.keyboard.press("Escape")

    # --- domain checks (logic stays here, tests read as one sentence) ---
    def shows_mgrs_of_shown_coordinates(self) -> bool:
        """MGRS matches the shown coordinates (1 m tolerance: coordinates are rounded to 5 decimals)."""
        lat, lng = (float(x) for x in self.coordinates_text.inner_text().split(","))
        return mgrs_close(self.mgrs_text.inner_text(), to_mgrs(lat, lng))

    def shows_coordinates_inside(self, corners) -> bool:
        lat, lng = (float(x) for x in self.coordinates_text.inner_text().split(","))
        return point_in_polygon(lat, lng, corners)
