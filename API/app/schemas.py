from __future__ import annotations

import math
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


NUMERIC_FIELDS = [
    "ph",
    "nitrogen",
    "phosphorus",
    "potassium",
    "zinc",
    "sulfur",
    "soil_moisture_surface",
    "wind_speed_10m",
    "specific_humidity_mean",
    "temperature_mean",
    "temperature_seasonal_range",
    "rainfall_mean",
    "rainfall_total_proxy",
    "cloud_amount",
    "surface_pressure",
]

ZONE_SAMPLE_EXAMPLE_MINIMAL = {
    "point_id": "A1",
    "ph": 6.5,
    "nitrogen": 100.0,
    "phosphorus": 40.0,
    "potassium": 70.0,
    "temperature_mean": 19.3,
    "rainfall_mean": 6.2,
}

ZONE_SAMPLE_EXAMPLE_EXTENDED = {
    "point_id": "A1",
    "soil_color": "reddish brown",
    "ph": 6.5,
    "nitrogen": 100.0,
    "phosphorus": 40.0,
    "potassium": 70.0,
    "zinc": 1.2,
    "sulfur": 10.0,
    "soil_moisture_surface": 0.68,
    "wind_speed_10m": 2.4,
    "specific_humidity_mean": 10.8,
    "temperature_mean": 19.3,
    "temperature_seasonal_range": 23.7,
    "rainfall_mean": 6.2,
    "rainfall_total_proxy": 24.8,
    "cloud_amount": 51.0,
    "surface_pressure": 79.4,
}

ZONE_PREDICTION_REQUEST_OPENAPI_EXAMPLES = {
    "minimal_zone_request": {
        "summary": "Contoh minimal dengan fitur tanah inti",
        "description": (
            "Contoh request paling minimal yang tetap valid untuk model zona aktif. "
            "Fitur opsional akan diimputasi oleh preprocessing pipeline."
        ),
        "value": {
            "zone_id": "zona_a",
            "top_k": 3,
            "samples": [
                ZONE_SAMPLE_EXAMPLE_MINIMAL,
                {
                    "point_id": "A2",
                    "ph": 6.4,
                    "nitrogen": 102.0,
                    "phosphorus": 39.0,
                    "potassium": 68.0,
                    "temperature_mean": 19.1,
                    "rainfall_mean": 6.1,
                },
                {
                    "point_id": "A3",
                    "ph": 6.6,
                    "nitrogen": 98.0,
                    "phosphorus": 41.0,
                    "potassium": 72.0,
                    "temperature_mean": 19.4,
                    "rainfall_mean": 6.3,
                },
            ],
        },
    },
    "extended_zone_request": {
        "summary": "Contoh lengkap dengan fitur opsional",
        "description": (
            "Contoh request yang lebih lengkap dan lebih dekat dengan feature contract model zona. "
            "Ini cocok dipakai untuk uji coba di Swagger UI."
        ),
        "value": {
            "zone_id": "zona_b",
            "top_k": 3,
            "samples": [
                ZONE_SAMPLE_EXAMPLE_EXTENDED,
                {
                    "point_id": "B2",
                    "soil_color": "reddish brown",
                    "ph": 6.4,
                    "nitrogen": 101.0,
                    "phosphorus": 39.5,
                    "potassium": 69.5,
                    "zinc": 1.1,
                    "sulfur": 10.5,
                    "soil_moisture_surface": 0.66,
                    "wind_speed_10m": 2.5,
                    "specific_humidity_mean": 10.7,
                    "temperature_mean": 19.1,
                    "temperature_seasonal_range": 23.5,
                    "rainfall_mean": 6.1,
                    "rainfall_total_proxy": 24.4,
                    "cloud_amount": 50.0,
                    "surface_pressure": 79.2,
                },
                {
                    "point_id": "B3",
                    "soil_color": "red",
                    "ph": 6.6,
                    "nitrogen": 99.0,
                    "phosphorus": 40.5,
                    "potassium": 71.0,
                    "zinc": 1.2,
                    "sulfur": 9.5,
                    "soil_moisture_surface": 0.69,
                    "wind_speed_10m": 2.3,
                    "specific_humidity_mean": 10.9,
                    "temperature_mean": 19.4,
                    "temperature_seasonal_range": 23.8,
                    "rainfall_mean": 6.3,
                    "rainfall_total_proxy": 25.2,
                    "cloud_amount": 52.0,
                    "surface_pressure": 79.5,
                },
            ],
        },
    },
}


class ZoneSample(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={"example": ZONE_SAMPLE_EXAMPLE_EXTENDED},
    )

    point_id: str = Field(..., min_length=1, description="Unique point identifier inside the request zone.")
    soil_color: str | None = Field(
        default=None,
        description="Optional normalized or raw soil color. Example: red, reddish brown, dark brown.",
    )
    ph: float = Field(..., description="Soil pH, expected in the 0-14 range.")
    nitrogen: float = Field(..., ge=0, description="Nitrogen measurement for the sample point.")
    phosphorus: float = Field(..., ge=0, description="Phosphorus measurement for the sample point.")
    potassium: float = Field(..., ge=0, description="Potassium measurement for the sample point.")
    zinc: float | None = Field(default=None, ge=0, description="Optional zinc measurement for the sample point.")
    sulfur: float | None = Field(default=None, ge=0, description="Optional sulfur measurement for the sample point.")
    soil_moisture_surface: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Optional top-layer soil moisture in the 0-1 range.",
    )
    wind_speed_10m: float | None = Field(default=None, description="Optional wind speed at 10 meters.")
    specific_humidity_mean: float | None = Field(default=None, ge=0, description="Optional mean specific humidity.")
    temperature_mean: float | None = Field(default=None, description="Optional mean temperature.")
    temperature_seasonal_range: float | None = Field(
        default=None,
        ge=0,
        description="Optional seasonal temperature range.",
    )
    rainfall_mean: float | None = Field(default=None, ge=0, description="Optional mean rainfall.")
    rainfall_total_proxy: float | None = Field(default=None, ge=0, description="Optional total rainfall proxy.")
    cloud_amount: float | None = Field(default=None, ge=0, description="Optional cloud amount.")
    surface_pressure: float | None = Field(default=None, ge=0, description="Optional surface pressure.")

    @field_validator(*NUMERIC_FIELDS, mode="before")
    @classmethod
    def reject_boolean_numeric_values(cls, value: Any) -> Any:
        if isinstance(value, bool):
            raise ValueError("must be a numeric value, not boolean.")
        return value

    @field_validator(*NUMERIC_FIELDS)
    @classmethod
    def validate_finite_numbers(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if not math.isfinite(value):
            raise ValueError("must be a finite numeric value.")
        return value

    @field_validator("ph")
    @classmethod
    def validate_ph_range(cls, value: float) -> float:
        if not 0 <= value <= 14:
            raise ValueError("must be between 0 and 14.")
        return value


class ZonePredictionRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                ZONE_PREDICTION_REQUEST_OPENAPI_EXAMPLES["minimal_zone_request"]["value"],
                ZONE_PREDICTION_REQUEST_OPENAPI_EXAMPLES["extended_zone_request"]["value"],
            ]
        },
    )

    zone_id: str = Field(..., min_length=1, description="Client-side identifier for the zone being predicted.")
    samples: list[ZoneSample] = Field(..., min_length=1, description="Raw point samples belonging to the same zone.")
    top_k: int = Field(default=3, ge=1, le=10, description="Maximum number of ranked predictions to return.")

    @model_validator(mode="after")
    def validate_unique_point_ids(self) -> "ZonePredictionRequest":
        point_ids = [sample.point_id for sample in self.samples]
        if len(point_ids) != len(set(point_ids)):
            raise ValueError("point_id values must be unique within one zone request.")
        return self


class ZoneStrategyRequest(ZonePredictionRequest):
    current_crop: str | None = Field(
        default=None,
        description="Optional currently planted crop for intervention-oriented advice.",
    )
    time_horizon_days: int = Field(
        default=14,
        ge=1,
        le=120,
        description="Planning horizon for the strategic agronomic recommendations.",
    )


class TopKPrediction(BaseModel):
    label: str
    probability: float


class PredictionPayload(BaseModel):
    recommended_label: str
    confidence: float
    top_k: list[TopKPrediction]


class ModelInfoPayload(BaseModel):
    model_name: str
    model_version: str | None = None
    feature_set_type: str
    active_scenario: str
    feature_columns: list[str]
    required_raw_fields: list[str]
    optional_raw_fields: list[str]
    target_labels: list[str]
    minimum_samples_required: int
    recommended_minimum_samples: int
    artifact_paths: dict[str, str]
    fallback_assumptions: list[str]


class ZonePredictionResponse(BaseModel):
    status: str
    zone_id: str
    sample_count: int
    aggregated_features: dict[str, Any]
    prediction: PredictionPayload
    model_info: ModelInfoPayload
    warnings: list[str]


class ZonePredictionDebugResponse(ZonePredictionResponse):
    debug: dict[str, Any]


class StrategyActionItem(BaseModel):
    title: str
    rationale: str
    timeframe: str
    expected_impact: str


class StrategicInsightPayload(BaseModel):
    provider: str
    summary: str
    urgency: str
    reasoning: list[str]
    recommended_actions: list[StrategyActionItem]
    monitoring_focus: list[str]
    risks: list[str]


class ZoneStrategyResponse(BaseModel):
    status: str
    zone_id: str
    sample_count: int
    aggregated_features: dict[str, Any]
    prediction: PredictionPayload
    strategic_insight: StrategicInsightPayload
    model_info: ModelInfoPayload
    warnings: list[str]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    active_model_name: str | None = None
    detail: str | None = None


class APIErrorBody(BaseModel):
    code: str
    message: str
    details: Any = None


class ErrorResponse(BaseModel):
    status: str
    error: APIErrorBody
