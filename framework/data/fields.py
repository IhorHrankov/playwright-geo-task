"""Reference data for the four static fields shipped with the application.

The values mirror the application's built-in GeoJSON (coordinates are [lng, lat]).
"""

from __future__ import annotations

from dataclasses import dataclass

LngLat = tuple[float, float]


@dataclass(frozen=True)
class Field:
    id: str
    name: str
    crop: str
    area_ha: float
    # Closed ring is not repeated: four corners in drawing order, (lng, lat).
    corners: tuple[LngLat, LngLat, LngLat, LngLat]

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """(min_lng, min_lat, max_lng, max_lat)."""
        lngs = [c[0] for c in self.corners]
        lats = [c[1] for c in self.corners]
        return min(lngs), min(lats), max(lngs), max(lats)

    def interior_point(self, u: float = 0.5, v: float = 0.5) -> tuple[float, float]:
        """Bilinear point inside the (convex) quadrilateral, u/v in (0, 1). Returns (lat, lng)."""
        if not (0 < u < 1 and 0 < v < 1):
            raise ValueError("u and v must be strictly between 0 and 1 to stay inside the field")
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = self.corners
        # corners: 0 = SW, 1 = SE, 2 = NE, 3 = NW
        lng = (1 - u) * (1 - v) * x0 + u * (1 - v) * x1 + u * v * x2 + (1 - u) * v * x3
        lat = (1 - u) * (1 - v) * y0 + u * (1 - v) * y1 + u * v * y2 + (1 - u) * v * y3
        return round(lat, 6), round(lng, 6)


FIELDS: tuple[Field, ...] = (
    Field(
        "field-1", "Поле №1 - Озима пшениця", "Озима пшениця", 68.4,
        ((30.485, 50.41), (30.505, 50.411), (30.508, 50.422), (30.487, 50.421)),
    ),
    Field(
        "field-2", "Поле №2 - Соняшник класичний", "Соняшник", 52.1,
        ((30.515, 50.412), (30.532, 50.413), (30.53, 50.424), (30.513, 50.423)),
    ),
    Field(
        "field-3", "Поле №3 - Кукурудза на зерно", "Кукурудза", 84.7,
        ((30.49, 50.428), (30.512, 50.429), (30.51, 50.44), (30.488, 50.439)),
    ),
    Field(
        "field-4", "Поле №4 - Ріпак озимий", "Ріпак", 41.3,
        ((30.52, 50.43), (30.538, 50.431), (30.536, 50.441), (30.518, 50.44)),
    ),
)

FIELDS_BY_ID: dict[str, Field] = {f.id: f for f in FIELDS}
DEFAULT_ACTIVE_FIELD = FIELDS[0]
