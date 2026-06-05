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


def test_zone_strategy_endpoint_returns_fallback_strategy(client: TestClient) -> None:
    payload = _valid_zone_payload()
    payload["current_crop"] = "Jagung"
    payload["time_horizon_days"] = 14
    response = client.post("/insights/zone-strategy", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["strategic_insight"]["provider"] == "local_fallback"
    assert body["strategic_insight"]["recommended_actions"]


def test_care_advice_endpoint_matches_laravel_contract(client: TestClient) -> None:
    response = client.post(
        "/advice/care",
        json={
            "zone_id": "1",
            "zone_name": "Zona Alpha",
            "current_crop": "Jagung",
            "history_window_minutes": 60,
            "nutrient_history": [
                {
                    "timestamp": "2026-06-01T08:00:00+07:00",
                    "ph": 6.1,
                    "nitrogen": 82,
                    "phosphorus": 17,
                    "potassium": 76,
                    "soil_moisture": 24,
                },
                {
                    "timestamp": "2026-06-01T08:30:00+07:00",
                    "ph": 6.0,
                    "nitrogen": 80,
                    "phosphorus": 18,
                    "potassium": 75,
                    "soil_moisture": 23,
                },
            ],
            "current_snapshot": {
                "ph": {"mean": 6.05},
                "nitrogen": {"mean": 81},
                "phosphorus": {"mean": 17.5},
                "potassium": {"mean": 75.5},
                "soil_moisture": {"mean": 23.5},
            },
            "threshold_context": {"trigger_reason": "critical_low_soil_moisture"},
            "weather_forecast": {
                "source": "BMKG",
                "daily_forecast": [
                    {
                        "date": "2026-06-05",
                        "summary": "Hujan Ringan",
                        "temperature_max_c": 31,
                        "rain_risk": True,
                    },
                    {
                        "date": "2026-06-06",
                        "summary": "Hujan Sedang",
                        "temperature_max_c": 33,
                        "rain_risk": True,
                    },
                ],
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "local_fallback"
    assert body["summary"]
    assert body["urgency"] in {"low", "medium", "high"}
    assert body["recommendations"][0]["title"]
    assert body["observation_focus"]
    assert body["risk_flags"]


def test_weather_forecast_endpoint_returns_monthly_temperature_forecast(client: TestClient) -> None:
    response = client.post(
        "/forecast/weather",
        json={
            "zone_id": "tanah-ijen",
            "latitude": -8.0582181,
            "longitude": 114.2417552,
            "months": 3,
            "crop_name": "Jagung",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["zone_id"] == "tanah-ijen"
    assert body["horizon_months"] == 3
    assert len(body["forecast"]) == 3
    assert "suhu_maksimum_c" in body["forecast"][0]
    assert body["model_info"]["model_type"] == "ARIMA"
    assert body["warnings"]


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
