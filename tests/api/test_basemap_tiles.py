"""Third-party tile services the map depends on (no auth: public endpoints)."""

from __future__ import annotations

import pytest

from framework.api.app_client import TileClient
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.api, pytest.mark.regression]

# Two tiles over the fields area (Kyiv) at zoom 14, plus one far away at zoom 10.
TILES = [(14, 9580, 5526), (14, 9580, 5527), (10, 598, 345)]


def test_satellite_tiles_are_served(tiles: TileClient) -> None:
    bodies = []
    for z, x, y in TILES:
        response = tiles.esri(z, x, y)
        assert response.status == 200
        assert response.headers["content-type"].startswith("image/")
        bodies.append(response.body())
    assert len(set(bodies)) == len(TILES), "different tiles must have different content"


@known_bug("BUG-07")
def test_streets_tiles_are_real_map_images(tiles: TileClient) -> None:
    bodies = []
    for z, x, y in TILES:
        response = tiles.carto(z, x, y)
        assert response.status == 200
        bodies.append(response.body())
    assert len(set(bodies)) == len(TILES), "CARTO returns the same placeholder image for every tile"
