"""HTTP checks of the Amplify host: Basic Auth, SPA entry point, bundle, 404, security headers."""

import pytest
from playwright.sync_api import APIRequestContext

from framework.api.app_client import AppClient
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.mark.smoke
def test_site_without_credentials_asks_for_basic_auth(anonymous_request: APIRequestContext) -> None:
    response = anonymous_request.get("/")

    assert response.status == 401
    assert response.headers.get("www-authenticate").startswith("Basic")


def test_site_with_wrong_password_is_rejected(wrong_password_request: APIRequestContext) -> None:
    response = wrong_password_request.get("/")

    assert response.status == 401


def test_demo_sample_without_credentials_is_rejected(anonymous_request: APIRequestContext) -> None:
    response = anonymous_request.get("/samples/monitoring-points-sample.geojson")

    assert response.status == 401


@pytest.mark.smoke
def test_index_page_is_served_to_authorised_user(app: AppClient) -> None:
    response = app.index()

    assert response.status == 200
    assert response.headers.get("content-type") == "text/html"
    assert "AgTech Fields GIS" in response.text()


def test_main_javascript_bundle_is_served(app: AppClient) -> None:
    response = app.main_bundle()

    assert response.status == 200
    assert response.headers.get("content-type") == "text/javascript"


def test_unknown_path_returns_404(app: AppClient) -> None:
    response = app.get("/definitely-not-here-404")

    assert response.status == 404


@known_bug("BUG-16")
@pytest.mark.parametrize(
    "header",
    ["strict-transport-security", "x-content-type-options", "x-frame-options", "content-security-policy"],
    ids=["hsts", "nosniff", "x-frame-options", "csp"],
)
def test_index_page_sends_security_header(app: AppClient, header: str) -> None:
    response = app.index()

    assert header in response.headers
