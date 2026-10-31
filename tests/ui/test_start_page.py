"""Start page (#/) and hash routing."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from framework.pages import FieldsGisPage, StartPage
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_start_page_describes_the_task(start_page: StartPage) -> None:
    expect(start_page.title).to_be_visible()
    expect(start_page.page.get_by_role("heading", name="Про застосунок")).to_be_visible()
    expect(start_page.page.get_by_role("heading", name="Що потрібно зробити")).to_be_visible()


def test_unknown_hash_route_falls_back_to_start_page(page: Page) -> None:
    page.goto("/#/no-such-route")
    expect(StartPage(page).title).to_be_visible()


def test_hash_navigation_switches_to_app(page: Page) -> None:
    StartPage(page).open()
    page.evaluate("location.hash = '#/test'")
    FieldsGisPage(page).wait_until_ready()


@known_bug("BUG-15")
def test_start_page_has_unique_element_ids(start_page: StartPage) -> None:
    assert start_page.duplicate_element_ids() == []
