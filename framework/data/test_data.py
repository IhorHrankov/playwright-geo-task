"""Літеральні тестові дані та наперед обчислені очікувані значення.

Усе, з чим порівнює тест, записано тут вручну (MGRS, порядок списку, лічильники), тож тести
ніколи не обчислюють очікування тією самою логікою, що й застосунок.
Значення MGRS звірено із застосунком і незалежним конвертером.
"""

from __future__ import annotations

from pathlib import Path

from framework.data.fields import FIELD_1, FIELD_2, FIELD_3, FIELD_4
from framework.data.models import Coordinates, MonitoringPoint, PointType

TEST_DATA_DIR = Path(__file__).resolve().parents[2] / "test_data"
IMPORT_DIR = TEST_DATA_DIR / "import"
EXPECTED_DIR = TEST_DATA_DIR / "expected"

# ---------------------------------------------------------------- стандартний набір (5 точок)

SOIL_SAMPLE_FIELD_1 = MonitoringPoint(
    id="std-1",
    fieldId=FIELD_1.id,
    coordinates=Coordinates(lat=50.41295, lng=30.48955),
    mgrs="36U UA 21639 87558",
    type=PointType.SOIL_SAMPLE,
    description="Проба ґрунту на глибині 0-30 см",
    createdAt="2026-09-20T08:30:00.000Z",
)
PESTS_FIELD_1 = MonitoringPoint(
    id="std-2",
    fieldId=FIELD_1.id,
    coordinates=Coordinates(lat=50.41905, lng=30.5031),
    mgrs="36U UA 22625 88203",
    type=PointType.PESTS,
    description="Осередок клопа шкідливої черепашки",
    createdAt="2026-09-21T10:15:00.000Z",
)
DISEASE_FIELD_2 = MonitoringPoint(
    id="std-3",
    fieldId=FIELD_2.id,
    coordinates=Coordinates(lat=50.42105, lng=30.51765),
    mgrs="36U UA 23666 88391",
    type=PointType.PLANT_DISEASE,
    description="Ознаки білої гнилі на прикореневій шийці",
    createdAt="2026-09-22T14:45:00.000Z",
)
OTHER_FIELD_3 = MonitoringPoint(
    id="std-4",
    fieldId=FIELD_3.id,
    coordinates=Coordinates(lat=50.43095, lng=30.5061),
    mgrs="36U UA 22882 89519",
    type=PointType.OTHER,
    description="Контрольна точка метеостанції",
    createdAt="2026-09-23T16:20:00.000Z",
)
PESTS_FIELD_4 = MonitoringPoint(
    id="std-5",
    fieldId=FIELD_4.id,
    coordinates=Coordinates(lat=50.4333, lng=30.5248),
    mgrs="36U UA 24219 89736",
    type=PointType.PESTS,
    description="Пастки на ріпакового квіткоїда",
    createdAt="2026-09-24T07:10:00.000Z",
)

# Жодна з цих точок не поруч із центром поля, тому клік у центр ніколи не влучає в маркер.
STANDARD_POINTS = [SOIL_SAMPLE_FIELD_1, PESTS_FIELD_1, DISEASE_FIELD_2, OTHER_FIELD_3, PESTS_FIELD_4]

STANDARD_DESCRIPTIONS_NEWEST_FIRST = [
    "Пастки на ріпакового квіткоїда",
    "Контрольна точка метеостанції",
    "Ознаки білої гнилі на прикореневій шийці",
    "Осередок клопа шкідливої черепашки",
    "Проба ґрунту на глибині 0-30 см",
]
STANDARD_DESCRIPTIONS_OLDEST_FIRST = [
    "Проба ґрунту на глибині 0-30 см",
    "Осередок клопа шкідливої черепашки",
    "Ознаки білої гнилі на прикореневій шийці",
    "Контрольна точка метеостанції",
    "Пастки на ріпакового квіткоїда",
]
STANDARD_IDS = ["std-1", "std-2", "std-3", "std-4", "std-5"]

# ------------------------------------------------------------------- точки для окремих сценаріїв

POINT_WITH_QUOTES = MonitoringPoint(
    id="qa-quotes",
    fieldId=FIELD_1.id,
    coordinates=Coordinates(lat=50.41295, lng=30.48955),
    mgrs="36U UA 21639 87558",
    type=PointType.OTHER,
    description='Опис з "лапками"; крапкою з комою',
    createdAt="2026-10-01T10:00:00.000Z",
)
POINT_WITH_FORMULA = MonitoringPoint(
    id="qa-formula",
    fieldId=FIELD_1.id,
    coordinates=Coordinates(lat=50.41295, lng=30.48955),
    mgrs="36U UA 21639 87558",
    type=PointType.OTHER,
    description='=HYPERLINK("http://example.com","QA CSV injection")',
    createdAt="2026-10-01T10:00:00.000Z",
)
DISEASE_WITH_DETAILS = MonitoringPoint(
    id="qa-popup",
    fieldId=FIELD_1.id,
    coordinates=Coordinates(lat=50.41295, lng=30.48955),
    mgrs="36U UA 21639 87558",
    type=PointType.PLANT_DISEASE,
    description="Фузаріоз колосу",
    createdAt="2026-10-01T10:00:00.000Z",
)

# ------------------------------------------------------------------------- тексти й межі

DESCRIPTION_250_CHARS = "щ" * 250
DESCRIPTION_251_CHARS = "щ" * 251

# ---------------------------------------------------------------------------- файли

EXPECTED_STANDARD_GEOJSON = EXPECTED_DIR / "standard_points.geojson"
EXPECTED_STANDARD_CSV = EXPECTED_DIR / "standard_points.csv"

# файли імпорту: валідні
VALID_POINTS_GEOJSON = IMPORT_DIR / "valid_points.geojson"  # std-1..std-4
VALID_POINTS_CSV = IMPORT_DIR / "valid_points.csv"  # std-1..std-4
COMMA_ENGLISH_HEADERS_CSV = IMPORT_DIR / "comma_english_headers.csv"  # qa-comma, без значення в колонці MGRS
ONE_POINT_GEOJSON = IMPORT_DIR / "one_point.geojson"

# файли імпорту: пошкоджені (застосунок відхиляє)
INVALID_JSON_GEOJSON = IMPORT_DIR / "malformed" / "invalid_json.geojson"
NOT_FEATURE_COLLECTION_GEOJSON = IMPORT_DIR / "malformed" / "not_feature_collection.geojson"
NO_POINT_FEATURES_GEOJSON = IMPORT_DIR / "malformed" / "no_point_features.geojson"
HEADER_ONLY_CSV = IMPORT_DIR / "malformed" / "header_only.csv"
WITHOUT_LAT_LNG_CSV = IMPORT_DIR / "malformed" / "without_lat_lng.csv"
NON_NUMERIC_COORDINATES_CSV = IMPORT_DIR / "malformed" / "non_numeric_coordinates.csv"

# файли імпорту: невалідні дані, які застосунок приймає (задокументовані дефекти)
OUTSIDE_FIELDS_CSV = IMPORT_DIR / "outside_fields.csv"  # BUG-01
OUTSIDE_FIELDS_GEOJSON = IMPORT_DIR / "outside_fields.geojson"  # BUG-01, BUG-04
FIELD_MISMATCH_CSV = IMPORT_DIR / "field_mismatch.csv"  # BUG-01
INVALID_COORDINATES_CSV = IMPORT_DIR / "invalid_coordinates.csv"  # BUG-02
DUPLICATE_IDS_CSV = IMPORT_DIR / "duplicate_ids.csv"  # BUG-03
INVALID_DATE_CSV = IMPORT_DIR / "invalid_date.csv"  # BUG-04
FAKE_MGRS_CSV = IMPORT_DIR / "fake_mgrs.csv"  # BUG-05
