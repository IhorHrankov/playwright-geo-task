from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from framework.components.base_component import BaseComponent
from framework.data.fields import Field


class FieldCard(BaseComponent):
    """One field in the sidebar (article role="button"; aria-pressed="true" when active)."""

    @property
    def title(self) -> Locator:
        return self.root.get_by_role("heading", level=3)

    @property
    def points_badge(self) -> Locator:
        return self.root.locator("span").last

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

    @property
    def titles(self) -> Locator:
        return self.cards.get_by_role("heading", level=3)

    @property
    def active_cards(self) -> Locator:
        return self.root.locator("article[aria-pressed='true']")

    def card(self, field: Field) -> FieldCard:
        return FieldCard(self.root.get_by_role("button", name=re.compile(rf"^{re.escape(field.name)},")))
