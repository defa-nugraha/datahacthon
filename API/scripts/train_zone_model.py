from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupKFold, ParameterGrid, RandomizedSearchCV, StratifiedGroupKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

warnings.filterwarnings(
    "ignore",
    message="`sklearn.utils.parallel.delayed` should be used with `sklearn.utils.parallel.Parallel`",
)

from scripts.build_zone_dataset import POINT_NUMERIC_FEATURES, prepare_zone_datasets
from scripts.common import (
    BEST_ZONE_MODEL_PATH,
    BEST_ZONE_PREPROCESSOR_PATH,
    PROJECT_ROOT,
    RANDOM_STATE,
    TARGET_COLUMN,
    ZONE_DATASET_PATH,
    ZONE_DATASET_EXTENDED_PATH,
    ZONE_DATASET_MINIMAL_PATH,
    ZONE_FEATURE_IMPORTANCE_PATH,
    ZONE_MODEL_METRICS_PATH,
    ZONE_MODELING_STRATEGY_PATH,
    ZONE_PREDICTION_SAMPLES_PATH,
    ZONE_TARGET_COLUMN,
    ensure_project_dirs,
)


ZONE_PROVENANCE_COLUMNS = {"zone_id", "base_context_id", "source_dataset", "sample_count_risk_flag"}
ZONE_LEAKAGE_COLUMNS = {"label_nunique", "zone_label_dominance_ratio"}
POINT_PROVENANCE_COLUMNS = {"point_id", "zone_id", "source_dataset", "base_context_id", "context_sample_count", "context_cluster_count"}
POINT_WEATHER_DETAIL_COLUMNS = {
    "QV2M-W",
    "QV2M-Sp",
    "QV2M-Su",
    "QV2M-Au",
    "T2M_MAX-W",
    "T2M_MAX-Sp",
    "T2M_MAX-Su",
    "T2M_MAX-Au",
    "T2M_MIN-W",
    "T2M_MIN-Sp",
    "T2M_MIN-Su",
    "T2M_MIN-Au",
    "PRECTOTCORR-W",
    "PRECTOTCORR-Sp",
    "PRECTOTCORR-Su",
    "PRECTOTCORR-Au",
    "WD10M",
    "GWETTOP",
    "CLOUD_AMT",
    "WS2M_RANGE",
    "PS",
}
POINT_FEATURE_COLUMNS = [
    "soil_color",
    "ph",
    "nitrogen",
    "phosphorus",
    "potassium",
    "zinc",
    "sulfur",
    "specific_humidity_mean",
    "temperature_mean",
    "temperature_seasonal_range",
    "rainfall_mean",
    "rainfall_total_proxy",
    "soil_moisture_surface",
    "cloud_amount",
    "surface_pressure",
]
SCORING = {
    "accuracy": "accuracy",
    "precision_macro": make_scorer(precision_score, average="macro", zero_division=0),
    "recall_macro": make_scorer(recall_score, average="macro", zero_division=0),
    "f1_macro": make_scorer(f1_score, average="macro", zero_division=0),
}


def infer_feature_types(frame: pd.DataFrame, feature_columns: list[str]) -> tuple[list[str], list[str]]:
    numeric_features = frame[feature_columns].select_dtypes(include=["number"]).columns.tolist()
    categorical_features = [column for column in feature_columns if column not in numeric_features]
    return numeric_features, categorical_features


def build_preprocessor(numeric_features: list[str], categorical_features: list[str]) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )


def get_model_candidates(random_state: int = RANDOM_STATE) -> dict[str, Any]:
    return {
        "logistic_regression": LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=180,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=220,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
    }


def get_search_space(best_model_name: str) -> dict[str, list[Any]]:
    if best_model_name == "logistic_regression":
        return {"model__C": [0.1, 0.3, 1.0, 3.0, 10.0]}
    return {
        "model__n_estimators": [120, 180, 260],
        "model__max_depth": [None, 8, 14],
        "model__min_samples_leaf": [1, 2, 4],
        "model__max_features": ["sqrt", 0.8],
    }


def evaluate_predictions(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def max_safe_stratified_group_splits(
    y: pd.Series,
    groups: pd.Series,
    requested_splits: int = 4,
) -> int:
    class_counts = y.value_counts()
    if class_counts.empty:
        return 0
    min_class_count = int(class_counts.min())
    n_groups = int(pd.Series(groups).nunique())
    if min_class_count < 2 or n_groups < 2:
        return 0
    return max(0, min(requested_splits, min_class_count, n_groups))


def make_group_cv(
    y: pd.Series,
    groups: pd.Series,
    requested_splits: int = 4,
    random_state: int = RANDOM_STATE,
) -> tuple[Any, str, int]:
    safe_stratified_splits = max_safe_stratified_group_splits(y, groups, requested_splits=requested_splits)
    if safe_stratified_splits >= 2:
        return (
            StratifiedGroupKFold(n_splits=safe_stratified_splits, shuffle=True, random_state=random_state),
            "stratified_group_kfold",
            safe_stratified_splits,
        )

    n_groups = int(pd.Series(groups).nunique())
    group_splits = min(requested_splits, n_groups)
    if group_splits >= 2:
        return (
            GroupKFold(n_splits=group_splits),
            "group_kfold_fallback",
            group_splits,
        )
    raise ValueError("At least 2 distinct groups are required for a group-aware split.")


def choose_best_group_split(
    y: pd.Series,
    groups: pd.Series,
    n_splits: int,
    random_state: int,
) -> tuple[np.ndarray, np.ndarray]:
    splitter, splitter_name, effective_splits = make_group_cv(
        y=y,
        groups=groups,
        requested_splits=n_splits,
        random_state=random_state,
    )
    overall_distribution = y.value_counts(normalize=True)
    candidates: list[tuple[tuple[float, float, float], tuple[np.ndarray, np.ndarray]]] = []
    dummy_X = np.zeros(len(y))
    for train_idx, test_idx in splitter.split(dummy_X, y, groups):
        train_distribution = y.iloc[train_idx].value_counts(normalize=True)
        test_distribution = y.iloc[test_idx].value_counts(normalize=True)
        train_coverage = float(train_distribution.shape[0])
        test_coverage = float(test_distribution.shape[0])
        min_train_class_count = float(y.iloc[train_idx].value_counts().min())
        divergence = float(overall_distribution.sub(test_distribution, fill_value=0).abs().sum())
        group_count = float(pd.Series(groups.iloc[test_idx]).nunique())
        test_size_gap = abs(len(test_idx) - (len(y) / effective_splits))
        score = (-train_coverage, -test_coverage, -min_train_class_count, divergence, test_size_gap, -group_count)
        candidates.append((score, (train_idx, test_idx)))
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def create_grouped_train_val_test_split(
    frame: pd.DataFrame,
    target_column: str,
    group_column: str,
    random_state: int = RANDOM_STATE,
) -> dict[str, np.ndarray]:
    outer_train_idx, test_idx = choose_best_group_split(
        y=frame[target_column],
        groups=frame[group_column],
        n_splits=min(4, frame[group_column].nunique()),
        random_state=random_state,
    )
    outer_train_frame = frame.iloc[outer_train_idx].reset_index(drop=True)
    inner_train_idx, val_idx = choose_best_group_split(
        y=outer_train_frame[target_column],
        groups=outer_train_frame[group_column],
        n_splits=min(3, outer_train_frame[group_column].nunique()),
        random_state=random_state + 1,
    )
    train_idx = outer_train_idx[inner_train_idx]
    validation_idx = outer_train_idx[val_idx]
    return {
        "train_idx": train_idx,
        "validation_idx": validation_idx,
        "test_idx": test_idx,
    }


def compare_zone_models_with_group_cv(
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    group_column: str,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    numeric_features, categorical_features = infer_feature_types(frame, feature_columns)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    groups = frame[group_column]
    y = frame[target_column]
    cv, cv_strategy, cv_splits = make_group_cv(
        y=y,
        groups=groups,
        requested_splits=min(4, groups.nunique()),
        random_state=random_state,
    )

    rows: list[dict[str, Any]] = []
    for model_name, model in get_model_candidates(random_state=random_state).items():
        pipeline = Pipeline([("preprocessor", clone(preprocessor)), ("model", model)])
        scores = cross_validate(
            pipeline,
            frame[feature_columns],
            y,
            cv=cv,
            scoring=SCORING,
            groups=groups,
            n_jobs=-1,
            return_train_score=False,
        )
        rows.append(
            {
                "model_name": model_name,
                "selection_strategy": cv_strategy,
                "cv_splits": int(cv_splits),
                "cv_accuracy_mean": float(scores["test_accuracy"].mean()),
                "cv_precision_macro_mean": float(scores["test_precision_macro"].mean()),
                "cv_recall_macro_mean": float(scores["test_recall_macro"].mean()),
                "cv_f1_macro_mean": float(scores["test_f1_macro"].mean()),
                "cv_accuracy_std": float(scores["test_accuracy"].std()),
                "cv_f1_macro_std": float(scores["test_f1_macro"].std()),
            }
    )
    return pd.DataFrame(rows).sort_values(["cv_f1_macro_mean", "cv_accuracy_mean"], ascending=False).reset_index(drop=True)


def compare_models_with_validation_holdout(
    train_frame: pd.DataFrame,
    validation_frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    numeric_features, categorical_features = infer_feature_types(train_frame, feature_columns)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    rows: list[dict[str, Any]] = []

    for model_name, model in get_model_candidates(random_state=random_state).items():
        pipeline = Pipeline([("preprocessor", clone(preprocessor)), ("model", model)])
        pipeline.fit(train_frame[feature_columns], train_frame[target_column])
        validation_predictions = pipeline.predict(validation_frame[feature_columns])
        validation_metrics = evaluate_predictions(validation_frame[target_column], validation_predictions)
        rows.append(
            {
                "model_name": model_name,
                "selection_strategy": "validation_holdout_fallback",
                "cv_splits": 0,
                "cv_accuracy_mean": validation_metrics["accuracy"],
                "cv_precision_macro_mean": validation_metrics["precision_macro"],
                "cv_recall_macro_mean": validation_metrics["recall_macro"],
                "cv_f1_macro_mean": validation_metrics["f1_macro"],
                "cv_accuracy_std": 0.0,
                "cv_f1_macro_std": 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values(["cv_f1_macro_mean", "cv_accuracy_mean"], ascending=False).reset_index(drop=True)


def tune_zone_model(
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    group_column: str,
    best_model_name: str,
    random_state: int = RANDOM_STATE,
) -> RandomizedSearchCV:
    numeric_features, categorical_features = infer_feature_types(frame, feature_columns)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    model = get_model_candidates(random_state=random_state)[best_model_name]
    pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])
    cv, _, _ = make_group_cv(
        y=frame[target_column],
        groups=frame[group_column],
        requested_splits=min(4, frame[group_column].nunique()),
        random_state=random_state,
    )
    search_space = get_search_space(best_model_name)
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=search_space,
        n_iter=min(5, int(np.prod([len(values) for values in search_space.values()]))),
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        random_state=random_state,
        refit=True,
        verbose=0,
    )
    search.fit(frame[feature_columns], frame[target_column], groups=frame[group_column])
    return search


def tune_zone_model_with_validation(
    train_frame: pd.DataFrame,
    validation_frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    best_model_name: str,
    random_state: int = RANDOM_STATE,
) -> tuple[Pipeline, dict[str, Any], float]:
    numeric_features, categorical_features = infer_feature_types(train_frame, feature_columns)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    base_model = get_model_candidates(random_state=random_state)[best_model_name]
    base_pipeline = Pipeline([("preprocessor", preprocessor), ("model", clone(base_model))])
    search_space = get_search_space(best_model_name)
    candidate_params = list(ParameterGrid(search_space))
    if best_model_name != "logistic_regression":
        candidate_params = candidate_params[:12]

    best_score = -math.inf
    best_params: dict[str, Any] = {}
    best_pipeline: Pipeline | None = None

    for params in candidate_params:
        candidate = clone(base_pipeline)
        candidate.set_params(**params)
        candidate.fit(train_frame[feature_columns], train_frame[target_column])
        predictions = candidate.predict(validation_frame[feature_columns])
        score = float(f1_score(validation_frame[target_column], predictions, average="macro", zero_division=0))
        if score > best_score:
            best_score = score
            best_params = dict(params)
            best_pipeline = candidate

    if best_pipeline is None:
        raise RuntimeError("Validation-based tuning failed to produce a fitted model.")
    return best_pipeline, best_params, best_score


def build_zone_prediction_samples(
    model: Pipeline,
    zone_frame: pd.DataFrame,
    feature_columns: list[str],
) -> pd.DataFrame:
    probabilities = model.predict_proba(zone_frame[feature_columns])
    classes = model.classes_
    top_indices = np.argsort(probabilities, axis=1)[:, ::-1][:, :3]
    predicted = classes[top_indices[:, 0]]
    rows = []
    for index, (_, row) in enumerate(zone_frame.iterrows()):
        top_predictions = [
            f"{classes[class_index]}:{probabilities[index, class_index]:.4f}"
            for class_index in top_indices[index]
        ]
        rows.append(
            {
                "zone_id": row["zone_id"],
                "base_context_id": int(row["base_context_id"]),
                "sample_count": int(row["sample_count"]),
                "actual_target": row[ZONE_TARGET_COLUMN],
                "predicted_target": predicted[index],
                "is_correct": int(predicted[index] == row[ZONE_TARGET_COLUMN]),
                "top_3_predictions": " | ".join(top_predictions),
            }
        )
    prediction_df = pd.DataFrame(rows)
    prediction_df.to_csv(ZONE_PREDICTION_SAMPLES_PATH, index=False)
    return prediction_df


def compute_zone_feature_importance(
    scenario_name: str,
    model: Pipeline,
    feature_frame: pd.DataFrame,
    target: pd.Series,
    feature_columns: list[str],
) -> pd.DataFrame:
    importance = permutation_importance(
        model,
        feature_frame[feature_columns],
        target,
        scoring="f1_macro",
        n_repeats=3,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )
    importance_df = pd.DataFrame(
        {
            "scenario_name": scenario_name,
            "feature": feature_columns,
            "importance_mean": importance.importances_mean,
            "importance_std": importance.importances_std,
        }
    ).sort_values(["scenario_name", "importance_mean"], ascending=[True, False])
    return importance_df


def point_zone_majority_vote(probabilities: np.ndarray, classes: np.ndarray, zone_ids: pd.Series) -> pd.Series:
    point_predictions = pd.DataFrame(probabilities, columns=classes)
    point_predictions["zone_id"] = zone_ids.values
    zone_scores = point_predictions.groupby("zone_id")[list(classes)].mean()
    return zone_scores.idxmax(axis=1)


def train_point_to_zone_baseline(
    point_frame: pd.DataFrame,
    zone_frame: pd.DataFrame,
    split_contexts: dict[str, set[int]],
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    train_points = point_frame.loc[point_frame["base_context_id"].isin(split_contexts["train"])].reset_index(drop=True)
    validation_points = point_frame.loc[point_frame["base_context_id"].isin(split_contexts["validation"])].reset_index(drop=True)
    test_points = point_frame.loc[point_frame["base_context_id"].isin(split_contexts["test"])].reset_index(drop=True)

    feature_columns = POINT_FEATURE_COLUMNS
    numeric_features, categorical_features = infer_feature_types(train_points, feature_columns)
    preprocessor = build_preprocessor(numeric_features, categorical_features)

    comparison_rows = []
    fitted_models: dict[str, Pipeline] = {}
    for model_name, model in get_model_candidates(random_state=random_state).items():
        pipeline = Pipeline([("preprocessor", clone(preprocessor)), ("model", model)])
        pipeline.fit(train_points[feature_columns], train_points[TARGET_COLUMN])

        validation_probabilities = pipeline.predict_proba(validation_points[feature_columns])
        validation_zone_predictions = point_zone_majority_vote(
            validation_probabilities,
            pipeline.classes_,
            validation_points["zone_id"],
        )
        validation_zone_truth = (
            zone_frame.set_index("zone_id")
            .loc[validation_zone_predictions.index, ZONE_TARGET_COLUMN]
        )
        validation_metrics = evaluate_predictions(validation_zone_truth, validation_zone_predictions.values)
        comparison_rows.append(
            {
                "model_name": model_name,
                "validation_accuracy": validation_metrics["accuracy"],
                "validation_precision_macro": validation_metrics["precision_macro"],
                "validation_recall_macro": validation_metrics["recall_macro"],
                "validation_f1_macro": validation_metrics["f1_macro"],
            }
        )
        fitted_models[model_name] = pipeline

    comparison_df = pd.DataFrame(comparison_rows).sort_values(
        ["validation_f1_macro", "validation_accuracy"], ascending=False
    ).reset_index(drop=True)
    best_model_name = comparison_df.iloc[0]["model_name"]

    train_val_points = point_frame.loc[
        point_frame["base_context_id"].isin(split_contexts["train"] | split_contexts["validation"])
    ].reset_index(drop=True)
    best_model = clone(fitted_models[best_model_name])
    best_model.fit(train_val_points[feature_columns], train_val_points[TARGET_COLUMN])

    test_probabilities = best_model.predict_proba(test_points[feature_columns])
    test_zone_predictions = point_zone_majority_vote(
        test_probabilities,
        best_model.classes_,
        test_points["zone_id"],
    )
    test_zone_truth = zone_frame.set_index("zone_id").loc[test_zone_predictions.index, ZONE_TARGET_COLUMN]
    test_metrics = evaluate_predictions(test_zone_truth, test_zone_predictions.values)

    return {
        "scenario_name": "point_to_zone_baseline",
        "feature_columns": feature_columns,
        "comparison_df": comparison_df,
        "best_model_name": best_model_name,
        "best_model": best_model,
        "validation_metrics": comparison_df.iloc[0][
            ["validation_accuracy", "validation_precision_macro", "validation_recall_macro", "validation_f1_macro"]
        ].to_dict(),
        "test_metrics": test_metrics,
        "test_zone_count": int(test_zone_predictions.shape[0]),
        "notes": [
            "This baseline is trained on individual points but evaluated after aggregating point predictions to the zone level.",
            "Model selection uses a fixed validation context split rather than grouped CV because the main production focus is the zone model.",
        ],
    }


def train_zone_scenario(
    scenario_name: str,
    zone_frame: pd.DataFrame,
    feature_columns: list[str],
    split_indices: dict[str, np.ndarray],
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    train_frame = zone_frame.iloc[split_indices["train_idx"]].reset_index(drop=True)
    validation_frame = zone_frame.iloc[split_indices["validation_idx"]].reset_index(drop=True)
    test_frame = zone_frame.iloc[split_indices["test_idx"]].reset_index(drop=True)

    safe_cv_splits = max_safe_stratified_group_splits(
        y=train_frame[ZONE_TARGET_COLUMN],
        groups=train_frame["base_context_id"],
        requested_splits=min(4, train_frame["base_context_id"].nunique()),
    )
    if safe_cv_splits >= 2:
        comparison_df = compare_zone_models_with_group_cv(
            frame=train_frame,
            feature_columns=feature_columns,
            target_column=ZONE_TARGET_COLUMN,
            group_column="base_context_id",
            random_state=random_state,
        )
        tuning_mode = "group_cv"
    else:
        comparison_df = compare_models_with_validation_holdout(
            train_frame=train_frame,
            validation_frame=validation_frame,
            feature_columns=feature_columns,
            target_column=ZONE_TARGET_COLUMN,
            random_state=random_state,
        )
        tuning_mode = "validation_holdout_fallback"
    best_model_name = comparison_df.iloc[0]["model_name"]
    if tuning_mode == "group_cv":
        search = tune_zone_model(
            frame=train_frame,
            feature_columns=feature_columns,
            target_column=ZONE_TARGET_COLUMN,
            group_column="base_context_id",
            best_model_name=best_model_name,
            random_state=random_state,
        )
        validation_predictions = search.best_estimator_.predict(validation_frame[feature_columns])
        validation_metrics = evaluate_predictions(validation_frame[ZONE_TARGET_COLUMN], validation_predictions)
        best_estimator = search.best_estimator_
        best_params = search.best_params_
        best_score = float(search.best_score_)
    else:
        best_estimator, best_params, best_score = tune_zone_model_with_validation(
            train_frame=train_frame,
            validation_frame=validation_frame,
            feature_columns=feature_columns,
            target_column=ZONE_TARGET_COLUMN,
            best_model_name=best_model_name,
            random_state=random_state,
        )
        validation_predictions = best_estimator.predict(validation_frame[feature_columns])
        validation_metrics = evaluate_predictions(validation_frame[ZONE_TARGET_COLUMN], validation_predictions)

    train_val_frame = zone_frame.iloc[
        np.concatenate([split_indices["train_idx"], split_indices["validation_idx"]])
    ].reset_index(drop=True)
    final_model = clone(best_estimator)
    final_model.fit(train_val_frame[feature_columns], train_val_frame[ZONE_TARGET_COLUMN])

    test_predictions = final_model.predict(test_frame[feature_columns])
    test_metrics = evaluate_predictions(test_frame[ZONE_TARGET_COLUMN], test_predictions)
    class_report = classification_report(test_frame[ZONE_TARGET_COLUMN], test_predictions, output_dict=True, zero_division=0)
    labels = sorted(train_val_frame[ZONE_TARGET_COLUMN].unique())
    matrix = confusion_matrix(test_frame[ZONE_TARGET_COLUMN], test_predictions, labels=labels)
    return {
        "scenario_name": scenario_name,
        "feature_columns": feature_columns,
        "train_frame": train_frame,
        "validation_frame": validation_frame,
        "test_frame": test_frame,
        "comparison_df": comparison_df,
        "best_model_name": best_model_name,
        "selection_strategy": tuning_mode,
        "best_params": best_params,
        "best_cv_or_validation_macro_f1": best_score,
        "final_model": final_model,
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "classification_report": class_report,
        "confusion_matrix_labels": labels,
        "confusion_matrix": matrix.tolist(),
    }


def build_zone_views(zone_minimal_df: pd.DataFrame, zone_extended_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    minimal_features = [
        column
        for column in zone_minimal_df.columns
        if column not in ZONE_PROVENANCE_COLUMNS | {ZONE_TARGET_COLUMN}
    ]
    extended_features = [
        column
        for column in zone_extended_df.columns
        if column not in ZONE_PROVENANCE_COLUMNS | ZONE_LEAKAGE_COLUMNS | {ZONE_TARGET_COLUMN}
    ]
    return {
        "zone_mean_only": {"frame": zone_minimal_df.copy(), "feature_columns": minimal_features},
        "zone_mean_plus_variability": {"frame": zone_extended_df.copy(), "feature_columns": extended_features},
    }


def append_zone_strategy_results(metrics_payload: dict[str, Any]) -> None:
    existing = ZONE_MODELING_STRATEGY_PATH.read_text(encoding="utf-8") if ZONE_MODELING_STRATEGY_PATH.exists() else ""
    results_section = f"""

## Modeling Results

- Point-based or zone-based raw data: point-based
- Final zone model framing: multiclass classification on zone labels
- Compared scenarios:
  - point-to-zone baseline
  - zone mean-only
  - zone mean + variability
- Best point baseline test macro F1: {metrics_payload['point_to_zone_baseline']['test_metrics']['f1_macro']:.4f}
- Best zone mean-only test macro F1: {metrics_payload['zone_mean_only']['test_metrics']['f1_macro']:.4f}
- Best zone variability test macro F1: {metrics_payload['zone_mean_plus_variability']['test_metrics']['f1_macro']:.4f}
- Selected production zone scenario: `{metrics_payload['selected_zone_scenario']}`
- Variability features improved test macro F1: {metrics_payload['variability_features_help_test']}
- Zone model outperformed point-to-zone baseline on test macro F1: {metrics_payload['zone_model_beats_point_baseline']}
"""
    ZONE_MODELING_STRATEGY_PATH.write_text(existing.rstrip() + "\n" + results_section.strip() + "\n", encoding="utf-8")


def run_zone_pipeline(save_artifacts: bool = True, random_state: int = RANDOM_STATE) -> dict[str, Any]:
    ensure_project_dirs()
    bundle = prepare_zone_datasets()

    point_frame = bundle["filtered_point_df"].copy()
    zone_minimal_df = bundle["zone_minimal_df"].copy()
    zone_extended_df = bundle["zone_extended_df"].copy()
    zone_views = build_zone_views(zone_minimal_df, zone_extended_df)

    split_indices = create_grouped_train_val_test_split(
        frame=zone_extended_df,
        target_column=ZONE_TARGET_COLUMN,
        group_column="base_context_id",
        random_state=random_state,
    )
    split_contexts = {
        "train": set(zone_extended_df.iloc[split_indices["train_idx"]]["base_context_id"].tolist()),
        "validation": set(zone_extended_df.iloc[split_indices["validation_idx"]]["base_context_id"].tolist()),
        "test": set(zone_extended_df.iloc[split_indices["test_idx"]]["base_context_id"].tolist()),
    }

    point_baseline_result = train_point_to_zone_baseline(
        point_frame=point_frame,
        zone_frame=zone_extended_df,
        split_contexts=split_contexts,
        random_state=random_state,
    )

    zone_results = {}
    for scenario_name, scenario in zone_views.items():
        zone_results[scenario_name] = train_zone_scenario(
            scenario_name=scenario_name,
            zone_frame=scenario["frame"],
            feature_columns=scenario["feature_columns"],
            split_indices=split_indices,
            random_state=random_state,
        )

    selected_zone_scenario = max(
        zone_results,
        key=lambda name: (
            zone_results[name]["validation_metrics"]["f1_macro"],
            zone_results[name]["test_metrics"]["f1_macro"],
        ),
    )
    best_zone_result = zone_results[selected_zone_scenario]
    selected_feature_importance = compute_zone_feature_importance(
        scenario_name=selected_zone_scenario,
        model=best_zone_result["final_model"],
        feature_frame=best_zone_result["test_frame"],
        target=best_zone_result["test_frame"][ZONE_TARGET_COLUMN],
        feature_columns=best_zone_result["feature_columns"],
    )
    selected_feature_importance.to_csv(ZONE_FEATURE_IMPORTANCE_PATH, index=False)

    prediction_samples_df = build_zone_prediction_samples(
        model=best_zone_result["final_model"],
        zone_frame=best_zone_result["test_frame"],
        feature_columns=best_zone_result["feature_columns"],
    )

    metrics_payload = {
        "split_strategy": {
            "type": "group_aware_stratified_split",
            "group_column": "base_context_id",
            "train_contexts": sorted(split_contexts["train"]),
            "validation_contexts": sorted(split_contexts["validation"]),
            "test_contexts": sorted(split_contexts["test"]),
        },
        "zone_builder_params": bundle["metadata"]["zone_builder_params"],
        "zone_dataset_summary": {
            "zone_dataset_path": str(ZONE_DATASET_PATH.relative_to(PROJECT_ROOT)),
            "zone_dataset_minimal_path": str(ZONE_DATASET_MINIMAL_PATH.relative_to(PROJECT_ROOT)),
            "zone_dataset_extended_path": str(ZONE_DATASET_EXTENDED_PATH.relative_to(PROJECT_ROOT)),
            "n_final_zones": int(zone_extended_df.shape[0]),
            "zone_class_distribution": zone_extended_df[ZONE_TARGET_COLUMN].value_counts().to_dict(),
            "average_points_per_zone": bundle["metadata"]["average_points_per_zone"],
        },
        "point_to_zone_baseline": {
            "best_model_name": point_baseline_result["best_model_name"],
            "feature_columns": point_baseline_result["feature_columns"],
            "model_comparison": point_baseline_result["comparison_df"].to_dict(orient="records"),
            "validation_metrics": point_baseline_result["validation_metrics"],
            "test_metrics": point_baseline_result["test_metrics"],
            "test_zone_count": point_baseline_result["test_zone_count"],
            "notes": point_baseline_result["notes"],
        },
        "zone_mean_only": {
            "best_model_name": zone_results["zone_mean_only"]["best_model_name"],
            "selection_strategy": zone_results["zone_mean_only"]["selection_strategy"],
            "best_model_params": zone_results["zone_mean_only"]["best_params"],
            "best_cv_or_validation_macro_f1": float(zone_results["zone_mean_only"]["best_cv_or_validation_macro_f1"]),
            "feature_columns": zone_results["zone_mean_only"]["feature_columns"],
            "model_comparison": zone_results["zone_mean_only"]["comparison_df"].to_dict(orient="records"),
            "validation_metrics": zone_results["zone_mean_only"]["validation_metrics"],
            "test_metrics": zone_results["zone_mean_only"]["test_metrics"],
        },
        "zone_mean_plus_variability": {
            "best_model_name": zone_results["zone_mean_plus_variability"]["best_model_name"],
            "selection_strategy": zone_results["zone_mean_plus_variability"]["selection_strategy"],
            "best_model_params": zone_results["zone_mean_plus_variability"]["best_params"],
            "best_cv_or_validation_macro_f1": float(zone_results["zone_mean_plus_variability"]["best_cv_or_validation_macro_f1"]),
            "feature_columns": zone_results["zone_mean_plus_variability"]["feature_columns"],
            "model_comparison": zone_results["zone_mean_plus_variability"]["comparison_df"].to_dict(orient="records"),
            "validation_metrics": zone_results["zone_mean_plus_variability"]["validation_metrics"],
            "test_metrics": zone_results["zone_mean_plus_variability"]["test_metrics"],
        },
        "selected_zone_scenario": selected_zone_scenario,
        "selected_zone_model_name": best_zone_result["best_model_name"],
        "selected_zone_selection_strategy": best_zone_result["selection_strategy"],
        "selected_zone_model_params": best_zone_result["best_params"],
        "selected_zone_validation_metrics": best_zone_result["validation_metrics"],
        "selected_zone_test_metrics": best_zone_result["test_metrics"],
        "selected_zone_confusion_matrix_labels": best_zone_result["confusion_matrix_labels"],
        "selected_zone_confusion_matrix": best_zone_result["confusion_matrix"],
        "selected_zone_classification_report": best_zone_result["classification_report"],
        "variability_features_help_validation": bool(
            zone_results["zone_mean_plus_variability"]["validation_metrics"]["f1_macro"]
            > zone_results["zone_mean_only"]["validation_metrics"]["f1_macro"]
        ),
        "variability_features_help_test": bool(
            zone_results["zone_mean_plus_variability"]["test_metrics"]["f1_macro"]
            > zone_results["zone_mean_only"]["test_metrics"]["f1_macro"]
        ),
        "zone_model_beats_point_baseline": bool(
            best_zone_result["test_metrics"]["f1_macro"] > point_baseline_result["test_metrics"]["f1_macro"]
        ),
        "best_zone_top_feature_importance": (
            selected_feature_importance.loc[selected_feature_importance["scenario_name"] == selected_zone_scenario]
            .head(20)
            .to_dict(orient="records")
        ),
        "artifacts": {
            "zone_model_metrics": str(ZONE_MODEL_METRICS_PATH.relative_to(PROJECT_ROOT)),
            "zone_prediction_samples": str(ZONE_PREDICTION_SAMPLES_PATH.relative_to(PROJECT_ROOT)),
            "zone_feature_importance": str(ZONE_FEATURE_IMPORTANCE_PATH.relative_to(PROJECT_ROOT)),
            "best_zone_model": str(BEST_ZONE_MODEL_PATH.relative_to(PROJECT_ROOT)),
            "best_zone_preprocessor": str(BEST_ZONE_PREPROCESSOR_PATH.relative_to(PROJECT_ROOT)),
        },
        "notes": [
            "Point baseline is intentionally evaluated at the zone level by aggregating point predictions inside each held-out zone.",
            "Zone scenarios use group-aware CV and group-aware hold-out splits keyed by base_context_id.",
            "Because raw coordinates are absent, the zone system remains a pseudo-zone approximation rather than a true geospatial field-zone model.",
        ],
    }

    if save_artifacts:
        joblib.dump(best_zone_result["final_model"], BEST_ZONE_MODEL_PATH)
        joblib.dump(best_zone_result["final_model"].named_steps["preprocessor"], BEST_ZONE_PREPROCESSOR_PATH)
        ZONE_MODEL_METRICS_PATH.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
        append_zone_strategy_results(metrics_payload)

    return {
        "bundle": bundle,
        "point_to_zone_baseline": point_baseline_result,
        "zone_results": zone_results,
        "selected_zone_result": best_zone_result,
        "prediction_samples_df": prediction_samples_df,
        "feature_importance_df": selected_feature_importance,
        "metrics_payload": metrics_payload,
    }


if __name__ == "__main__":
    result = run_zone_pipeline(save_artifacts=True)
    print(json.dumps(result["metrics_payload"], indent=2))
