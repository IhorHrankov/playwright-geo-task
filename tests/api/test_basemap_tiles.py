"""Third-party tile services the map depends on (public endpoints, no auth).

Three different tiles over the fields area must have three different images.
"""

import pytest

from framework.api.app_client import TileClient
from tests.known_bugs import known_bug

pytestmark = [pytest.mark.api, pytest.mark.regression]


def test_satellite_tile_is_an_image(tiles: TileClient) -> None:
    response = tiles.esri(z=14, x=9580, y=5526)

    assert response.status == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_satellite_tiles_differ_from_each_other(tiles: TileClient) -> None:
    assert tiles.esri_distinct_images(TileClient.KYIV_TILES) == 3


@known_bug("BUG-07")
def test_street_tiles_differ_from_each_other(tiles: TileClient) -> None:
    assert tiles.carto_distinct_images(TileClient.KYIV_TILES) == 3
