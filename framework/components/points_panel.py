from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from framework.components.base_component import BaseComponent
from framework.data.models import PointType

_COUNT_RE = re.compile(r"\((\d+)\)")


class PointCard(BaseComponent):
    """A monitoring point in the sidebar list."""

    @property
    def type_badge(self) -> Locator:
        return self.root.locator("header span").first

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
    """Points section: counter, search, sort, type filter, list, reset."""

    def __init__(self, page: Page) -> None:
        super().__init__(page.locator("section[aria-labelledby='points-heading']"))

    # --- locators ---
    @property
    def heading(self) -> Locator:
        return self.root.locator("#points-heading")

    @property
    def search_input(self) -> Locator:
        return self.root.get_by_role("searchbox", name="Пошук моніторингових точок за описом, MGRS або назвою поля")

    @property
    def sort_button(self) -> Locator:
        return self.root.get_by_role("button", name=re.compile("^Сортування за датою"))

    @property
    def type_toolbar(self) -> Locator:
        return self.root.get_by_role("toolbar", name="Фільтрація точок за категоріями замірів")

    @property
    def cards(self) -> Locator:
        return self.root.locator("article[aria-label^='Точка заміру']")

    @property
    def empty_state(self) -> Locator:
        return self.root.get_by_text("Точок за вашим запитом не знайдено")

    @property
    def reset_filters_button(self) -> Locator:
        return self.root.get_by_role("button", name="Скинути фільтри")

    @property
    def reset_data_button(self) -> Locator:
        return self.root.get_by_role("button", name="Скинути дані")

    # --- queries ---
    def counter(self) -> int:
        match = _COUNT_RE.search(self.heading.inner_text())
        assert match, f"counter not found in heading {self.heading.inner_text()!r}"
        return int(match.group(1))

    def card_at(self, index: int) -> PointCard:
        return PointCard(self.cards.nth(index))

    def card_by_description(self, text: str) -> PointCard:
        return PointCard(self.cards.filter(has_text=text))

    def descriptions(self) -> list[str]:
        return [d.strip() for d in self.cards.locator("p").all_inner_texts()]

    def created_at_values(self) -> list[str]:
        return self.cards.locator("time").evaluate_all("els => els.map(e => e.getAttribute('datetime'))")

    def sort_is_newest_first(self) -> bool:
        return "спочатку нові" in (self.sort_button.get_attribute("aria-label") or "")

    # --- actions ---
    def search(self, text: str) -> None:
        self.search_input.fill(text)

    def filter_by_type(self, point_type: PointType | None) -> None:
        label = "Всі" if point_type is None else point_type.label
        self.type_toolbar.get_by_role("button", name=label, exact=True).click()

    def type_filter_button(self, point_type: PointType | None) -> Locator:
        label = "Всі" if point_type is None else point_type.label
        return self.type_toolbar.get_by_role("button", name=label, exact=True)

    def toggle_sort(self) -> None:
        self.sort_button.click()

    def reset_data(self, *, accept: bool = True) -> None:
        """Click "Скинути дані" and answer the native confirm() dialog."""
        self.page.once("dialog", lambda d: d.accept() if accept else d.dismiss())
        self.reset_data_button.click()
