"""Contract of /samples/monitoring-points-sample.geojson (the file behind 'Завантажити демо-зразок')."""

import pytest

from framework.api.app_client import AppClient
from framework.data.models import PointFeatureCollection
from framework.storage import PointRecords

pytestmark = [pytest.mark.api, pytest.mark.regression]


@pytest.fixture(scope="module")
def sample(app: AppClient) -> PointRecords:
    return PointRecords.from_geojson(app.sample_geojson().json())


@pytest.mark.smoke
def test_sample_is_served_as_geojson(app: AppClient) -> None:
    response = app.sample_geojson()

    assert response.status == 200
    assert response.headers.get("content-type").startswith("application/geo+json")


def test_sample_matches_feature_collection_schema(app: AppClient) -> None:
    PointFeatureCollection.model_validate(app.sample_geojson().json())  # raises with details on mismatch


def test_sample_contains_six_demo_points(sample: PointRecords) -> None:
    assert sample.ids() == [
        "sample-pt-1", "sample-pt-2", "sample-pt-3", "sample-pt-4", "sample-pt-5", "sample-pt-6",
    ]


def test_sample_points_lie_inside_their_fields(sample: PointRecords) -> None:
    assert sample.outside_their_field() == []


def test_sample_mgrs_matches_coordinates(sample: PointRecords) -> None:
    assert sample.with_wrong_mgrs() == []


def test_sample_field_names_match_field_ids(sample: PointRecords) -> None:
    assert sample.with_wrong_field_name() == []


def test_sample_type_labels_match_types(sample: PointRecords) -> None:
    assert sample.with_wrong_type_label() == []


def test_sample_creation_dates_are_valid_and_in_the_past(sample: PointRecords) -> None:
    assert sample.created_in_future_or_invalid() == []
