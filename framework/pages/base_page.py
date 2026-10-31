"""Base class for page objects: shared page handle, navigation, readiness contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from playwright.sync_api import Locator, Page


class BasePage(ABC):
    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    @abstractmethod
    def path(self) -> str:
        """Path relative to base_url (the app uses hash routing)."""

    @property
    @abstractmethod
    def ready_marker(self) -> Locator:
        """An element that is visible only when the page is usable."""

    def open(self) -> Self:
        self.page.goto(self.path)
        self.wait_until_ready()
        return self

    def reload(self) -> Self:
        self.page.reload()
        self.wait_until_ready()
        return self

    def wait_until_ready(self) -> None:
        self.ready_marker.wait_for(state="visible")
