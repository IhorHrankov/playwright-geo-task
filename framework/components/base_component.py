"""Базовий клас компонентів: кожен компонент обмежений власним кореневим локатором."""

from __future__ import annotations

from playwright.sync_api import Locator, Page


class BaseComponent:
    def __init__(self, root: Locator) -> None:
        self.root = root

    @property
    def page(self) -> Page:
        return self.root.page

    def is_visible(self) -> bool:
        return self.root.is_visible()
