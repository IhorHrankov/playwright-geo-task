"""Базовий клас page objects: спільний page, навігація, контракт готовності."""

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
        """Шлях відносно base_url (застосунок використовує hash-маршрутизацію)."""

    @property
    @abstractmethod
    def ready_marker(self) -> Locator:
        """Елемент, видимий лише тоді, коли сторінкою можна користуватися."""

    def open(self) -> Self:
        # Готовність визначає ready_marker; подія load залежить від повільних сторонніх ресурсів.
        self.page.goto(self.path, wait_until="domcontentloaded")
        self.wait_until_ready()
        return self

    def reload(self) -> Self:
        self.page.reload(wait_until="domcontentloaded")
        self.wait_until_ready()
        return self

    def wait_until_ready(self) -> None:
        self.ready_marker.wait_for(state="visible")
