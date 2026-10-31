"""Thin HTTP client for the static Amplify host and the tile providers the map depends on.

The application has no backend REST API: everything it loads over HTTP is static
(index.html, JS bundle, /samples/*.geojson) plus third-party basemap tiles. These are
the "API" contracts the UI relies on, so they are checked directly at HTTP level.
"""

from __future__ import annotations

import re

from playwright.sync_api import APIRequestContext, APIResponse

SAMPLE_GEOJSON_PATH = "/samples/monitoring-points-sample.geojson"
CARTO_TILE = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
ESRI_TILE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
_BUNDLE_RE = re.compile(r'src="(/assets/index-[\w-]+\.js)"')


class AppClient:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    def index(self) -> APIResponse:
        return self.request.get("/")

    def sample_geojson(self) -> APIResponse:
        return self.request.get(SAMPLE_GEOJSON_PATH)

    def bundle_path(self) -> str:
        html = self.index().text()
        match = _BUNDLE_RE.search(html)
        assert match, "main JS bundle is not referenced from index.html"
        return match.group(1)

    def get(self, path: str) -> APIResponse:
        return self.request.get(path)


class TileClient:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    def carto(self, z: int, x: int, y: int, subdomain: str = "a") -> APIResponse:
        return self.request.get(CARTO_TILE.format(s=subdomain, z=z, x=x, y=y))

    def esri(self, z: int, x: int, y: int) -> APIResponse:
        return self.request.get(ESRI_TILE.format(z=z, x=x, y=y))
