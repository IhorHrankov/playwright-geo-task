from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.components.base_component import BaseComponent


class Toast(BaseComponent):
    """Notification shown after actions (role="status")."""

    def __init__(self, page: Page) -> None:
        super().__init__(page.get_by_role("status"))

    @property
    def message(self) -> Locator:
        return self.root.locator("span").first

    def close(self) -> None:
        self.root.get_by_role("button", name="Закрити сповіщення").click()
