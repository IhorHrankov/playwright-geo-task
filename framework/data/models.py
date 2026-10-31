"""Domain models: monitoring points as stored by the app, plus GeoJSON export/import contracts."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

STORAGE_KEY = "agtech_monitoring_points_v1"


class PointType(str, Enum):
    SOIL_SAMPLE = "SOIL_SAMPLE"
    PESTS = "PESTS"
    PLANT_DISEASE = "PLANT_DISEASE"
    OTHER = "OTHER"

    @property
    def label(self) -> str:
        return POINT_TYPE_LABELS[self]


POINT_TYPE_LABELS: dict[PointType, str] = {
    PointType.SOIL_SAMPLE: "Проба ґрунту",
    PointType.PESTS: "Шкідники",
    PointType.PLANT_DISEASE: "Хвороби рослин",
    PointType.OTHER: "Інше",
}


class Coordinates(BaseModel):
    lat: float
    lng: float


class MonitoringPoint(BaseModel):
    """A point exactly as the app keeps it in localStorage."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    id: str
    field_id: str = Field(alias="fieldId")
    coordinates: Coordinates
    mgrs: str
    type: PointType
    description: str | None = None
    created_at: str = Field(alias="createdAt")

    def to_storage(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


# ---------- GeoJSON contract (export file and /samples/*.geojson) ----------


class PointGeometry(BaseModel):
    type: Literal["Point"]
    coordinates: tuple[float, float]  # [lng, lat]

    @field_validator("coordinates")
    @classmethod
    def _in_wgs84_range(cls, value: tuple[float, float]) -> tuple[float, float]:
        lng, lat = value
        if not (-180 <= lng <= 180 and -90 <= lat <= 90):
            raise ValueError(f"coordinates out of WGS84 range: {value}")
        return value


class PointProperties(BaseModel):
    id: str
    fieldId: str
    fieldName: str
    type: PointType
    typeLabel: str
    mgrs: str
    description: str
    createdAt: str

    @field_validator("createdAt")
    @classmethod
    def _iso8601(cls, value: str) -> str:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


class PointFeature(BaseModel):
    type: Literal["Feature"]
    geometry: PointGeometry
    properties: PointProperties


class PointFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"]
    features: list[PointFeature]
