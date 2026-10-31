from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.components.base_component import BaseComponent
from framework.data.models import PointType


class AddPointModal(BaseComponent):
    """Dialog "Додати моніторингову точку" opened by a click inside the active field."""

    def __init__(self, page: Page) -> None:
        super().__init__(page.get_by_role("dialog", name="Додати моніторингову точку"))

    @property
    def coordinates_section(self) -> Locator:
        return self.root.get_by_role("region", name="Географічні координати заміру")

    @property
    def lat_lng_text(self) -> Locator:
        # second <span> of the "WGS 84 (Lat, Lng)" row
        return self.root.locator("section > div").nth(0).locator(":scope > span").nth(1)

    @property
    def mgrs_text(self) -> Locator:
        return self.root.locator("section > div").nth(1).locator(":scope > span").nth(1)

    @property
    def type_select(self) -> Locator:
        return self.root.get_by_label("Тип моніторингу")

    @property
    def description_input(self) -> Locator:
        return self.root.get_by_label("Опис (опціонально)")

    @property
    def error_message(self) -> Locator:
        return self.root.get_by_role("alert")

    @property
    def save_button(self) -> Locator:
        return self.root.get_by_role("button", name="Зберегти точку")

    @property
    def cancel_button(self) -> Locator:
        return self.root.get_by_role("button", name="Скасувати")

    @property
    def close_button(self) -> Locator:
        return self.root.get_by_role("button", name="Закрити модальне вікно")

    def lat_lng(self) -> tuple[float, float]:
        lat, lng = (float(x) for x in self.lat_lng_text.inner_text().split(","))
        return lat, lng

    def fill(self, point_type: PointType, description: str | None = None) -> None:
        self.type_select.select_option(point_type.value)
        if description is not None:
            self.description_input.fill(description)

    def save(self) -> None:
        self.save_button.click()

    def add(self, point_type: PointType, description: str | None = None) -> None:
        self.fill(point_type, description)
        self.save()
