from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.base import clone
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
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
from sklearn.model_selection import RandomizedSearchCV, cross_validate
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

warnings.filterwarnings("ignore", category=UserWarning)

from scripts.build_zone_dataset import ZONE_BUILDER_PARAMS, assign_zone_ids, build_zone_statistics, normalize_point_dataframe
from scripts.common import (
    ARTIFACTS_DIR,
    MODELS_DIR,
    PIPELINES_DIR,
    PROJECT_ROOT,
    RANDOM_STATE,
    TARGET_COLUMN,
    ZONE_DATASET_EXTENDED_PATH,
    ZONE_DATASET_MINIMAL_PATH,
    ZONE_METADATA_PATH,
    ZONE_MODEL_METRICS_PATH,
    ZONE_TARGET_COLUMN,
    ensure_project_dirs,
)
from scripts.model_wrappers import FlattenPredictionClassifier, StringLabelXGBClassifier, flatten_predictions
from scripts.train_zone_model import build_preprocessor, choose_best_group_split, infer_feature_types, make_group_cv


LABEL_MAPPING_ID = {
    "Barley": "Jelai",
    "Maize": "Jagung",
    "Teff": "Teff",
    "Wheat": "Gandum",
}

ZONE_PROVENANCE_COLUMNS = {"zone_id", "base_context_id", "source_dataset", "sample_count_risk_flag"}
ZONE_LEAKAGE_COLUMNS = {"label_nunique", "zone_label_dominance_ratio"}

ZONE_DATASET_EXTENDED_ID_PATH = ZONE_DATASET_EXTENDED_PATH.with_name("zone_dataset_extended_id.csv")
ZONE_DATASET_MINIMAL_ID_PATH = ZONE_DATASET_MINIMAL_PATH.with_name("zone_dataset_minimal_id.csv")

LABEL_AUDIT_ID_PATH = ARTIFACTS_DIR / "label_audit_indonesia.md"
LABEL_MAPPING_ID_PATH = ARTIFACTS_DIR / "label_mapping_id.json"
LABEL_EXPANSION_DECISION_PATH = ARTIFACTS_DIR / "indonesia_label_expansion_decision.md"
MODEL_COMPARISON_ID_PATH = ARTIFACTS_DIR / "model_comparison_id.csv"
BEST_MODEL_METRICS_ID_PATH = ARTIFACTS_DIR / "best_model_metrics_id.json"
BEST_MODEL_SUMMARY_ID_PATH = ARTIFACTS_DIR / "best_model_summary_id.md"
BEST_MODEL_CLASSIFICATION_REPORT_ID_PATH = ARTIFACTS_DIR / "classification_report_best_model_id.txt"
BEST_MODEL_CONFUSION_MATRIX_ID_PATH = ARTIFACTS_DIR / "confusion_matrix_best_model_id.png"

BEST_ZONE_MODEL_ID_PATH = MODELS_DIR / "best_zone_model_id.joblib"
BEST_ZONE_PIPELINE_ID_PATH = PIPELINES_DIR / "best_zone_pipeline_id.joblib"

SCORING = {
    "accuracy": "accuracy",
    "precision_macro": make_scorer(precision_score, average="macro", zero_division=0),
    "recall_macro": make_scorer(recall_score, average="macro", zero_division=0),
    "f1_macro": make_scorer(f1_score, average="macro", zero_division=0),
    "f1_weighted": make_scorer(f1_score, average="weighted", zero_division=0),
}


def evaluate_predictions(y_true: pd.Series | np.ndarray, y_pred: Any) -> dict[str, float]:
    predictions = flatten_predictions(y_pred)
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision_macro": float(precision_score(y_true, predictions, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, predictions, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, predictions, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, predictions, average="weighted", zero_division=0)),
    }


def map_labels_to_indonesia(frame: pd.DataFrame, target_column: str) -> pd.DataFrame:
    mapped = frame.copy()
    mapped[target_column] = mapped[target_column].map(LABEL_MAPPING_ID).fillna(mapped[target_column])
    return mapped


def get_model_candidates(random_state: int = RANDOM_STATE) -> dict[str, Any]:
    return {
        "logistic_regression": LogisticRegression(
            max_iter=4000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=240,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=1,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=260,
            class_weight="balanced_subsample",
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=1,
        ),
        "lightgbm": LGBMClassifier(
            n_estimators=120,
            learning_rate=0.05,
            num_leaves=15,
            min_child_samples=3,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=1,
            verbosity=-1,
        ),
        "catboost": FlattenPredictionClassifier(
            estimator=CatBoostClassifier(
                iterations=120,
                depth=4,
                learning_rate=0.05,
                loss_function="MultiClass",
                auto_class_weights="Balanced",
                random_seed=random_state,
                thread_count=1,
                verbose=False,
            )
        ),
        "xgboost": StringLabelXGBClassifier(
            estimator=XGBClassifier(
                objective="multi:softprob",
                eval_metric="mlogloss",
                n_estimators=120,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=random_state,
                n_jobs=1,
                tree_method="hist",
            )
        ),
    }


def get_search_space(model_name: str) -> dict[str, list[Any]]:
    if model_name == "logistic_regression":
        return {"model__C": [0.1, 0.3, 1.0, 3.0, 10.0]}
    if model_name in {"random_forest", "extra_trees"}:
        return {
            "model__n_estimators": [120, 240, 360],
            "model__max_depth": [None, 6, 10],
            "model__min_samples_leaf": [1, 2, 4],
            "model__max_features": ["sqrt", 0.8],
        }
    if model_name == "lightgbm":
        return {
            "model__n_estimators": [40, 80, 120],
            "model__learning_rate": [0.03, 0.05, 0.1],
            "model__num_leaves": [7, 15, 31],
            "model__min_child_samples": [1, 3, 5],
            "model__subsample": [0.8, 1.0],
            "model__colsample_bytree": [0.8, 1.0],
        }
    if model_name == "catboost":
        return {
            "model__estimator__iterations": [60, 120, 180],
            "model__estimator__depth": [3, 4, 6],
            "model__estimator__learning_rate": [0.03, 0.05, 0.1],
            "model__estimator__l2_leaf_reg": [1, 3, 5],
        }
    if model_name == "xgboost":
        return {
            "model__estimator__n_estimators": [40, 80, 120],
            "model__estimator__max_depth": [3, 4, 6],
            "model__estimator__learning_rate": [0.03, 0.05, 0.1],
            "model__estimator__subsample": [0.8, 1.0],
            "model__estimator__colsample_bytree": [0.8, 1.0],
        }
    raise KeyError(f"Unknown model name: {model_name}")


def parameter_space_size(search_space: dict[str, list[Any]]) -> int:
    total = 1
    for values in search_space.values():
        total *= len(values)
    return total


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


def compare_models_with_group_cv(
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
        try:
            scores = cross_validate(
                pipeline,
                frame[feature_columns],
                y,
                cv=cv,
                scoring=SCORING,
                groups=groups,
                n_jobs=1,
                return_train_score=False,
                error_score="raise",
            )
            rows.append(
                {
                    "model_name": model_name,
                    "fit_status": "success",
                    "selection_strategy": cv_strategy,
                    "cv_splits": int(cv_splits),
                    "cv_accuracy_mean": float(scores["test_accuracy"].mean()),
                    "cv_precision_macro_mean": float(scores["test_precision_macro"].mean()),
                    "cv_recall_macro_mean": float(scores["test_recall_macro"].mean()),
                    "cv_f1_macro_mean": float(scores["test_f1_macro"].mean()),
                    "cv_f1_weighted_mean": float(scores["test_f1_weighted"].mean()),
                    "cv_accuracy_std": float(scores["test_accuracy"].std()),
                    "cv_f1_macro_std": float(scores["test_f1_macro"].std()),
                    "error_message": "",
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "model_name": model_name,
                    "fit_status": "failed",
                    "selection_strategy": cv_strategy,
                    "cv_splits": int(cv_splits),
                    "cv_accuracy_mean": np.nan,
                    "cv_precision_macro_mean": np.nan,
                    "cv_recall_macro_mean": np.nan,
                    "cv_f1_macro_mean": np.nan,
                    "cv_f1_weighted_mean": np.nan,
                    "cv_accuracy_std": np.nan,
                    "cv_f1_macro_std": np.nan,
                    "error_message": f"{type(exc).__name__}: {exc}",
                }
            )

    comparison_df = pd.DataFrame(rows)
    comparison_df["fit_rank"] = np.where(comparison_df["fit_status"] == "success", 0, 1)
    comparison_df = comparison_df.sort_values(
        ["fit_rank", "cv_f1_macro_mean", "cv_accuracy_mean"],
        ascending=[True, False, False],
    ).drop(columns="fit_rank").reset_index(drop=True)
    return comparison_df


def tune_model(
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    group_column: str,
    model_name: str,
    random_state: int = RANDOM_STATE,
) -> tuple[Pipeline, dict[str, Any], float]:
    numeric_features, categorical_features = infer_feature_types(frame, feature_columns)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    model = get_model_candidates(random_state=random_state)[model_name]
    pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])
    search_space = get_search_space(model_name)
    cv, _, _ = make_group_cv(
        y=frame[target_column],
        groups=frame[group_column],
        requested_splits=min(4, frame[group_column].nunique()),
        random_state=random_state,
    )

    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=search_space,
        n_iter=min(6, parameter_space_size(search_space)),
        scoring="f1_macro",
        cv=cv,
        n_jobs=1,
        random_state=random_state,
        refit=True,
        verbose=0,
    )
    search.fit(frame[feature_columns], frame[target_column], groups=frame[group_column])
    return search.best_estimator_, dict(search.best_params_), float(search.best_score_)


def scenario_dev_test_split(
    scenario_frame: pd.DataFrame,
    dev_zone_ids: set[str],
    test_zone_ids: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dev_frame = scenario_frame.loc[scenario_frame["zone_id"].isin(dev_zone_ids)].reset_index(drop=True)
    test_frame = scenario_frame.loc[scenario_frame["zone_id"].isin(test_zone_ids)].reset_index(drop=True)
    return dev_frame, test_frame


def evaluate_final_model(
    model: Pipeline,
    test_frame: pd.DataFrame,
    feature_columns: list[str],
    labels: list[str],
) -> tuple[dict[str, float], dict[str, Any], list[list[int]]]:
    predictions = flatten_predictions(model.predict(test_frame[feature_columns]))
    metrics = evaluate_predictions(test_frame[ZONE_TARGET_COLUMN], predictions)
    report = classification_report(
        test_frame[ZONE_TARGET_COLUMN],
        predictions,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(test_frame[ZONE_TARGET_COLUMN], predictions, labels=labels)
    return metrics, report, matrix.tolist()


def write_label_mapping() -> None:
    LABEL_MAPPING_ID_PATH.write_text(
        json.dumps(LABEL_MAPPING_ID, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_label_audit(
    zone_extended_df: pd.DataFrame,
    source_point_counts: dict[str, int],
    candidate_zone_counts: dict[str, int],
    retained_zone_counts: dict[str, int],
) -> None:
    metadata = json.loads(ZONE_METADATA_PATH.read_text(encoding="utf-8"))
    hidden_candidates = {
        label: count
        for label, count in source_point_counts.items()
        if label not in retained_zone_counts
    }
    content = f"""# Audit Label Indonesia

## Dataset Aktif

- File sumber zona aktif: `data/processed/zone_dataset_extended.csv`
- File output label Indonesia: `data/processed/zone_dataset_extended_id.csv`
- Target column aktif: `{ZONE_TARGET_COLUMN}`
- Unique labels aktif: {sorted(zone_extended_df[ZONE_TARGET_COLUMN].unique().tolist())}
- Distribusi label aktif: {zone_extended_df[ZONE_TARGET_COLUMN].value_counts().to_dict()}

## Mapping Label ke Bahasa Indonesia

- Barley -> Jelai
- Maize -> Jagung
- Teff -> Teff
- Wheat -> Gandum

## Audit Source Data

- Source dataset: `{metadata.get('source_dataset')}`
- Label titik setelah normalisasi: {source_point_counts}
- Kandidat label di level zona sebelum filter kualitas: {candidate_zone_counts}
- Label final yang lolos filter kualitas dan support kelas: {retained_zone_counts}

## Temuan Penting

1. Source data titik memang mengandung label tambahan seperti `Bean`, `Pea`, `Sorghum`, `Dagussa`, `Niger Seed`, `Potato`, dan `Red Pepper`.
2. Tidak ada label tambahan tersebut yang lolos sampai dataset zona final aktif. Setelah filter kualitas zona dan minimum support kelas, hanya empat label yang tersisa.
3. Beberapa label tambahan tidak bisa dipetakan langsung ke tanaman umum Indonesia secara sah. Contoh: `Bean` terlalu ambigu untuk dipaksa menjadi `Kedelai` atau `Kacang Tanah`.
4. Label yang masih tersisa dapat diterjemahkan ke Bahasa Indonesia tanpa mengubah makna agronominya.

## Hidden / Non-Retained Candidates

{hidden_candidates}
"""
    LABEL_AUDIT_ID_PATH.write_text(content, encoding="utf-8")


def write_expansion_decision(
    source_point_counts: dict[str, int],
    quality_kept_zone_counts: dict[str, int],
    retained_zone_counts: dict[str, int],
) -> None:
    content = f"""# Keputusan Ekspansi Label Indonesia

## Keputusan

Pendekatan yang dipilih adalah **B**:

- tidak menambahkan kelas baru khas Indonesia ke dataset training aktif
- hanya menerjemahkan label final yang sudah valid ke Bahasa Indonesia
- melatih ulang model pada label terjemahan tersebut

## Alasan

1. Dataset zona aktif yang valid saat ini hanya berisi empat kelas final: {retained_zone_counts}.
2. Label tambahan pada source point data ({source_point_counts}) tidak bertahan pada level zona dengan kualitas yang memadai.
3. Setelah filter kualitas zona (`min_samples_per_zone >= {ZONE_BUILDER_PARAMS['min_samples_per_zone']}` dan dominant label ratio `>= {ZONE_BUILDER_PARAMS['min_zone_label_dominance_ratio']}`), label yang tersisa tetap hanya {quality_kept_zone_counts}.
4. Tidak ada dasar yang sah untuk mengganti label seperti `Wheat` menjadi `Padi` atau `Barley` menjadi `Singkong`.
5. Label seperti `Bean` terlalu umum dan tidak dapat dipetakan secara aman ke `Kedelai` atau `Kacang Tanah`.

## Implikasi

- Model hasil pembaruan tetap terbatas pada empat tanaman: `Jelai`, `Jagung`, `Teff`, `Gandum`.
- Model belum dapat mengeluarkan rekomendasi untuk `Padi`, `Kedelai`, `Singkong`, `Ubi Jalar`, `Tebu`, `Kacang Tanah`, `Cabai`, atau `Bawang Merah`.

## Data Tambahan yang Dibutuhkan

Untuk mendukung tanaman yang umum di Indonesia secara valid, dibutuhkan salah satu dari:

1. dataset zona dengan label tanaman Indonesia yang eksplisit
2. raw point data dengan label yang jelas dan cukup support untuk membentuk zona berkualitas
3. field/grid geospasial Indonesia yang bisa di-join dengan crop presence atau suitability label yang tervalidasi
"""
    LABEL_EXPANSION_DECISION_PATH.write_text(content, encoding="utf-8")


def plot_confusion_matrix(matrix: list[list[int]], labels: list[str]) -> None:
    array = np.asarray(matrix)
    fig, ax = plt.subplots(figsize=(7, 5))
    image = ax.imshow(array, cmap="Blues")
    plt.colorbar(image, ax=ax)
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_yticklabels(labels)
    ax.set_xlabel("Prediksi")
    ax.set_ylabel("Aktual")
    ax.set_title("Confusion Matrix Best Model (ID Labels)")
    for row_index in range(array.shape[0]):
        for col_index in range(array.shape[1]):
            ax.text(col_index, row_index, int(array[row_index, col_index]), ha="center", va="center", color="black")
    fig.tight_layout()
    fig.savefig(BEST_MODEL_CONFUSION_MATRIX_ID_PATH, dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_summary(
    best_result: dict[str, Any],
    baseline_metrics: dict[str, Any],
    final_distribution: dict[str, int],
) -> None:
    baseline_test = baseline_metrics.get("selected_zone_test_metrics", {})
    baseline_name = baseline_metrics.get("selected_zone_model_name", "unknown_model")
    baseline_scenario = baseline_metrics.get("selected_zone_scenario", "unknown_scenario")
    best_test = best_result["test_metrics"]
    improvement_accuracy = (
        best_test["accuracy"] - baseline_test["accuracy"]
        if "accuracy" in baseline_test
        else math.nan
    )
    improvement_f1 = (
        best_test["f1_macro"] - baseline_test["f1_macro"]
        if "f1_macro" in baseline_test
        else math.nan
    )
    summary = f"""# Best Model Summary (Indonesia Labels)

## Final Selection

- Best scenario: `{best_result['scenario_name']}`
- Best model: `{best_result['best_model_name']}`
- Selection metric: macro F1 on group-aware CV
- Best CV macro F1: {best_result['tuned_cv_f1_macro']:.4f}

## Holdout Test Metrics

- Accuracy: {best_test['accuracy']:.4f}
- Macro precision: {best_test['precision_macro']:.4f}
- Macro recall: {best_test['recall_macro']:.4f}
- Macro F1: {best_test['f1_macro']:.4f}
- Weighted F1: {best_test['f1_weighted']:.4f}

## Comparison vs Previous Active Baseline

- Previous active model: `{baseline_name}` on `{baseline_scenario}`
- Previous test accuracy: {baseline_test.get('accuracy', float('nan')):.4f}
- Previous test macro F1: {baseline_test.get('f1_macro', float('nan')):.4f}
- Accuracy delta: {improvement_accuracy:.4f}
- Macro F1 delta: {improvement_f1:.4f}

## Final Class Distribution

{final_distribution}

## Deployment Note

Artifact baru disimpan terpisah agar tidak mengganti model API aktif secara diam-diam. Model baru siap dipakai oleh API jika path artifact diarahkan ke file `*_id.joblib` dan environment runtime memuat dependency yang relevan.
"""
    BEST_MODEL_SUMMARY_ID_PATH.write_text(summary, encoding="utf-8")


def write_model_selection_analysis(
    zone_extended_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    split_contexts: dict[str, list[int]],
    best_result: dict[str, Any],
    baseline_metrics: dict[str, Any],
) -> None:
    baseline_test = baseline_metrics.get("selected_zone_test_metrics", {})
    comparison_table = comparison_df.to_string(index=False)
    content = f"""# Model Selection Analysis (Indonesia Labels)

## Dataset Audit

- Dataset aktif: `data/processed/zone_dataset_extended_id.csv`
- Jumlah zona: {zone_extended_df.shape[0]}
- Jumlah fitur extended: {zone_extended_df.shape[1] - 1}
- Target column: `{ZONE_TARGET_COLUMN}`
- Distribusi kelas: {zone_extended_df[ZONE_TARGET_COLUMN].value_counts().to_dict()}
- Jumlah group konteks (`base_context_id`): {zone_extended_df['base_context_id'].nunique()}

## Split Strategy

- Split utama: group-aware holdout berdasarkan `base_context_id`
- Dev contexts: {split_contexts['dev']}
- Test contexts: {split_contexts['test']}
- Seleksi model: group-aware CV pada dev split
- Metrik seleksi utama: macro F1

## Candidate Models

```
{comparison_table}
```

## Selection Decision

1. Model dipilih berdasarkan macro F1 pada group-aware CV, bukan accuracy test.
2. Scenario final: `{best_result['scenario_name']}`
3. Model final: `{best_result['best_model_name']}`
4. Holdout test accuracy: {best_result['test_metrics']['accuracy']:.4f}
5. Holdout test macro F1: {best_result['test_metrics']['f1_macro']:.4f}
6. Baseline model aktif sebelumnya memiliki accuracy {baseline_test.get('accuracy', float('nan')):.4f} dan macro F1 {baseline_test.get('f1_macro', float('nan')):.4f}.

## Interpretation

- Karena dataset sangat kecil dan tidak seimbang, macro F1 lebih representatif daripada accuracy semata.
- Pergantian label ke Bahasa Indonesia tidak menambah informasi baru pada fitur; perubahan performa, jika ada, berasal dari pemilihan model dan tuning, bukan dari translasi label itu sendiri.
"""
    (ARTIFACTS_DIR / "model_selection_analysis.md").write_text(content, encoding="utf-8")


def main() -> dict[str, Any]:
    ensure_project_dirs()
    write_label_mapping()

    zone_extended_df = pd.read_csv(ZONE_DATASET_EXTENDED_PATH)
    zone_minimal_df = pd.read_csv(ZONE_DATASET_MINIMAL_PATH)

    zone_extended_id_df = map_labels_to_indonesia(zone_extended_df, ZONE_TARGET_COLUMN)
    zone_minimal_id_df = map_labels_to_indonesia(zone_minimal_df, ZONE_TARGET_COLUMN)

    zone_extended_id_df.to_csv(ZONE_DATASET_EXTENDED_ID_PATH, index=False)
    zone_minimal_id_df.to_csv(ZONE_DATASET_MINIMAL_ID_PATH, index=False)

    point_df = normalize_point_dataframe()
    point_label_counts = point_df[TARGET_COLUMN].value_counts().to_dict()
    point_with_zones = assign_zone_ids(point_df, ZONE_BUILDER_PARAMS)
    zone_stats, kept_zone_stats = build_zone_statistics(point_with_zones, ZONE_BUILDER_PARAMS)

    candidate_zone_counts = zone_stats[ZONE_TARGET_COLUMN].value_counts().to_dict()
    quality_kept_zone_counts = zone_stats.loc[
        zone_stats["zone_quality_flag"] == "kept", ZONE_TARGET_COLUMN
    ].value_counts().to_dict()
    retained_zone_counts = kept_zone_stats[ZONE_TARGET_COLUMN].value_counts().to_dict()

    write_label_audit(
        zone_extended_df=zone_extended_id_df,
        source_point_counts=point_label_counts,
        candidate_zone_counts=candidate_zone_counts,
        retained_zone_counts=retained_zone_counts,
    )
    write_expansion_decision(
        source_point_counts=point_label_counts,
        quality_kept_zone_counts=quality_kept_zone_counts,
        retained_zone_counts=retained_zone_counts,
    )

    zone_views = build_zone_views(zone_minimal_id_df, zone_extended_id_df)

    dev_idx, test_idx = choose_best_group_split(
        y=zone_extended_id_df[ZONE_TARGET_COLUMN],
        groups=zone_extended_id_df["base_context_id"],
        n_splits=min(4, zone_extended_id_df["base_context_id"].nunique()),
        random_state=RANDOM_STATE,
    )
    dev_zone_ids = set(zone_extended_id_df.iloc[dev_idx]["zone_id"].tolist())
    test_zone_ids = set(zone_extended_id_df.iloc[test_idx]["zone_id"].tolist())

    baseline_metrics = {}
    if ZONE_MODEL_METRICS_PATH.exists():
        baseline_metrics = json.loads(ZONE_MODEL_METRICS_PATH.read_text(encoding="utf-8"))

    comparison_rows: list[dict[str, Any]] = []
    scenario_results: dict[str, dict[str, Any]] = {}

    for scenario_name, scenario in zone_views.items():
        dev_frame, test_frame = scenario_dev_test_split(scenario["frame"], dev_zone_ids, test_zone_ids)
        comparison_df = compare_models_with_group_cv(
            frame=dev_frame,
            feature_columns=scenario["feature_columns"],
            target_column=ZONE_TARGET_COLUMN,
            group_column="base_context_id",
            random_state=RANDOM_STATE,
        )
        successful_candidates = comparison_df.loc[comparison_df["fit_status"] == "success"].reset_index(drop=True)
        if successful_candidates.empty:
            raise RuntimeError(f"No successful candidates for scenario {scenario_name}.")

        top_models = successful_candidates.head(2)["model_name"].tolist()
        tuned_candidates: list[dict[str, Any]] = []

        for model_name in top_models:
            tuned_estimator, best_params, tuned_cv_f1 = tune_model(
                frame=dev_frame,
                feature_columns=scenario["feature_columns"],
                target_column=ZONE_TARGET_COLUMN,
                group_column="base_context_id",
                model_name=model_name,
                random_state=RANDOM_STATE,
            )
            labels = sorted(dev_frame[ZONE_TARGET_COLUMN].unique().tolist())
            test_metrics, class_report, matrix = evaluate_final_model(
                model=tuned_estimator,
                test_frame=test_frame,
                feature_columns=scenario["feature_columns"],
                labels=labels,
            )
            tuned_candidates.append(
                {
                    "scenario_name": scenario_name,
                    "best_model_name": model_name,
                    "best_model": tuned_estimator,
                    "best_params": best_params,
                    "tuned_cv_f1_macro": tuned_cv_f1,
                    "test_metrics": test_metrics,
                    "classification_report": class_report,
                    "confusion_matrix_labels": labels,
                    "confusion_matrix": matrix,
                    "feature_columns": scenario["feature_columns"],
                    "dev_frame": dev_frame,
                    "test_frame": test_frame,
                }
            )

        best_scenario_candidate = max(
            tuned_candidates,
            key=lambda item: (
                item["tuned_cv_f1_macro"],
                item["test_metrics"]["f1_macro"],
                item["test_metrics"]["accuracy"],
            ),
        )
        scenario_results[scenario_name] = {
            "comparison_df": comparison_df,
            "winner": best_scenario_candidate,
        }

        for _, row in comparison_df.iterrows():
            record = {
                "scenario_name": scenario_name,
                "model_name": row["model_name"],
                "fit_status": row["fit_status"],
                "selection_strategy": row["selection_strategy"],
                "cv_splits": row["cv_splits"],
                "cv_accuracy_mean": row["cv_accuracy_mean"],
                "cv_precision_macro_mean": row["cv_precision_macro_mean"],
                "cv_recall_macro_mean": row["cv_recall_macro_mean"],
                "cv_f1_macro_mean": row["cv_f1_macro_mean"],
                "cv_f1_weighted_mean": row["cv_f1_weighted_mean"],
                "cv_accuracy_std": row["cv_accuracy_std"],
                "cv_f1_macro_std": row["cv_f1_macro_std"],
                "selected_for_tuning": row["model_name"] in top_models,
                "is_scenario_winner": row["model_name"] == best_scenario_candidate["best_model_name"],
                "is_final_selected": False,
                "tuned_cv_f1_macro": np.nan,
                "test_accuracy": np.nan,
                "test_precision_macro": np.nan,
                "test_recall_macro": np.nan,
                "test_f1_macro": np.nan,
                "test_f1_weighted": np.nan,
                "best_params_json": "",
                "error_message": row["error_message"],
            }
            if row["model_name"] == best_scenario_candidate["best_model_name"]:
                record["tuned_cv_f1_macro"] = best_scenario_candidate["tuned_cv_f1_macro"]
                record["test_accuracy"] = best_scenario_candidate["test_metrics"]["accuracy"]
                record["test_precision_macro"] = best_scenario_candidate["test_metrics"]["precision_macro"]
                record["test_recall_macro"] = best_scenario_candidate["test_metrics"]["recall_macro"]
                record["test_f1_macro"] = best_scenario_candidate["test_metrics"]["f1_macro"]
                record["test_f1_weighted"] = best_scenario_candidate["test_metrics"]["f1_weighted"]
                record["best_params_json"] = json.dumps(best_scenario_candidate["best_params"], ensure_ascii=False)
            comparison_rows.append(record)

    best_result = max(
        [scenario_results[name]["winner"] for name in scenario_results],
        key=lambda item: (
            item["tuned_cv_f1_macro"],
            item["test_metrics"]["f1_macro"],
            item["test_metrics"]["accuracy"],
        ),
    )

    comparison_df = pd.DataFrame(comparison_rows)
    comparison_df.loc[
        (comparison_df["scenario_name"] == best_result["scenario_name"])
        & (comparison_df["model_name"] == best_result["best_model_name"]),
        "is_final_selected",
    ] = True
    comparison_df.to_csv(MODEL_COMPARISON_ID_PATH, index=False)

    BEST_MODEL_CLASSIFICATION_REPORT_ID_PATH.write_text(
        classification_report(
            best_result["test_frame"][ZONE_TARGET_COLUMN],
            flatten_predictions(best_result["best_model"].predict(best_result["test_frame"][best_result["feature_columns"]])),
            labels=best_result["confusion_matrix_labels"],
            zero_division=0,
        ),
        encoding="utf-8",
    )
    plot_confusion_matrix(best_result["confusion_matrix"], best_result["confusion_matrix_labels"])

    joblib.dump(best_result["best_model"], BEST_ZONE_MODEL_ID_PATH)
    joblib.dump(best_result["best_model"].named_steps["preprocessor"], BEST_ZONE_PIPELINE_ID_PATH)

    split_contexts = {
        "dev": sorted(zone_extended_id_df.loc[zone_extended_id_df["zone_id"].isin(dev_zone_ids), "base_context_id"].unique().tolist()),
        "test": sorted(zone_extended_id_df.loc[zone_extended_id_df["zone_id"].isin(test_zone_ids), "base_context_id"].unique().tolist()),
    }

    metrics_payload = {
        "label_mapping": LABEL_MAPPING_ID,
        "target_column": ZONE_TARGET_COLUMN,
        "zone_dataset_path": str(ZONE_DATASET_EXTENDED_ID_PATH.relative_to(PROJECT_ROOT)),
        "class_distribution": zone_extended_id_df[ZONE_TARGET_COLUMN].value_counts().to_dict(),
        "split_strategy": {
            "type": "group_aware_holdout_plus_group_cv",
            "group_column": "base_context_id",
            "dev_contexts": split_contexts["dev"],
            "test_contexts": split_contexts["test"],
        },
        "zone_mean_only": {
            "feature_columns": zone_views["zone_mean_only"]["feature_columns"],
            "model_comparison": scenario_results["zone_mean_only"]["comparison_df"].to_dict(orient="records"),
            "best_model_name": scenario_results["zone_mean_only"]["winner"]["best_model_name"],
            "best_model_params": scenario_results["zone_mean_only"]["winner"]["best_params"],
            "tuned_cv_f1_macro": scenario_results["zone_mean_only"]["winner"]["tuned_cv_f1_macro"],
            "test_metrics": scenario_results["zone_mean_only"]["winner"]["test_metrics"],
        },
        "zone_mean_plus_variability": {
            "feature_columns": zone_views["zone_mean_plus_variability"]["feature_columns"],
            "model_comparison": scenario_results["zone_mean_plus_variability"]["comparison_df"].to_dict(orient="records"),
            "best_model_name": scenario_results["zone_mean_plus_variability"]["winner"]["best_model_name"],
            "best_model_params": scenario_results["zone_mean_plus_variability"]["winner"]["best_params"],
            "tuned_cv_f1_macro": scenario_results["zone_mean_plus_variability"]["winner"]["tuned_cv_f1_macro"],
            "test_metrics": scenario_results["zone_mean_plus_variability"]["winner"]["test_metrics"],
        },
        "selected_zone_scenario": best_result["scenario_name"],
        "selected_zone_model_name": best_result["best_model_name"],
        "selected_zone_model_params": best_result["best_params"],
        "selected_zone_cv_metric_name": "f1_macro",
        "selected_zone_cv_metric_value": best_result["tuned_cv_f1_macro"],
        "selected_zone_test_metrics": best_result["test_metrics"],
        "selected_zone_confusion_matrix_labels": best_result["confusion_matrix_labels"],
        "selected_zone_confusion_matrix": best_result["confusion_matrix"],
        "selected_zone_classification_report": best_result["classification_report"],
        "baseline_previous_active_model": {
            "selected_zone_scenario": baseline_metrics.get("selected_zone_scenario"),
            "selected_zone_model_name": baseline_metrics.get("selected_zone_model_name"),
            "selected_zone_test_metrics": baseline_metrics.get("selected_zone_test_metrics"),
        },
        "artifacts": {
            "label_audit_indonesia": str(LABEL_AUDIT_ID_PATH.relative_to(PROJECT_ROOT)),
            "label_mapping_id": str(LABEL_MAPPING_ID_PATH.relative_to(PROJECT_ROOT)),
            "indonesia_label_expansion_decision": str(LABEL_EXPANSION_DECISION_PATH.relative_to(PROJECT_ROOT)),
            "zone_dataset_extended_id": str(ZONE_DATASET_EXTENDED_ID_PATH.relative_to(PROJECT_ROOT)),
            "model_comparison_id": str(MODEL_COMPARISON_ID_PATH.relative_to(PROJECT_ROOT)),
            "best_model_metrics_id": str(BEST_MODEL_METRICS_ID_PATH.relative_to(PROJECT_ROOT)),
            "best_model_summary_id": str(BEST_MODEL_SUMMARY_ID_PATH.relative_to(PROJECT_ROOT)),
            "classification_report_best_model_id": str(BEST_MODEL_CLASSIFICATION_REPORT_ID_PATH.relative_to(PROJECT_ROOT)),
            "confusion_matrix_best_model_id": str(BEST_MODEL_CONFUSION_MATRIX_ID_PATH.relative_to(PROJECT_ROOT)),
            "best_zone_model_id": str(BEST_ZONE_MODEL_ID_PATH.relative_to(PROJECT_ROOT)),
            "best_zone_pipeline_id": str(BEST_ZONE_PIPELINE_ID_PATH.relative_to(PROJECT_ROOT)),
        },
        "notes": [
            "Tidak ada kelas baru khas Indonesia yang ditambahkan karena dataset zona aktif tidak mendukungnya secara valid.",
            "Translasi label ke Bahasa Indonesia tidak mengubah fitur input, hanya representasi target kelas.",
            "Model dipilih berdasarkan macro F1 pada group-aware CV untuk mengurangi bias akibat class imbalance dan ukuran dataset yang kecil.",
        ],
    }
    BEST_MODEL_METRICS_ID_PATH.write_text(json.dumps(metrics_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    write_summary(
        best_result=best_result,
        baseline_metrics=baseline_metrics,
        final_distribution=zone_extended_id_df[ZONE_TARGET_COLUMN].value_counts().to_dict(),
    )
    write_model_selection_analysis(
        zone_extended_df=zone_extended_id_df,
        comparison_df=comparison_df,
        split_contexts=split_contexts,
        best_result=best_result,
        baseline_metrics=baseline_metrics,
    )
    return metrics_payload


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))
