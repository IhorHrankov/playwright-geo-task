"""UI-фікстури. Кожен тест має власний контекст браузера, тому localStorage не спільний."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import pytest
from playwright.sync_api import BrowserContext, Page

from framework.data.models import MonitoringPoint
from framework.data.test_data import STANDARD_POINTS
from framework.pages import FieldsGisPage
from framework.storage import seed_points

OpenGis = Callable[[Sequence[MonitoringPoint]], FieldsGisPage]


@pytest.fixture
def open_gis_with(page: Page, context: BrowserContext) -> OpenGis:
    """Відкриває #/test саме із заданими точками у сховищі: ``open_gis_with([POINT])``."""

    def _open(points: Sequence[MonitoringPoint]) -> FieldsGisPage:
        seed_points(context, points)
        return FieldsGisPage(page).open()

    return _open


@pytest.fixture
def gis_page(open_gis_with: OpenGis) -> FieldsGisPage:
    """#/test із 5 стандартними точками (framework/data/test_data.py)."""
    return open_gis_with(STANDARD_POINTS)


@pytest.fixture
def empty_gis_page(open_gis_with: OpenGis) -> FieldsGisPage:
    """#/test без жодної точки."""
    return open_gis_with([])
