"""Доменні моделі: моніторингові точки в тому вигляді, як їх зберігає застосунок."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from framework.data.ui_texts import UI

STORAGE_KEY = "agtech_monitoring_points_v1"


class PointType(StrEnum):
    SOIL_SAMPLE = "SOIL_SAMPLE"
    PESTS = "PESTS"
    PLANT_DISEASE = "PLANT_DISEASE"
    OTHER = "OTHER"

    @property
    def label(self) -> str:
        return POINT_TYPE_LABELS[self]


POINT_TYPE_LABELS: dict[PointType, str] = {
    PointType.SOIL_SAMPLE: UI.fields_gis.point_types.soil_sample,
    PointType.PESTS: UI.fields_gis.point_types.pests,
    PointType.PLANT_DISEASE: UI.fields_gis.point_types.plant_disease,
    PointType.OTHER: UI.fields_gis.point_types.other,
}


class Coordinates(BaseModel):
    lat: float
    lng: float


class MonitoringPoint(BaseModel):
    """Точка саме в тому вигляді, як застосунок тримає її в localStorage."""

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
