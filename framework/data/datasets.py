"""Named, deterministic datasets seeded into localStorage before a test starts."""

from __future__ import annotations

from datetime import UTC, datetime

from framework.data.builders import make_point
from framework.data.fields import FIELDS
from framework.data.models import MonitoringPoint, PointType

F1, F2, F3, F4 = FIELDS


def standard_points() -> list[MonitoringPoint]:
    """Five points, every type present, distinct dates, none near a field centre (u=v=0.5 stays free)."""
    return [
        make_point(F1, u=0.2, v=0.25, point_type=PointType.SOIL_SAMPLE, point_id="std-1",
                   description="Проба ґрунту на глибині 0-30 см",
                   created_at=datetime(2026, 9, 20, 8, 30, tzinfo=UTC)),
        make_point(F1, u=0.8, v=0.75, point_type=PointType.PESTS, point_id="std-2",
                   description="Осередок клопа шкідливої черепашки",
                   created_at=datetime(2026, 9, 21, 10, 15, tzinfo=UTC)),
        make_point(F2, u=0.25, v=0.8, point_type=PointType.PLANT_DISEASE, point_id="std-3",
                   description="Ознаки білої гнилі на прикореневій шийці",
                   created_at=datetime(2026, 9, 22, 14, 45, tzinfo=UTC)),
        make_point(F3, u=0.75, v=0.2, point_type=PointType.OTHER, point_id="std-4",
                   description="Контрольна точка метеостанції",
                   created_at=datetime(2026, 9, 23, 16, 20, tzinfo=UTC)),
        make_point(F4, u=0.3, v=0.3, point_type=PointType.PESTS, point_id="std-5",
                   description="Пастки на ріпакового квіткоїда",
                   created_at=datetime(2026, 9, 24, 7, 10, tzinfo=UTC)),
    ]


def empty() -> list[MonitoringPoint]:
    return []
