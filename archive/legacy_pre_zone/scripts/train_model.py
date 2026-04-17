from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import warnings

import joblib
import numpy as np
import pandas as pd
import sys
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
    make_scorer,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

warnings.filterwarnings(
    "ignore",
    message="`sklearn.utils.parallel.delayed` should be used with `sklearn.utils.parallel.Parallel`",
)

from scripts.common import (
    BEST_MODEL_PATH,
    BEST_PREPROCESSOR_PATH,
    FEATURE_IMPORTANCE_PATH,
    FINAL_DATASET_PATH,
    FINAL_METADATA_PATH,
    MODEL_METRICS_PATH,
    MODELING_STRATEGY_PATH,
    PREDICTION_SAMPLES_PATH,
    PROJECT_ROOT,
    RANDOM_STATE,
    TARGET_COLUMN,
    ensure_project_dirs,
)
from scripts.data_preparation import prepare_datasets


PROVENANCE_COLUMNS = {"record_id", "source_dataset"}
SCORING = {
    "accuracy": "accuracy",
    "precision_macro": make_scorer(precision_score, average="macro", zero_division=0),
    "recall_macro": make_scorer(recall_score, average="macro", zero_division=0),
    "f1_macro": make_scorer(f1_score, average="macro", zero_division=0),
}


def load_final_dataset(dataset_path: Path | None = None) -> pd.DataFrame:
    path = Path(dataset_path or FINAL_DATASET_PATH)
    if not path.exists():
        prepare_datasets()
    return pd.read_csv(path)


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    feature_columns = [column for column in df.columns if column not in PROVENANCE_COLUMNS | {TARGET_COLUMN}]
    X = df[feature_columns].copy()
    y = df[TARGET_COLUMN].copy()
    return X, y, feature_columns


def create_data_splits(
    df: pd.DataFrame,
    test_size: float = 0.15,
    validation_size: float = 0.15,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    X, y, feature_columns = split_features_target(df)
    record_ids = df["record_id"].copy()

    X_train_val, X_test, y_train_val, y_test, record_train_val, record_test = train_test_split(
        X,
        y,
        record_ids,
        test_size=test_size,
        stratify=y,
        random_state=random_state,
    )
    adjusted_validation_size = validation_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val, record_train, record_val = train_test_split(
        X_train_val,
        y_train_val,
        record_train_val,
        test_size=adjusted_validation_size,
        stratify=y_train_val,
        random_state=random_state,
    )

    return {
        "feature_columns": feature_columns,
        "X_train": X_train.reset_index(drop=True),
        "X_val": X_val.reset_index(drop=True),
        "X_test": X_test.reset_index(drop=True),
        "y_train": y_train.reset_index(drop=True),
        "y_val": y_val.reset_index(drop=True),
        "y_test": y_test.reset_index(drop=True),
        "record_train": record_train.reset_index(drop=True),
        "record_val": record_val.reset_index(drop=True),
        "record_test": record_test.reset_index(drop=True),
    }


def infer_feature_types(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric_features = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_features = [column for column in X.columns if column not in numeric_features]
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
            n_estimators=400,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=500,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
    }


def compare_models_with_cv(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    preprocessor: ColumnTransformer,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=random_state)
    rows: list[dict[str, Any]] = []
    for name, model in get_model_candidates(random_state=random_state).items():
        pipeline = Pipeline([("preprocessor", clone(preprocessor)), ("model", model)])
        scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=cv,
            scoring=SCORING,
            n_jobs=-1,
            return_train_score=False,
        )
        rows.append(
            {
                "model_name": name,
                "cv_accuracy_mean": float(scores["test_accuracy"].mean()),
                "cv_precision_macro_mean": float(scores["test_precision_macro"].mean()),
                "cv_recall_macro_mean": float(scores["test_recall_macro"].mean()),
                "cv_f1_macro_mean": float(scores["test_f1_macro"].mean()),
                "cv_accuracy_std": float(scores["test_accuracy"].std()),
                "cv_f1_macro_std": float(scores["test_f1_macro"].std()),
            }
        )
    comparison_df = pd.DataFrame(rows).sort_values(
        ["cv_f1_macro_mean", "cv_accuracy_mean"], ascending=False
    ).reset_index(drop=True)
    return comparison_df


def get_search_space(best_model_name: str, random_state: int = RANDOM_STATE) -> tuple[Pipeline, dict[str, list[Any]]]:
    numeric_features, categorical_features = [], []
    model_candidates = get_model_candidates(random_state=random_state)
    model = model_candidates[best_model_name]
    pipeline = Pipeline([("preprocessor", "passthrough"), ("model", model)])
    if best_model_name == "logistic_regression":
        search_space = {
            "model__C": [0.1, 0.3, 1.0, 3.0, 10.0],
        }
    elif best_model_name == "random_forest":
        search_space = {
            "model__n_estimators": [300, 500, 700],
            "model__max_depth": [None, 8, 12, 18],
            "model__min_samples_leaf": [1, 2, 4, 8],
            "model__max_features": ["sqrt", 0.6, 0.8],
        }
    else:
        search_space = {
            "model__n_estimators": [300, 500, 700],
            "model__max_depth": [None, 8, 12, 18],
            "model__min_samples_leaf": [1, 2, 4, 8],
            "model__max_features": ["sqrt", 0.6, 0.8],
        }
    return pipeline, search_space


def tune_best_model(
    best_model_name: str,
    preprocessor: ColumnTransformer,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = RANDOM_STATE,
) -> RandomizedSearchCV:
    base_pipeline, search_space = get_search_space(best_model_name, random_state=random_state)
    base_pipeline.set_params(preprocessor=clone(preprocessor))
    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=random_state)
    search = RandomizedSearchCV(
        estimator=base_pipeline,
        param_distributions=search_space,
        n_iter=min(8, int(np.prod([len(values) for values in search_space.values()]))),
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        random_state=random_state,
        refit=True,
        verbose=0,
    )
    search.fit(X_train, y_train)
    return search


def evaluate_predictions(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, Any]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def build_prediction_samples(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    record_ids: pd.Series,
) -> pd.DataFrame:
    probabilities = model.predict_proba(X_test)
    classes = model.classes_
    top_k_indices = np.argsort(probabilities, axis=1)[:, ::-1][:, :3]
    predicted = classes[top_k_indices[:, 0]]

    records = []
    for index, record_id in enumerate(record_ids):
        top3 = [f"{classes[class_idx]}:{probabilities[index, class_idx]:.4f}" for class_idx in top_k_indices[index]]
        records.append(
            {
                "record_id": record_id,
                "actual_target": y_test.iloc[index],
                "predicted_target": predicted[index],
                "is_correct": int(y_test.iloc[index] == predicted[index]),
                "top_3_predictions": " | ".join(top3),
            }
        )
    prediction_df = pd.DataFrame(records)
    prediction_df.to_csv(PREDICTION_SAMPLES_PATH, index=False)
    return prediction_df


def compute_feature_importance(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    importance = permutation_importance(
        model,
        X_test,
        y_test,
        scoring="f1_macro",
        n_repeats=8,
        random_state=random_state,
        n_jobs=1,
    )
    feature_importance_df = pd.DataFrame(
        {
            "feature": X_test.columns,
            "importance_mean": importance.importances_mean,
            "importance_std": importance.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)
    feature_importance_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False)
    return feature_importance_df


def write_modeling_strategy(metrics_payload: dict[str, Any]) -> None:
    strategy = f"""# Modeling Strategy

## Problem Framing

- Selected framing: multiclass classification for crop recommendation.
- Reason: the final dataset contains one target label per observation and does not include user-item interaction data or graded relevance judgments required by a classical recommender system.
- Deployment stance: use the classifier as the main predictive engine, then optionally apply rule-based post-filtering from EcoCrop or GAEZ later.

## Dataset Decision

- Training dataset: `data/processed/final_dataset.csv`
- Source: single-source cleaned version of `mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`
- Cross-source row-level merging was rejected because candidate datasets lack reliable shared keys, aligned units, or consistent label semantics.

## Validation Protocol

- Split strategy: stratified train/validation/test.
- Random seed: {RANDOM_STATE}
- Model selection: 4-fold stratified cross-validation on the training split with `macro_f1` as the primary ranking metric.
- Hyperparameter tuning: `RandomizedSearchCV` on the best cross-validation candidate only.
- Final evaluation: hold-out test split after refitting the tuned model on train + validation.

## Models Compared

- Logistic Regression with class balancing for an interpretable linear baseline.
- Random Forest for nonlinear tabular robustness.
- Extra Trees for a stronger high-variance ensemble baseline on mixed numeric/categorical features.

## Risks And Mitigations

- Class imbalance: handled with stratification, macro metrics, and class-weighted models.
- Data leakage: preprocessing is fully contained inside scikit-learn pipelines and fit only on training data within each split/CV fold.
- Label noise: `soil_color` and crop labels were normalized, and the non-crop class `Fallow` was removed from the target space.
- Merge noise: avoided by not forcing weak cross-source joins.
- External validity: the model is trained on an Ethiopia-based dataset, so transfer to Indonesia must be treated as a domain adaptation problem, not assumed.

## Best Model Summary

- Best model: `{metrics_payload['best_model_name']}`
- Validation macro F1: {metrics_payload['validation_metrics']['f1_macro']:.4f}
- Test macro F1: {metrics_payload['test_metrics']['f1_macro']:.4f}
- Test accuracy: {metrics_payload['test_metrics']['accuracy']:.4f}
"""
    MODELING_STRATEGY_PATH.write_text(strategy, encoding="utf-8")


def run_training(
    dataset_path: Path | None = None,
    save_artifacts: bool = True,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    ensure_project_dirs()
    if not FINAL_DATASET_PATH.exists() or not FINAL_METADATA_PATH.exists():
        prepare_datasets()

    df = load_final_dataset(dataset_path or FINAL_DATASET_PATH)
    metadata = json.loads(FINAL_METADATA_PATH.read_text(encoding="utf-8"))
    splits = create_data_splits(df, random_state=random_state)
    numeric_features, categorical_features = infer_feature_types(splits["X_train"])
    preprocessor = build_preprocessor(numeric_features, categorical_features)

    comparison_df = compare_models_with_cv(
        splits["X_train"],
        splits["y_train"],
        preprocessor=preprocessor,
        random_state=random_state,
    )
    best_model_name = comparison_df.iloc[0]["model_name"]
    search = tune_best_model(
        best_model_name=best_model_name,
        preprocessor=preprocessor,
        X_train=splits["X_train"],
        y_train=splits["y_train"],
        random_state=random_state,
    )

    validation_predictions = search.best_estimator_.predict(splits["X_val"])
    validation_metrics = evaluate_predictions(splits["y_val"], validation_predictions)

    X_train_full = pd.concat([splits["X_train"], splits["X_val"]], ignore_index=True)
    y_train_full = pd.concat([splits["y_train"], splits["y_val"]], ignore_index=True)
    final_model = clone(search.best_estimator_)
    final_model.fit(X_train_full, y_train_full)

    test_predictions = final_model.predict(splits["X_test"])
    test_metrics = evaluate_predictions(splits["y_test"], test_predictions)
    class_report = classification_report(splits["y_test"], test_predictions, output_dict=True, zero_division=0)
    labels = sorted(y_train_full.unique())
    matrix = confusion_matrix(splits["y_test"], test_predictions, labels=labels)

    prediction_df = build_prediction_samples(
        model=final_model,
        X_test=splits["X_test"],
        y_test=splits["y_test"],
        record_ids=splits["record_test"],
    )
    feature_importance_df = compute_feature_importance(
        model=final_model,
        X_test=splits["X_test"],
        y_test=splits["y_test"],
        random_state=random_state,
    )

    metrics_payload = {
        "dataset_path": str((dataset_path or FINAL_DATASET_PATH).relative_to(PROJECT_ROOT)),
        "target_column": TARGET_COLUMN,
        "feature_columns": splits["feature_columns"],
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "split_sizes": {
            "train": int(splits["X_train"].shape[0]),
            "validation": int(splits["X_val"].shape[0]),
            "test": int(splits["X_test"].shape[0]),
        },
        "class_distribution_full_dataset": df[TARGET_COLUMN].value_counts().to_dict(),
        "cross_validation_results": comparison_df.to_dict(orient="records"),
        "best_model_name": best_model_name,
        "best_model_params": search.best_params_,
        "best_cv_macro_f1": float(search.best_score_),
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "classification_report": class_report,
        "confusion_matrix_labels": labels,
        "confusion_matrix": matrix.tolist(),
        "top_feature_importance": feature_importance_df.head(15).to_dict(orient="records"),
        "notes": [
            "Model comparison and tuning used only the training split to avoid leakage.",
            "Final model was retrained on train+validation before the hold-out test evaluation.",
            "The baseline operates on a single-source supervised dataset; Indonesia-specific generalization remains limited.",
        ],
        "dataset_metadata_snapshot": {
            "rows_after_cleaning": metadata["rows_after_cleaning"],
            "removed_rows": metadata["removed_rows"],
        },
    }

    if save_artifacts:
        joblib.dump(final_model, BEST_MODEL_PATH)
        joblib.dump(final_model.named_steps["preprocessor"], BEST_PREPROCESSOR_PATH)
        MODEL_METRICS_PATH.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
        write_modeling_strategy(metrics_payload)

    return {
        "dataset": df,
        "splits": splits,
        "comparison_df": comparison_df,
        "search": search,
        "final_model": final_model,
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "prediction_df": prediction_df,
        "feature_importance_df": feature_importance_df,
        "metrics_payload": metrics_payload,
    }


if __name__ == "__main__":
    result = run_training(save_artifacts=True)
    print(json.dumps(result["metrics_payload"], indent=2))
