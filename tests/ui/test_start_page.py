"""Start page (#/) and hash routing."""

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


def test_unknown_route_opens_start_page(page: Page) -> None:
    page.goto("/#/no-such-route")

    expect(StartPage(page).title).to_be_visible()


def test_test_route_opens_application(page: Page) -> None:
    page.goto("/#/test")

    expect(FieldsGisPage(page).app_title).to_be_visible()


@known_bug("BUG-15")
def test_start_page_element_ids_are_unique(start_page: StartPage) -> None:
    assert start_page.duplicate_element_ids() == []
