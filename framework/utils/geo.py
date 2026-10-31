"""Independent geodesy helpers used as a test oracle (no dependency on the app's own code).

* ``to_mgrs`` — WGS84 lat/lng -> MGRS (5-digit, 1 m precision) via UTM (Snyder series).
* ``point_in_polygon`` — ray casting on lng/lat.
* ``polygon_area_ha`` — planar area on a local equirectangular projection (accurate for small fields).
"""

from __future__ import annotations

import math
from collections.abc import Sequence

_A = 6378137.0
_F = 1 / 298.257223563
_K0 = 0.9996
_E2 = _F * (2 - _F)
_EP2 = _E2 / (1 - _E2)

_BANDS = "CDEFGHJKLMNPQRSTUVWXX"
_COL_SETS = ("ABCDEFGH", "JKLMNPQR", "STUVWXYZ")
_ROW_LETTERS = "ABCDEFGHJKLMNPQRSTUV"


def is_valid_lat_lng(lat: float, lng: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lng <= 180


def to_utm(lat: float, lng: float) -> tuple[int, float, float]:
    """Return (zone, easting, northing). Norway/Svalbard zone exceptions are out of scope."""
    if not is_valid_lat_lng(lat, lng) or not -80 <= lat <= 84:
        raise ValueError(f"coordinates outside the UTM/MGRS domain: {lat}, {lng}")
    zone = int((lng + 180) / 6) + 1
    lon0 = math.radians((zone - 1) * 6 - 180 + 3)
    phi, lam = math.radians(lat), math.radians(lng)
    n = _A / math.sqrt(1 - _E2 * math.sin(phi) ** 2)
    t = math.tan(phi) ** 2
    c = _EP2 * math.cos(phi) ** 2
    a = math.cos(phi) * (lam - lon0)
    m = _A * (
        (1 - _E2 / 4 - 3 * _E2**2 / 64 - 5 * _E2**3 / 256) * phi
        - (3 * _E2 / 8 + 3 * _E2**2 / 32 + 45 * _E2**3 / 1024) * math.sin(2 * phi)
        + (15 * _E2**2 / 256 + 45 * _E2**3 / 1024) * math.sin(4 * phi)
        - (35 * _E2**3 / 3072) * math.sin(6 * phi)
    )
    easting = _K0 * n * (a + (1 - t + c) * a**3 / 6 + (5 - 18 * t + t * t + 72 * c - 58 * _EP2) * a**5 / 120)
    northing = _K0 * (
        m
        + n
        * math.tan(phi)
        * (a * a / 2 + (5 - t + 9 * c + 4 * c * c) * a**4 / 24 + (61 - 58 * t + t * t + 600 * c - 330 * _EP2) * a**6 / 720)
    )
    if lat < 0:
        northing += 10_000_000
    return zone, easting + 500_000, northing


def to_mgrs(lat: float, lng: float) -> str:
    """Format exactly like the app: ``36U UA 22034 87773``."""
    zone, easting, northing = to_utm(lat, lng)
    band = _BANDS[int((lat + 80) // 8)]
    col = _COL_SETS[(zone - 1) % 3][int(easting // 100_000) - 1]
    row_offset = 5 if zone % 2 == 0 else 0
    row = _ROW_LETTERS[(int(northing // 100_000) + row_offset) % 20]
    return f"{zone}{band} {col}{row} {int(easting % 100_000):05d} {int(northing % 100_000):05d}"


def mgrs_close(actual: str, expected: str, tolerance_m: int = 2) -> bool:
    """Same grid zone and 100 km square, easting/northing within ``tolerance_m`` metres.

    Used where the UI shows coordinates rounded to 5 decimals while MGRS is computed
    from the unrounded click position (a difference of up to ~1 m is expected).
    """
    try:
        gz_a, sq_a, e_a, n_a = actual.split()
        gz_e, sq_e, e_e, n_e = expected.split()
    except ValueError:
        return False
    return (
        (gz_a, sq_a) == (gz_e, sq_e)
        and abs(int(e_a) - int(e_e)) <= tolerance_m
        and abs(int(n_a) - int(n_e)) <= tolerance_m
    )


def point_in_polygon(lat: float, lng: float, ring: Sequence[tuple[float, float]]) -> bool:
    """Ray casting. ``ring`` is a sequence of (lng, lat) vertices, closed or open."""
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > lat) != (yj > lat) and lng < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def polygon_area_ha(ring: Sequence[tuple[float, float]]) -> float:
    """Shoelace area of a small (lng, lat) polygon, in hectares."""
    lat0 = math.radians(sum(p[1] for p in ring) / len(ring))
    pts = [(math.radians(x) * _A * math.cos(lat0), math.radians(y) * _A) for x, y in ring]
    area = 0.0
    for i, (x1, y1) in enumerate(pts):
        x2, y2 = pts[(i + 1) % len(pts)]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2 / 10_000
