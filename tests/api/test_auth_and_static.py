"""HTTP checks of the Amplify host: Basic Auth, SPA entry point, bundle, 404, security headers."""

from __future__ import annotations

import pytest
from playwright.sync_api import APIRequestContext

from framework.api.app_client import AppClient
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.mark.smoke
def test_site_requires_basic_auth(anonymous_request: APIRequestContext) -> None:
    response = anonymous_request.get("/")

    assert response.status == 401
    assert response.headers.get("www-authenticate", "").lower().startswith("basic")


def test_wrong_password_is_rejected(wrong_password_request: APIRequestContext) -> None:
    assert wrong_password_request.get("/").status == 401


@pytest.mark.parametrize("path", ["/samples/monitoring-points-sample.geojson", "/index.html"])
def test_protected_resources_need_auth(anonymous_request: APIRequestContext, path: str) -> None:
    assert anonymous_request.get(path).status == 401


@pytest.mark.smoke
def test_index_html_is_served(app: AppClient) -> None:
    response = app.index()

    assert response.status == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "AgTech Fields GIS" in response.text()


def test_main_bundle_is_served_as_javascript(app: AppClient) -> None:
    response = app.get(app.bundle_path())

    assert response.status == 200
    assert response.headers["content-type"].startswith(("text/javascript", "application/javascript"))
    assert len(response.body()) > 10_000


def test_unknown_path_returns_404(app: AppClient) -> None:
    assert app.get("/definitely-not-here-404").status == 404


@known_bug("BUG-16")
@pytest.mark.parametrize(
    "header",
    ["strict-transport-security", "x-content-type-options", "x-frame-options", "content-security-policy"],
)
def test_security_headers_present(app: AppClient, header: str) -> None:
    assert header in app.index().headers
