from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.components.base_component import BaseComponent
from framework.data.models import PointType
from framework.utils.geo import mgrs_close, point_in_polygon, to_mgrs


class AddPointModal(BaseComponent):
    """Діалог «Додати моніторингову точку», що відкривається кліком усередині активного поля."""

    def __init__(self, page: Page) -> None:
        super().__init__(page.get_by_role("dialog", name="Додати моніторингову точку"))

    # --- локатори ---
    @property
    def coordinates_text(self) -> Locator:
        """'50.41254, 30.50097' (WGS 84, 5 знаків після коми)."""
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

    # --- дії ---
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

    # --- доменні перевірки (логіка лишається тут, тест читається одним реченням) ---
    def shows_mgrs_of_shown_coordinates(self) -> bool:
        """MGRS відповідає показаним координатам (допуск 1 м: координати округлені до 5 знаків)."""
        lat, lng = (float(x) for x in self.coordinates_text.inner_text().split(","))
        return mgrs_close(self.mgrs_text.inner_text(), to_mgrs(lat, lng))

    def shows_coordinates_inside(self, corners) -> bool:
        lat, lng = (float(x) for x in self.coordinates_text.inner_text().split(","))
        return point_in_polygon(lat, lng, corners)
