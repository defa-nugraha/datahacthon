from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _resolve_path(project_root: Path, raw_value: str | None, default_relative: str) -> Path:
    value = raw_value or default_relative
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (project_root / candidate).resolve()


@dataclass(frozen=True)
class Settings:
    project_root: Path
    zone_model_path: Path
    zone_preprocessing_path: Path
    zone_metrics_path: Path
    zone_metadata_path: Path
    zone_feature_summary_path: Path
    active_zone_scenario: str | None
    active_zone_model_version: str | None
    absolute_min_samples: int
    recommended_min_samples_override: int | None
    allow_prediction_below_recommended_min_samples: bool
    default_top_k: int
    log_level: str
    api_title: str
    api_version: str

    @classmethod
    def from_env(cls) -> "Settings":
        project_root = Path(
            os.getenv("PROJECT_ROOT", Path(__file__).resolve().parents[2])
        ).expanduser().resolve()
        recommended_override = os.getenv("ZONE_INFERENCE_RECOMMENDED_MIN_SAMPLES")

        return cls(
            project_root=project_root,
            zone_model_path=_resolve_path(
                project_root,
                os.getenv("ZONE_MODEL_PATH"),
                "artifacts/models/best_zone_model.joblib",
            ),
            zone_preprocessing_path=_resolve_path(
                project_root,
                os.getenv("ZONE_PREPROCESSING_PATH"),
                "artifacts/pipelines/zone_preprocessing_pipeline.joblib",
            ),
            zone_metrics_path=_resolve_path(
                project_root,
                os.getenv("ZONE_METRICS_PATH"),
                "artifacts/zone_model_metrics.json",
            ),
            zone_metadata_path=_resolve_path(
                project_root,
                os.getenv("ZONE_METADATA_PATH"),
                "data/processed/zone_dataset_metadata.json",
            ),
            zone_feature_summary_path=_resolve_path(
                project_root,
                os.getenv("ZONE_FEATURE_SUMMARY_PATH"),
                "artifacts/zone_feature_summary.csv",
            ),
            active_zone_scenario=os.getenv("ACTIVE_ZONE_SCENARIO") or None,
            active_zone_model_version=os.getenv("ACTIVE_ZONE_MODEL_VERSION") or None,
            absolute_min_samples=max(1, int(os.getenv("ZONE_INFERENCE_ABSOLUTE_MIN_SAMPLES", "3"))),
            recommended_min_samples_override=(
                int(recommended_override) if recommended_override is not None else None
            ),
            allow_prediction_below_recommended_min_samples=_parse_bool(
                os.getenv("ALLOW_PREDICTION_BELOW_RECOMMENDED_MIN_SAMPLES"),
                default=True,
            ),
            default_top_k=max(1, int(os.getenv("DEFAULT_TOP_K", "3"))),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            api_title=os.getenv(
                "API_TITLE",
                "Zone-Based Vegetation Recommendation API",
            ),
            api_version=os.getenv("API_VERSION", "1.0.0"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
