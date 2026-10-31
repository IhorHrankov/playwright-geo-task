"""API fixtures: Playwright APIRequestContext with and without Basic Auth."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from playwright.sync_api import APIRequestContext, Playwright

from framework.api.app_client import AppClient, TileClient
from framework.config import Credentials


@pytest.fixture(scope="session")
def api_base_url(base_url: str | None, settings) -> str:
    return (base_url or settings.base_url).rstrip("/")


@pytest.fixture(scope="session")
def authed_request(
    playwright: Playwright, api_base_url: str, credentials: Credentials
) -> Iterator[APIRequestContext]:
    ctx = playwright.request.new_context(base_url=api_base_url, http_credentials=credentials.as_playwright())
    yield ctx
    ctx.dispose()


@pytest.fixture(scope="session")
def anonymous_request(playwright: Playwright, api_base_url: str) -> Iterator[APIRequestContext]:
    ctx = playwright.request.new_context(base_url=api_base_url)
    yield ctx
    ctx.dispose()


@pytest.fixture(scope="session")
def wrong_password_request(
    playwright: Playwright, api_base_url: str, credentials: Credentials
) -> Iterator[APIRequestContext]:
    ctx = playwright.request.new_context(
        base_url=api_base_url,
        http_credentials={"username": credentials.username, "password": credentials.password + "-wrong"},
    )
    yield ctx
    ctx.dispose()


@pytest.fixture(scope="session")
def app(authed_request: APIRequestContext) -> AppClient:
    return AppClient(authed_request)


@pytest.fixture(scope="session")
def tiles(playwright: Playwright) -> Iterator[TileClient]:
    ctx = playwright.request.new_context()
    yield TileClient(ctx)
    ctx.dispose()
