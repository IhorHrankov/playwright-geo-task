from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from framework.components.base_component import BaseComponent
from framework.data.models import PointType


class PointCard(BaseComponent):
    """A monitoring point in the sidebar list."""

    @property
    def type_badge(self) -> Locator:
        return self.root.locator("header span").first

    @property
    def field_name(self) -> Locator:
        return self.root.locator("header span").nth(1)

    @property
    def description(self) -> Locator:
        return self.root.locator("p")

    @property
    def mgrs(self) -> Locator:
        return self.root.locator("footer span").first

    @property
    def created_at(self) -> Locator:
        return self.root.locator("time")

    def show_on_map(self) -> None:
        self.root.get_by_text("Показати на карті").click()

    def delete(self) -> None:
        self.root.get_by_role("button", name="Видалити точку моніторингу").click()


class PointsPanel(BaseComponent):
    """Points section: counter heading, search, sort, type filter, list, reset."""

    def __init__(self, page: Page) -> None:
        super().__init__(page.locator("section[aria-labelledby='points-heading']"))

    # --- locators used in assertions ---
    @property
    def heading(self) -> Locator:
        """Text: 'Моніторингові точки (N)'."""
        return self.root.locator("#points-heading")

    @property
    def cards(self) -> Locator:
        return self.root.locator("article[aria-label^='Точка заміру']")

    @property
    def descriptions(self) -> Locator:
        return self.cards.locator("p")

    @property
    def type_badges(self) -> Locator:
        return self.cards.locator("header span:first-child")

    @property
    def search_input(self) -> Locator:
        return self.root.get_by_role(
            "searchbox", name="Пошук моніторингових точок за описом, MGRS або назвою поля"
        )

    @property
    def sort_button(self) -> Locator:
        return self.root.get_by_role("button", name=re.compile("^Сортування за датою"))

    @property
    def empty_state(self) -> Locator:
        return self.root.get_by_text("Точок за вашим запитом не знайдено")

    @property
    def reset_filters_button(self) -> Locator:
        return self.root.get_by_role("button", name="Скинути фільтри")

    def type_filter(self, point_type: PointType) -> Locator:
        return self._type_toolbar.get_by_role("button", name=point_type.label, exact=True)

    @property
    def all_types_filter(self) -> Locator:
        return self._type_toolbar.get_by_role("button", name="Всі", exact=True)

    @property
    def _type_toolbar(self) -> Locator:
        return self.root.get_by_role("toolbar", name="Фільтрація точок за категоріями замірів")

    # --- cards ---
    @property
    def first_card(self) -> PointCard:
        return PointCard(self.cards.first)

    def card(self, description: str) -> PointCard:
        return PointCard(self.cards.filter(has=self.page.locator("p", has_text=description)).first)

    # --- actions ---
    def search(self, text: str) -> None:
        self.search_input.fill(text)

    def filter_by_type(self, point_type: PointType) -> None:
        self.type_filter(point_type).click()

    def toggle_sort(self) -> None:
        self.sort_button.click()

    def reset_data(self) -> None:
        """Click 'Скинути дані' and confirm the native dialog."""
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.root.get_by_role("button", name="Скинути дані").click()

    def reset_data_but_cancel(self) -> None:
        self.page.once("dialog", lambda dialog: dialog.dismiss())
        self.root.get_by_role("button", name="Скинути дані").click()
