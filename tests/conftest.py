"""Фікстури на сесію: налаштування, Basic Auth для контекстів браузера, стабільні локаль і часовий пояс."""

from __future__ import annotations

import os

import pytest

from framework.config import Credentials, Settings


def pytest_configure(config: pytest.Config) -> None:
    # Дозволяє BASE_URL з оточення / .env, якщо --base-url не передано явно.
    env_url = os.getenv("BASE_URL")
    if env_url and hasattr(config.option, "base_url") and not config.getoption("base_url", default=None):
        config.option.base_url = env_url.rstrip("/")


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def credentials(settings: Settings) -> Credentials:
    if settings.credentials is None:
        pytest.skip("APP_USERNAME / APP_PASSWORD не задано (див. .env.example)")
    return settings.credentials


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, credentials: Credentials) -> dict:
    """Кожен контекст браузера проходить Basic Auth і показує дати для Києва."""
    return {
        **browser_context_args,
        "http_credentials": credentials.as_playwright(),
        "locale": "uk-UA",
        "timezone_id": "Europe/Kyiv",
        "viewport": {"width": 1440, "height": 900},
        "accept_downloads": True,
    }
