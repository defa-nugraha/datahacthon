from __future__ import annotations

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.exceptions import ArtifactLoadError, FeatureMismatchError
from app.main import create_app
from app.schemas import ZonePredictionRequest
from app.services.feature_engineering import required_and_optional_raw_fields
from app.services.model_loader import load_zone_artifacts
from app.services.predictor import ZonePredictor


def _sample(point_id: str, **overrides):
    payload = {
        "point_id": point_id,
        "ph": 6.4,
        "nitrogen": 100.0,
        "phosphorus": 39.0,
        "potassium": 70.0,
        "temperature_mean": 19.2,
        "rainfall_mean": 6.2,
    }
    payload.update(overrides)
    return payload


def _valid_zone_payload(sample_count: int = 8) -> dict:
    return {
        "zone_id": "zone_test",
        "top_k": 3,
        "samples": [_sample(f"P{i + 1}") for i in range(sample_count)],
    }


@pytest.fixture
def client() -> TestClient:
    app = create_app(get_settings())
    with TestClient(app) as test_client:
        yield test_client


def test_predict_zone_valid_request(client: TestClient) -> None:
    response = client.post("/predict/zone", json=_valid_zone_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["zone_id"] == "zone_test"
    assert body["sample_count"] == 8
    assert "ph_mean" in body["aggregated_features"]
    assert body["prediction"]["recommended_label"] in body["model_info"]["target_labels"]
    assert len(body["prediction"]["top_k"]) == 3


def test_predict_zone_rejects_too_few_samples(client: TestClient) -> None:
    response = client.post("/predict/zone", json=_valid_zone_payload(sample_count=2))
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "business_validation_error"
    assert body["error"]["details"]["minimum_samples_required"] == 3


def test_predict_zone_missing_required_field_returns_422(client: TestClient) -> None:
    payload = _valid_zone_payload()
    del payload["samples"][0]["phosphorus"]
    response = client.post("/predict/zone", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "request_validation_error"


def test_predict_zone_invalid_numeric_value_raises_validation_error() -> None:
    payload = _valid_zone_payload()
    payload["samples"][0]["ph"] = float("nan")
    with pytest.raises(ValidationError):
        ZonePredictionRequest(**payload)


def test_predictor_returns_prediction_successfully() -> None:
    predictor = ZonePredictor.from_settings(get_settings())
    payload = ZonePredictionRequest(**_valid_zone_payload())
    result = predictor.predict(payload)
    assert result["status"] == "success"
    assert result["model_info"]["feature_set_type"] == "mean_plus_variability"
    assert result["prediction"]["recommended_label"] in predictor.artifacts.classes_


def test_feature_mismatch_detection_raises_error() -> None:
    with pytest.raises(FeatureMismatchError):
        required_and_optional_raw_fields(["unsupported_feature_mean"])


def test_artifact_model_not_found_raises_error(tmp_path) -> None:
    broken_settings = replace(
        get_settings(),
        zone_model_path=tmp_path / "missing-model.joblib",
    )
    with pytest.raises(ArtifactLoadError):
        load_zone_artifacts(broken_settings)
