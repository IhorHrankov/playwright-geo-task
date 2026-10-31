from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from framework.components.base_component import BaseComponent
from framework.data.fields import Field


class FieldCard(BaseComponent):
    """One field in the sidebar (article role="button", aria-pressed = active)."""

    @property
    def title(self) -> Locator:
        return self.root.get_by_role("heading", level=3)

    @property
    def points_badge(self) -> Locator:
        return self.root.locator("span").last

    def points_count(self) -> int:
        return int(self.points_badge.inner_text().strip())

    def is_active(self) -> bool:
        return self.root.get_attribute("aria-pressed") == "true"

    def select(self) -> None:
        self.root.click()


class FieldsList(BaseComponent):
    def __init__(self, page: Page) -> None:
        super().__init__(page.locator("section[aria-labelledby='fields-heading']"))

    @property
    def heading(self) -> Locator:
        return self.root.locator("#fields-heading")

    @property
    def cards(self) -> Locator:
        return self.root.locator("article[aria-pressed]")

    def card(self, field: Field) -> FieldCard:
        return FieldCard(self.root.get_by_role("button", name=re.compile(rf"^{re.escape(field.name)},")))

    def active_card(self) -> FieldCard:
        return FieldCard(self.root.locator("article[aria-pressed='true']"))
