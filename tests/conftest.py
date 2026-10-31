"""Session-wide fixtures: settings, Basic Auth for browser contexts, deterministic locale/timezone."""

from __future__ import annotations

import os

import pytest

from framework.config import Credentials, Settings


def pytest_configure(config: pytest.Config) -> None:
    # Allow BASE_URL from the environment / .env when --base-url is not passed explicitly.
    env_url = os.getenv("BASE_URL")
    if env_url and hasattr(config.option, "base_url") and not config.getoption("base_url", default=None):
        config.option.base_url = env_url.rstrip("/")


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def credentials(settings: Settings) -> Credentials:
    if settings.credentials is None:
        pytest.skip("APP_USERNAME / APP_PASSWORD are not configured (see .env.example)")
    return settings.credentials


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, credentials: Credentials) -> dict:
    """Every browser context authenticates with Basic Auth and renders dates for Kyiv."""
    return {
        **browser_context_args,
        "http_credentials": credentials.as_playwright(),
        "locale": "uk-UA",
        "timezone_id": "Europe/Kyiv",
        "viewport": {"width": 1440, "height": 900},
        "accept_downloads": True,
    }
