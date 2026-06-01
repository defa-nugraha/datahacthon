from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from app.core.exceptions import FeatureMismatchError
from app.schemas import ZoneSample
from scripts.zone_utils import normalize_soil_color


NUMERIC_AGGREGATION_SUFFIXES = (
    "_missing_ratio",
    "_median",
    "_range",
    "_count",
    "_mean",
    "_std",
    "_min",
    "_max",
    "_cv",
)
CATEGORICAL_AGGREGATION_SUFFIXES = (
    "_missing_ratio",
    "_dominant_ratio",
    "_mode",
    "_nunique",
)
SUPPORTED_RAW_NUMERIC_FIELDS = {
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
}
SUPPORTED_RAW_CATEGORICAL_FIELDS = {"soil_color"}
MANDATORY_RAW_FIELDS = ["ph", "nitrogen", "phosphorus", "potassium"]
OPTIONAL_RAW_FIELDS = [
    "zinc",
    "sulfur",
    "soil_color",
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
TRAINING_CONTEXT_FEATURES = {"sample_count", "context_sample_count", "context_cluster_count"}


@dataclass(frozen=True)
class ZoneAggregationResult:
    model_input: OrderedDict[str, Any]
    response_aggregated_features: OrderedDict[str, Any]
    full_numeric_aggregations: dict[str, dict[str, Any]]
    full_categorical_aggregations: dict[str, dict[str, Any]]
    warnings: list[str]
    imputed_model_features: list[str]


def _serializable_value(value: Any) -> Any:
    if isinstance(value, (np.floating, float)):
        if np.isnan(value):
            return None
        return float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if pd.isna(value):
        return None
    return value


def _dominant_value(series: pd.Series) -> Any:
    modes = series.mode(dropna=True)
    if not modes.empty:
        return modes.iloc[0]
    non_null = series.dropna()
    if not non_null.empty:
        return non_null.iloc[0]
    return None


def _compute_numeric_aggregations(series: pd.Series) -> dict[str, Any]:
    missing_ratio = float(series.isna().mean())
    count = int(series.count())
    mean = float(series.mean()) if count else np.nan
    std = float(series.std()) if count > 1 else 0.0
    minimum = float(series.min()) if count else np.nan
    maximum = float(series.max()) if count else np.nan
    median = float(series.median()) if count else np.nan
    value_range = maximum - minimum if count else np.nan
    cv = float(std / abs(mean)) if count and abs(mean) > 1e-9 else 0.0
    return {
        "mean": mean,
        "std": std,
        "min": minimum,
        "max": maximum,
        "median": median,
        "count": count,
        "range": value_range,
        "cv": cv,
        "missing_ratio": missing_ratio,
    }


def _compute_categorical_aggregations(series: pd.Series) -> dict[str, Any]:
    non_null = series.dropna()
    dominant_ratio = 0.0
    if not non_null.empty:
        dominant_ratio = float(non_null.value_counts(normalize=True).iloc[0])
    return {
        "mode": _dominant_value(series),
        "nunique": int(non_null.nunique()),
        "dominant_ratio": dominant_ratio,
        "missing_ratio": float(series.isna().mean()),
    }


def _parse_feature_name(feature_name: str) -> tuple[str, str]:
    if feature_name in TRAINING_CONTEXT_FEATURES:
        return ("context", feature_name)

    for suffix in sorted(NUMERIC_AGGREGATION_SUFFIXES + CATEGORICAL_AGGREGATION_SUFFIXES, key=len, reverse=True):
        if feature_name.endswith(suffix):
            raw_feature = feature_name[: -len(suffix)]
            aggregation_key = suffix.removeprefix("_")
            return raw_feature, aggregation_key
    raise FeatureMismatchError(
        f"Unsupported model feature `{feature_name}` for raw zone inference.",
        details={"feature_name": feature_name},
    )


def required_and_optional_raw_fields(feature_columns: list[str]) -> tuple[list[str], list[str]]:
    required = set(MANDATORY_RAW_FIELDS)
    optional = set(OPTIONAL_RAW_FIELDS)

    for feature_name in feature_columns:
        raw_feature, _ = _parse_feature_name(feature_name)
        if raw_feature in TRAINING_CONTEXT_FEATURES or raw_feature in {"context"}:
            continue
        if raw_feature not in SUPPORTED_RAW_NUMERIC_FIELDS and raw_feature not in SUPPORTED_RAW_CATEGORICAL_FIELDS:
            raise FeatureMismatchError(
                "The active model requires a raw feature that is not supported by the inference API.",
                details={"feature_name": feature_name, "raw_feature": raw_feature},
            )
        if raw_feature in SUPPORTED_RAW_NUMERIC_FIELDS or raw_feature in SUPPORTED_RAW_CATEGORICAL_FIELDS:
            optional.add(raw_feature)

    return sorted(required), sorted(optional - required)


def samples_to_frame(samples: list[ZoneSample]) -> pd.DataFrame:
    records = [sample.model_dump() for sample in samples]
    frame = pd.DataFrame(records)
    if "soil_color" in frame.columns:
        frame["soil_color"] = frame["soil_color"].map(
            lambda value: normalize_soil_color(value) if pd.notna(value) and value is not None else None
        )
    return frame


def aggregate_zone_features(
    *,
    samples: list[ZoneSample],
    feature_columns: list[str],
    recommended_minimum_samples: int,
) -> ZoneAggregationResult:
    frame = samples_to_frame(samples)
    warnings: list[str] = []

    sample_count = int(frame.shape[0])

    if sample_count < recommended_minimum_samples:
        warnings.append(
            "sample_count is below the recommended zone threshold used during training; prediction may be less stable."
        )

    numeric_stats = {
        field: _compute_numeric_aggregations(frame[field] if field in frame.columns else pd.Series([np.nan] * sample_count))
        for field in SUPPORTED_RAW_NUMERIC_FIELDS
    }
    categorical_stats = {
        field: _compute_categorical_aggregations(frame[field] if field in frame.columns else pd.Series([None] * sample_count))
        for field in SUPPORTED_RAW_CATEGORICAL_FIELDS
    }

    model_input: OrderedDict[str, Any] = OrderedDict()
    imputed_model_features: list[str] = []
    response_features: OrderedDict[str, Any] = OrderedDict()

    for feature_name in feature_columns:
        raw_feature, aggregation_key = _parse_feature_name(feature_name)

        if aggregation_key == "sample_count":
            value = sample_count
        elif feature_name == "context_sample_count":
            value = sample_count
            warnings.append(
                "context_sample_count is not derivable from request payload and was approximated with sample_count."
            )
        elif feature_name == "context_cluster_count":
            value = 1
            warnings.append(
                "context_cluster_count is not derivable from request payload and was fixed to 1 for inference."
            )
        elif raw_feature in numeric_stats:
            value = numeric_stats[raw_feature][aggregation_key]
        elif raw_feature in categorical_stats:
            value = categorical_stats[raw_feature][aggregation_key]
        else:
            raise FeatureMismatchError(
                f"Unsupported raw feature `{raw_feature}` required by `{feature_name}`.",
                details={"feature_name": feature_name, "raw_feature": raw_feature},
            )

        if value is None or (isinstance(value, float) and np.isnan(value)):
            imputed_model_features.append(feature_name)

        model_input[feature_name] = value
        response_features[feature_name] = _serializable_value(value)

    optional_missing_fields = [
        raw_field
        for raw_field in OPTIONAL_RAW_FIELDS
        if raw_field in frame.columns and frame[raw_field].isna().all()
    ]
    if optional_missing_fields:
        warnings.append(
            "Some optional raw fields were entirely missing and will be imputed by the preprocessing pipeline: "
            + ", ".join(sorted(optional_missing_fields))
        )

    if imputed_model_features:
        warnings.append(
            "The following model features could not be computed directly from the request and were left missing for pipeline imputation: "
            + ", ".join(imputed_model_features)
        )

    full_numeric = {
        raw_feature: {metric: _serializable_value(value) for metric, value in stats.items()}
        for raw_feature, stats in numeric_stats.items()
    }
    full_categorical = {
        raw_feature: {metric: _serializable_value(value) for metric, value in stats.items()}
        for raw_feature, stats in categorical_stats.items()
    }

    return ZoneAggregationResult(
        model_input=model_input,
        response_aggregated_features=response_features,
        full_numeric_aggregations=full_numeric,
        full_categorical_aggregations=full_categorical,
        warnings=list(dict.fromkeys(warnings)),
        imputed_model_features=sorted(set(imputed_model_features)),
    )


def build_model_frame(model_input: OrderedDict[str, Any], feature_columns: list[str]) -> pd.DataFrame:
    if list(model_input.keys()) != list(feature_columns):
        raise FeatureMismatchError(
            "Model input ordering does not match the active training feature order.",
            details={
                "model_input_keys": list(model_input.keys()),
                "feature_columns": feature_columns,
            },
        )
    frame = pd.DataFrame([model_input], columns=feature_columns)
    return frame
