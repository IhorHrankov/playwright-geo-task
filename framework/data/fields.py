"""Чотири статичні поля застосунку (значення повторюють GeoJSON застосунку)."""

from __future__ import annotations

from dataclasses import dataclass

from framework.data.ui_texts import UI

LngLat = tuple[float, float]


@dataclass(frozen=True)
class Field:
    id: str
    name: str
    crop: str
    area_ha: float
    # чотири кути в порядку малювання (SW, SE, NE, NW), кожен (lng, lat)
    corners: tuple[LngLat, LngLat, LngLat, LngLat]
    # індекс поля у списку та його полігона на карті
    order: int

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """(min_lng, min_lat, max_lng, max_lat)."""
        lngs = [c[0] for c in self.corners]
        lats = [c[1] for c in self.corners]
        return min(lngs), min(lats), max(lngs), max(lats)

    def interior_point(self, u: float = 0.5, v: float = 0.5) -> tuple[float, float]:
        """Білінійна точка всередині чотирикутника, u/v в (0, 1). Повертає (lat, lng)."""
        if not (0 < u < 1 and 0 < v < 1):
            raise ValueError("u і v мають бути строго між 0 і 1, щоб лишатися всередині поля")
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = self.corners
        lng = (1 - u) * (1 - v) * x0 + u * (1 - v) * x1 + u * v * x2 + (1 - u) * v * x3
        lat = (1 - u) * (1 - v) * y0 + u * (1 - v) * y1 + u * v * y2 + (1 - u) * v * y3
        return round(lat, 6), round(lng, 6)


FIELD_1 = Field(
    "field-1",
    UI.fields_gis.fields.field_1.name,
    UI.fields_gis.fields.field_1.crop,
    68.4,
    ((30.485, 50.41), (30.505, 50.411), (30.508, 50.422), (30.487, 50.421)),
    order=0,
)
FIELD_2 = Field(
    "field-2",
    UI.fields_gis.fields.field_2.name,
    UI.fields_gis.fields.field_2.crop,
    52.1,
    ((30.515, 50.412), (30.532, 50.413), (30.53, 50.424), (30.513, 50.423)),
    order=1,
)
FIELD_3 = Field(
    "field-3",
    UI.fields_gis.fields.field_3.name,
    UI.fields_gis.fields.field_3.crop,
    84.7,
    ((30.49, 50.428), (30.512, 50.429), (30.51, 50.44), (30.488, 50.439)),
    order=2,
)
FIELD_4 = Field(
    "field-4",
    UI.fields_gis.fields.field_4.name,
    UI.fields_gis.fields.field_4.crop,
    41.3,
    ((30.52, 50.43), (30.538, 50.431), (30.536, 50.441), (30.518, 50.44)),
    order=3,
)

FIELDS: tuple[Field, ...] = (FIELD_1, FIELD_2, FIELD_3, FIELD_4)
FIELDS_BY_ID: dict[str, Field] = {f.id: f for f in FIELDS}
