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


class ZoneSample(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    point_id: str = Field(..., min_length=1, description="Unique point identifier inside the request zone.")
    soil_color: str | None = Field(
        default=None,
        description="Optional normalized or raw soil color. Example: red, reddish brown, dark brown.",
    )
    ph: float = Field(..., description="Soil pH, expected in the 0-14 range.")
    nitrogen: float = Field(..., ge=0, description="Nitrogen measurement for the sample point.")
    phosphorus: float = Field(..., ge=0, description="Phosphorus measurement for the sample point.")
    potassium: float = Field(..., ge=0, description="Potassium measurement for the sample point.")
    zinc: float = Field(..., ge=0, description="Zinc measurement for the sample point.")
    sulfur: float = Field(..., ge=0, description="Sulfur measurement for the sample point.")
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
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    zone_id: str = Field(..., min_length=1, description="Client-side identifier for the zone being predicted.")
    samples: list[ZoneSample] = Field(..., min_length=1, description="Raw point samples belonging to the same zone.")
    top_k: int = Field(default=3, ge=1, le=10, description="Maximum number of ranked predictions to return.")

    @model_validator(mode="after")
    def validate_unique_point_ids(self) -> "ZonePredictionRequest":
        point_ids = [sample.point_id for sample in self.samples]
        if len(point_ids) != len(set(point_ids)):
            raise ValueError("point_id values must be unique within one zone request.")
        return self


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
