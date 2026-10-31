"""Contract of /samples/monitoring-points-sample.geojson (the file behind "Завантажити демо-зразок")."""

from __future__ import annotations

from datetime import datetime

import pytest

from framework.api.app_client import AppClient
from framework.data.fields import FIELDS_BY_ID
from framework.data.models import PointFeatureCollection, PointType
from framework.utils.geo import point_in_polygon, to_mgrs

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.fixture(scope="module")
def sample(app: AppClient) -> PointFeatureCollection:
    response = app.sample_geojson()
    assert response.status == 200, response.status_text
    return PointFeatureCollection.model_validate(response.json())


@pytest.mark.smoke
def test_sample_is_served_as_geojson(app: AppClient) -> None:
    response = app.sample_geojson()

    assert response.status == 200
    assert response.headers["content-type"].startswith("application/geo+json")


def test_sample_matches_schema(sample: PointFeatureCollection) -> None:
    assert len(sample.features) == 6  # the UI announces "Завантажено 6 точок"


def test_sample_ids_are_unique(sample: PointFeatureCollection) -> None:
    ids = [f.properties.id for f in sample.features]
    assert len(ids) == len(set(ids))


def test_each_point_belongs_to_known_field_and_lies_inside_it(sample: PointFeatureCollection) -> None:
    for f in sample.features:
        lng, lat = f.geometry.coordinates
        field = FIELDS_BY_ID.get(f.properties.fieldId)
        assert field, f"{f.properties.id}: unknown field {f.properties.fieldId}"
        assert f.properties.fieldName == field.name
        assert point_in_polygon(lat, lng, field.corners), f"{f.properties.id} is outside {field.id}"


def test_mgrs_matches_coordinates(sample: PointFeatureCollection) -> None:
    for f in sample.features:
        lng, lat = f.geometry.coordinates
        assert f.properties.mgrs == to_mgrs(lat, lng), f.properties.id


def test_type_label_matches_type(sample: PointFeatureCollection) -> None:
    for f in sample.features:
        assert f.properties.typeLabel == PointType(f.properties.type).label


def test_created_at_is_in_the_past(sample: PointFeatureCollection) -> None:
    now = datetime.now().astimezone()
    for f in sample.features:
        assert datetime.fromisoformat(f.properties.createdAt.replace("Z", "+00:00")) < now
