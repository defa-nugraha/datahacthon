from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.core.config import Settings
from app.core.exceptions import ArtifactLoadError, FeatureMismatchError


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ZoneModelArtifacts:
    model: Any
    preprocessing_pipeline: Any | None
    feature_columns: list[str]
    classes_: list[str]
    active_scenario: str
    feature_set_type: str
    model_name: str
    model_version: str | None
    metrics: dict[str, Any]
    metadata: dict[str, Any]
    feature_summary: pd.DataFrame
    minimum_samples_required: int
    recommended_minimum_samples: int
    artifact_paths: dict[str, str]
    fallback_assumptions: list[str]


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _resolve_active_scenario(metrics: dict[str, Any], requested: str | None) -> str:
    if requested and requested in metrics:
        return requested
    selected = metrics.get("selected_zone_scenario")
    if selected:
        return selected
    if "zone_mean_only" in metrics:
        return "zone_mean_only"
    if "zone_mean_plus_variability" in metrics:
        return "zone_mean_plus_variability"
    return "unknown"


def _feature_set_type(active_scenario: str) -> str:
    if active_scenario == "zone_mean_only":
        return "mean_only"
    if active_scenario == "zone_mean_plus_variability":
        return "mean_plus_variability"
    return "unknown"


def _derive_feature_columns(model: Any, metrics: dict[str, Any], active_scenario: str) -> list[str]:
    scenario_payload = metrics.get(active_scenario, {})
    feature_columns = scenario_payload.get("feature_columns")
    if feature_columns:
        return list(feature_columns)

    model_feature_names = getattr(model, "feature_names_in_", None)
    if model_feature_names is not None:
        return list(model_feature_names)

    preprocessor = getattr(getattr(model, "named_steps", {}).get("preprocessor", None), "feature_names_in_", None)
    if preprocessor is not None:
        return list(preprocessor)

    raise FeatureMismatchError(
        "Unable to determine model feature ordering from artifacts.",
        details={
            "active_scenario": active_scenario,
        },
    )


def _artifact_version(path: Path, configured_version: str | None) -> str | None:
    if configured_version:
        return configured_version
    if not path.exists():
        return None
    timestamp = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return timestamp.isoformat()


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _recommended_min_samples(settings: Settings, metadata: dict[str, Any]) -> int:
    if settings.recommended_min_samples_override is not None:
        return settings.recommended_min_samples_override

    builder_params = metadata.get("zone_builder_params", {})
    candidate = builder_params.get("min_samples_per_zone")
    if candidate is not None:
        return int(candidate)
    return max(settings.absolute_min_samples, 3)


def _artifact_paths(settings: Settings) -> dict[str, str]:
    return {
        "model_path": _display_path(settings.zone_model_path, settings.project_root),
        "preprocessing_path": _display_path(settings.zone_preprocessing_path, settings.project_root),
        "metrics_path": _display_path(settings.zone_metrics_path, settings.project_root),
        "metadata_path": _display_path(settings.zone_metadata_path, settings.project_root),
        "feature_summary_path": _display_path(settings.zone_feature_summary_path, settings.project_root),
    }


def load_zone_artifacts(settings: Settings) -> ZoneModelArtifacts:
    if not settings.zone_model_path.exists():
        raise ArtifactLoadError(
            "Zone model artifact not found.",
            details={"model_path": str(settings.zone_model_path)},
        )

    model = joblib.load(settings.zone_model_path)
    preprocessing_pipeline = None
    if settings.zone_preprocessing_path.exists():
        preprocessing_pipeline = joblib.load(settings.zone_preprocessing_path)

    metrics = _read_json_if_exists(settings.zone_metrics_path)
    metadata = _read_json_if_exists(settings.zone_metadata_path)
    feature_summary = _read_csv_if_exists(settings.zone_feature_summary_path)

    fallback_assumptions: list[str] = []
    if not metrics:
        fallback_assumptions.append(
            "zone_model_metrics.json was not available; feature ordering fell back to the loaded model artifact."
        )
    if not metadata:
        fallback_assumptions.append(
            "zone_dataset_metadata.json was not available; recommended sample threshold fell back to API config defaults."
        )
    if feature_summary.empty:
        fallback_assumptions.append(
            "zone_feature_summary.csv was not available; schema introspection for diagnostics is limited."
        )

    active_scenario = _resolve_active_scenario(metrics, settings.active_zone_scenario)
    feature_columns = _derive_feature_columns(model, metrics, active_scenario)
    feature_set_type = _feature_set_type(active_scenario)

    model_feature_names = list(getattr(model, "feature_names_in_", []))
    if model_feature_names and model_feature_names != feature_columns:
        raise FeatureMismatchError(
            "Feature ordering mismatch between the selected scenario metadata and the serialized model pipeline.",
            details={
                "metadata_feature_columns": feature_columns,
                "model_feature_columns": model_feature_names,
            },
        )

    preprocessor_feature_names = list(getattr(preprocessing_pipeline, "feature_names_in_", [])) if preprocessing_pipeline is not None else []
    if preprocessor_feature_names and preprocessor_feature_names != feature_columns:
        raise FeatureMismatchError(
            "Feature ordering mismatch between preprocessing artifact and the selected scenario metadata.",
            details={
                "metadata_feature_columns": feature_columns,
                "preprocessing_feature_columns": preprocessor_feature_names,
            },
        )

    scenario_payload = metrics.get(active_scenario, {})
    base_model_name = scenario_payload.get("best_model_name") or metrics.get("selected_zone_model_name", "zone_model")
    scenario_label = active_scenario if active_scenario != "unknown" else feature_set_type
    model_name = f"{base_model_name}_{scenario_label}"
    minimum_samples_required = max(settings.absolute_min_samples, 1)
    recommended_minimum_samples = max(
        minimum_samples_required,
        _recommended_min_samples(settings, metadata),
    )

    LOGGER.info(
        "Loaded zone inference artifacts with scenario=%s feature_set_type=%s feature_count=%s",
        active_scenario,
        feature_set_type,
        len(feature_columns),
    )

    return ZoneModelArtifacts(
        model=model,
        preprocessing_pipeline=preprocessing_pipeline,
        feature_columns=feature_columns,
        classes_=list(getattr(model, "classes_", [])),
        active_scenario=active_scenario,
        feature_set_type=feature_set_type,
        model_name=model_name,
        model_version=_artifact_version(settings.zone_model_path, settings.active_zone_model_version),
        metrics=metrics,
        metadata=metadata,
        feature_summary=feature_summary,
        minimum_samples_required=minimum_samples_required,
        recommended_minimum_samples=recommended_minimum_samples,
        artifact_paths=_artifact_paths(settings),
        fallback_assumptions=fallback_assumptions,
    )
