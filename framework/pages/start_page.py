from __future__ import annotations

from playwright.sync_api import Locator

from framework.pages.base_page import BasePage


class StartPage(BasePage):
    """Landing page (#/) with the task description."""

    path = "/#/"

    @property
    def ready_marker(self) -> Locator:
        return self.title

    @property
    def title(self) -> Locator:
        return self.page.get_by_role("heading", level=1, name="Тестове завдання для QA Engineer")

    def duplicate_element_ids(self) -> list[str]:
        return self.page.evaluate(
            """() => {
                const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
                return [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))];
            }"""
        )
