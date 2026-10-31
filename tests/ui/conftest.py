"""UI fixtures: page objects injected into tests, with localStorage seeded before the first load."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import pytest
from playwright.sync_api import BrowserContext, Page

from framework.data import datasets
from framework.data.models import MonitoringPoint
from framework.pages import FieldsGisPage, StartPage
from framework.storage import seed_points

OpenGis = Callable[..., FieldsGisPage]


@pytest.fixture
def open_gis(page: Page, context: BrowserContext) -> OpenGis:
    """Factory: ``open_gis(points)`` seeds the given points and opens #/test."""

    def _open(points: Sequence[MonitoringPoint] | None = None) -> FieldsGisPage:
        seed_points(context, datasets.standard_points() if points is None else points)
        return FieldsGisPage(page).open()

    return _open


@pytest.fixture
def standard_points() -> list[MonitoringPoint]:
    return datasets.standard_points()


@pytest.fixture
def gis_page(open_gis: OpenGis, standard_points: list[MonitoringPoint]) -> FieldsGisPage:
    """Main page with the standard dataset (5 points across 4 fields)."""
    return open_gis(standard_points)


@pytest.fixture
def empty_gis_page(open_gis: OpenGis) -> FieldsGisPage:
    return open_gis([])


@pytest.fixture
def start_page(page: Page) -> StartPage:
    return StartPage(page).open()
