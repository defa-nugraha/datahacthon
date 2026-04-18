from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "datasets"
CSV_DIR = DATASETS_DIR / "csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODELS_DIR = ARTIFACTS_DIR / "models"
PIPELINES_DIR = ARTIFACTS_DIR / "pipelines"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

ZONE_NOTEBOOK_PATH = NOTEBOOKS_DIR / "zone_based_vegetation_recommendation.ipynb"

PRIMARY_DATASET_PATH = CSV_DIR / "mendeley_8v757rr4st_crop_recommendation_soil_weather.csv"

TARGET_COLUMN = "target_crop"
ZONE_TARGET_COLUMN = "zone_target"
RANDOM_STATE = 42

ZONE_DATASET_PATH = PROCESSED_DIR / "zone_dataset.csv"
ZONE_DATASET_MINIMAL_PATH = PROCESSED_DIR / "zone_dataset_minimal.csv"
ZONE_DATASET_EXTENDED_PATH = PROCESSED_DIR / "zone_dataset_extended.csv"
ZONE_METADATA_PATH = PROCESSED_DIR / "zone_dataset_metadata.json"

ZONE_MODELING_STRATEGY_PATH = ARTIFACTS_DIR / "zone_modeling_strategy.md"
ZONE_FEATURE_SUMMARY_PATH = ARTIFACTS_DIR / "zone_feature_summary.csv"
ZONE_MODEL_METRICS_PATH = ARTIFACTS_DIR / "zone_model_metrics.json"
ZONE_FEATURE_IMPORTANCE_PATH = ARTIFACTS_DIR / "zone_feature_importance.csv"
ZONE_PREDICTION_SAMPLES_PATH = ARTIFACTS_DIR / "zone_prediction_samples.csv"
MODEL_SELECTION_ANALYSIS_PATH = ARTIFACTS_DIR / "model_selection_analysis.md"
MODEL_COMPARISON_PATH = ARTIFACTS_DIR / "model_comparison.csv"
BEST_MODEL_METRICS_PATH = ARTIFACTS_DIR / "best_model_metrics.json"
BEST_MODEL_SUMMARY_PATH = ARTIFACTS_DIR / "best_model_summary.md"
BEST_MODEL_CONFUSION_MATRIX_PATH = ARTIFACTS_DIR / "confusion_matrix_best_model.png"
BEST_MODEL_CLASSIFICATION_REPORT_PATH = ARTIFACTS_DIR / "classification_report_best_model.txt"
BEST_MODEL_FEATURE_IMPORTANCE_PATH = ARTIFACTS_DIR / "feature_importance_best_model.csv"

BEST_ZONE_MODEL_PATH = MODELS_DIR / "best_zone_model.joblib"
BEST_ZONE_PREPROCESSOR_PATH = PIPELINES_DIR / "zone_preprocessing_pipeline.joblib"
BEST_ZONE_PIPELINE_PATH = PIPELINES_DIR / "best_zone_pipeline.joblib"


def ensure_project_dirs() -> None:
    for path in [PROCESSED_DIR, ARTIFACTS_DIR, MODELS_DIR, PIPELINES_DIR, NOTEBOOKS_DIR]:
        path.mkdir(parents=True, exist_ok=True)
