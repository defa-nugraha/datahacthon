from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from app.core.config import Settings
from app.core.exceptions import BusinessValidationError, FeatureMismatchError, PredictionError
from app.schemas import ZonePredictionRequest
from app.services.feature_engineering import (
    aggregate_zone_features,
    build_model_frame,
    required_and_optional_raw_fields,
)
from app.services.model_loader import ZoneModelArtifacts, load_zone_artifacts


LOGGER = logging.getLogger(__name__)


class ZonePredictor:
    """Inference service for raw zone samples."""

    def __init__(self, artifacts: ZoneModelArtifacts, settings: Settings) -> None:
        self.artifacts = artifacts
        self.settings = settings
        self.required_raw_fields, self.optional_raw_fields = required_and_optional_raw_fields(
            artifacts.feature_columns
        )

    @classmethod
    def from_settings(cls, settings: Settings) -> "ZonePredictor":
        artifacts = load_zone_artifacts(settings)
        return cls(artifacts=artifacts, settings=settings)

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model_name": self.artifacts.model_name,
            "model_version": self.artifacts.model_version,
            "feature_set_type": self.artifacts.feature_set_type,
            "active_scenario": self.artifacts.active_scenario,
            "feature_columns": self.artifacts.feature_columns,
            "required_raw_fields": self.required_raw_fields,
            "optional_raw_fields": self.optional_raw_fields,
            "target_labels": self.artifacts.classes_,
            "minimum_samples_required": self.artifacts.minimum_samples_required,
            "recommended_minimum_samples": self.artifacts.recommended_minimum_samples,
            "artifact_paths": self.artifacts.artifact_paths,
            "fallback_assumptions": self.artifacts.fallback_assumptions
            + [
                "context_sample_count is approximated with the request sample_count during inference.",
                "context_cluster_count is fixed to 1 during inference because the client submits one ready-made zone.",
            ],
        }

    def _validate_business_rules(self, payload: ZonePredictionRequest) -> list[str]:
        sample_count = len(payload.samples)
        if sample_count < self.artifacts.minimum_samples_required:
            raise BusinessValidationError(
                "sample_count is below the minimum accepted threshold for zone inference.",
                details={
                    "sample_count": sample_count,
                    "minimum_samples_required": self.artifacts.minimum_samples_required,
                },
            )

        warnings: list[str] = []
        if (
            sample_count < self.artifacts.recommended_minimum_samples
            and not self.settings.allow_prediction_below_recommended_min_samples
        ):
            raise BusinessValidationError(
                "sample_count is below the recommended threshold and low-sample prediction is disabled by configuration.",
                details={
                    "sample_count": sample_count,
                    "recommended_minimum_samples": self.artifacts.recommended_minimum_samples,
                },
            )

        if sample_count < self.artifacts.recommended_minimum_samples:
            warnings.append(
                "sample_count is below the training-time recommended minimum; the service continues because low-sample prediction is enabled."
            )
        return warnings

    def _predict_probabilities(self, feature_frame: pd.DataFrame) -> tuple[list[str], list[float]]:
        model = self.artifacts.model
        if not hasattr(model, "predict_proba"):
            raise PredictionError("The loaded model does not expose predict_proba for ranked inference.")
        probabilities = model.predict_proba(feature_frame)[0]
        classes = list(model.classes_)
        return classes, [float(value) for value in probabilities]

    def predict(self, payload: ZonePredictionRequest, *, include_debug: bool = False) -> dict[str, Any]:
        warnings = self._validate_business_rules(payload)

        aggregation = aggregate_zone_features(
            samples=payload.samples,
            feature_columns=self.artifacts.feature_columns,
            recommended_minimum_samples=self.artifacts.recommended_minimum_samples,
        )
        warnings.extend(aggregation.warnings)

        feature_frame = build_model_frame(aggregation.model_input, self.artifacts.feature_columns)
        model_feature_names = list(getattr(self.artifacts.model, "feature_names_in_", []))
        if model_feature_names and model_feature_names != list(feature_frame.columns):
            raise FeatureMismatchError(
                "Feature frame columns do not match the serialized model feature order.",
                details={
                    "feature_frame_columns": feature_frame.columns.tolist(),
                    "model_feature_columns": model_feature_names,
                },
            )

        classes, probabilities = self._predict_probabilities(feature_frame)
        ranked_indices = sorted(range(len(probabilities)), key=lambda index: probabilities[index], reverse=True)
        top_k = min(payload.top_k, len(ranked_indices))
        top_predictions = [
            {
                "label": classes[index],
                "probability": probabilities[index],
            }
            for index in ranked_indices[:top_k]
        ]

        response: dict[str, Any] = {
            "status": "success",
            "zone_id": payload.zone_id,
            "sample_count": len(payload.samples),
            "aggregated_features": dict(aggregation.response_aggregated_features),
            "prediction": {
                "recommended_label": top_predictions[0]["label"],
                "confidence": top_predictions[0]["probability"],
                "top_k": top_predictions,
            },
            "model_info": self.get_model_info(),
            "warnings": list(dict.fromkeys(warnings)),
        }

        if include_debug:
            response["debug"] = {
                "model_input_ordered_features": dict(aggregation.response_aggregated_features),
                "imputed_model_features": aggregation.imputed_model_features,
                "all_numeric_aggregations": aggregation.full_numeric_aggregations,
                "all_categorical_aggregations": aggregation.full_categorical_aggregations,
            }

        LOGGER.info(
            "Zone prediction completed for zone_id=%s sample_count=%s predicted_label=%s confidence=%.4f",
            payload.zone_id,
            len(payload.samples),
            top_predictions[0]["label"],
            top_predictions[0]["probability"],
        )
        return response
