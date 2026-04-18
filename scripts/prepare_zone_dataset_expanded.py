from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_zone_dataset import aggregate_numeric_features
from scripts.common import ARTIFACTS_DIR, CSV_DIR, PROCESSED_DIR, PROJECT_ROOT, RANDOM_STATE, ZONE_TARGET_COLUMN, ensure_project_dirs


ACTIVE_ZONE_DATASET_ID_PATH = PROCESSED_DIR / "zone_dataset_extended_id.csv"
KAGGLE_MIRROR_PATH = CSV_DIR / "crop_recommendation_kaggle_mirror.csv"
RICE_FERTILITY_ZENODO_PATH = CSV_DIR / "rice_npk_fertility_zenodo.csv"
SUGARCANE_GITHUB_PATH = CSV_DIR / "sugarcane_data_github.csv"
AGRICULTURE_GIST_PATH = CSV_DIR / "agriculture_dataset_gist.csv"
CROP_RECOMMEND_GIST_PATH = CSV_DIR / "crop_recommend_gist.csv"

ARCHIVE_DIR = PROJECT_ROOT / "archive" / "legacy_pre_zone"
MENDELEY_VYNX_PATH = ARCHIVE_DIR / "datasets" / "csv" / "mendeley_vynxnppr7j_crop_recommendation.csv"
ZENODO_17_CROPS_PATH = ARCHIVE_DIR / "datasets" / "csv" / "zenodo_17666722_training_samples_combined.csv"

SCREENING_PATH = ARTIFACTS_DIR / "dataset_expansion_screening.csv"
DECISION_PATH = ARTIFACTS_DIR / "dataset_expansion_decision.md"
INTEGRATION_STRATEGY_PATH = ARTIFACTS_DIR / "dataset_integration_strategy.md"
LABEL_MAPPING_EXPANDED_PATH = ARTIFACTS_DIR / "label_mapping_expanded_id.json"
READINESS_PATH = ARTIFACTS_DIR / "retraining_readiness_expanded.md"
EXPANDED_FEATURE_SUMMARY_PATH = ARTIFACTS_DIR / "zone_feature_summary_expanded.csv"

EXPANDED_DATASET_PATH = PROCESSED_DIR / "zone_dataset_expanded_id.csv"
EXPANDED_DATASET_MINIMAL_PATH = PROCESSED_DIR / "zone_dataset_expanded_id_minimal.csv"
EXPANDED_METADATA_PATH = PROCESSED_DIR / "zone_dataset_expanded_id_metadata.json"

FINAL_NUMERIC_FAMILIES = [
    "ph",
    "nitrogen",
    "phosphorus",
    "potassium",
    "temperature_mean",
    "rainfall_mean",
]
FINAL_BASE_COLUMNS = [
    "zone_id",
    "base_context_id",
    "source_dataset",
    "source_region",
    "integration_strategy",
    "sample_count",
    "context_sample_count",
    "context_cluster_count",
    "sample_count_risk_flag",
]
FINAL_EXTENDED_BASE_COLUMNS = FINAL_BASE_COLUMNS + [
    "label_nunique",
    "zone_label_dominance_ratio",
]
FINAL_MINIMAL_COLUMNS = FINAL_BASE_COLUMNS + [f"{feature}_mean" for feature in FINAL_NUMERIC_FAMILIES] + [ZONE_TARGET_COLUMN]
FINAL_EXTENDED_COLUMNS = FINAL_EXTENDED_BASE_COLUMNS + [
    f"{feature}_{suffix}"
    for feature in FINAL_NUMERIC_FAMILIES
    for suffix in ["mean", "std", "min", "max", "median", "count", "range", "cv", "missing_ratio"]
] + [ZONE_TARGET_COLUMN]

KAGGLE_SELECTED_CROPS = {
    "Rice",
    "Maize",
    "Banana",
    "Coconut",
    "Coffee",
    "Mango",
    "Orange",
    "Papaya",
    "Watermelon",
    "MungBean",
}
KAGGLE_REGION_NOTE = "Kaggle benchmark / global-generalized crop suitability"
ACTIVE_REGION_NOTE = "Ethiopia"

LABEL_MAPPING_EXPANDED_ID = {
    "Barley": "Jelai",
    "Wheat": "Gandum",
    "Teff": "Teff",
    "Maize": "Jagung",
    "Rice": "Padi",
    "Banana": "Pisang",
    "Coconut": "Kelapa",
    "Coffee": "Kopi",
    "Mango": "Mangga",
    "Orange": "Jeruk",
    "Papaya": "Pepaya",
    "Watermelon": "Semangka",
    "MungBean": "Kacang Hijau",
}


@dataclass(frozen=True)
class PseudoZoneParams:
    source_prefix: str
    target_zone_size: int = 20
    min_samples_per_zone: int = 8
    min_dominance_ratio: float = 0.60
    min_zones_per_class: int = 3
    climate_bins: tuple[tuple[str, int], ...] = (
        ("temperature_mean", 6),
        ("rainfall_mean", 6),
        ("humidity", 5),
    )
    cluster_features: tuple[str, ...] = ("ph", "nitrogen", "phosphorus", "potassium")


def dominant_value(series: pd.Series) -> Any:
    modes = series.mode(dropna=True)
    if not modes.empty:
        return modes.iloc[0]
    non_null = series.dropna()
    if not non_null.empty:
        return non_null.iloc[0]
    return np.nan


def safe_qcut(series: pd.Series, bins: int) -> pd.Series:
    if series.dropna().nunique() <= 1:
        return pd.Series([0] * len(series), index=series.index, dtype="Int64")
    try:
        return pd.qcut(series, q=min(bins, series.dropna().nunique()), labels=False, duplicates="drop").astype("Int64")
    except ValueError:
        return pd.Series([0] * len(series), index=series.index, dtype="Int64")


def load_active_zone_standardized() -> tuple[pd.DataFrame, pd.DataFrame]:
    active_df = pd.read_csv(ACTIVE_ZONE_DATASET_ID_PATH).copy()
    standardized = pd.DataFrame(index=active_df.index)
    standardized["zone_id"] = active_df["zone_id"].astype(str).map(lambda value: f"active::{value}")
    standardized["base_context_id"] = active_df["base_context_id"].astype(str).map(lambda value: f"active::{value}")
    standardized["source_dataset"] = active_df["source_dataset"].fillna("active_zone_dataset")
    standardized["source_region"] = ACTIVE_REGION_NOTE
    standardized["integration_strategy"] = "native_zone_dataset"
    for column in ["sample_count", "context_sample_count", "context_cluster_count", "label_nunique", "zone_label_dominance_ratio", "sample_count_risk_flag"]:
        standardized[column] = active_df[column]

    for feature in ["ph", "nitrogen", "phosphorus", "potassium"]:
        for suffix in ["mean", "std", "min", "max", "median", "count", "range", "cv", "missing_ratio"]:
            standardized[f"{feature}_{suffix}"] = active_df[f"{feature}_{suffix}"]

    for source_feature in ["temperature_mean", "rainfall_mean"]:
        for suffix in ["mean", "std", "min", "max", "median", "count", "range", "cv", "missing_ratio"]:
            standardized[f"{source_feature}_{suffix}"] = active_df[f"{source_feature}_{suffix}"]

    standardized[ZONE_TARGET_COLUMN] = active_df[ZONE_TARGET_COLUMN]
    minimal_df = standardized[FINAL_MINIMAL_COLUMNS].copy()
    extended_df = standardized[FINAL_EXTENDED_COLUMNS].copy()
    return minimal_df, extended_df


def load_kaggle_points() -> pd.DataFrame:
    df = pd.read_csv(KAGGLE_MIRROR_PATH).rename(
        columns={
            "Nitrogen": "nitrogen",
            "Phosphorus": "phosphorus",
            "Potassium": "potassium",
            "Temperature": "temperature_mean",
            "Humidity": "humidity",
            "pH_Value": "ph",
            "Rainfall": "rainfall_mean",
            "Crop": "target_crop",
        }
    )
    df = df.loc[df["target_crop"].isin(KAGGLE_SELECTED_CROPS)].copy()
    df["source_dataset"] = KAGGLE_MIRROR_PATH.stem
    df["source_region"] = KAGGLE_REGION_NOTE
    df["integration_strategy"] = "pseudo_zone_from_point_benchmark"
    df["point_id"] = [f"kaggle_point_{idx + 1:05d}" for idx in range(df.shape[0])]
    return df.reset_index(drop=True)


def assign_pseudo_zone_ids(point_df: pd.DataFrame, params: PseudoZoneParams) -> pd.DataFrame:
    enriched = point_df.copy()
    context_keys: list[str] = []
    for column_name, bin_count in params.climate_bins:
        bin_column = f"{column_name}_context_bin"
        enriched[bin_column] = safe_qcut(enriched[column_name], bin_count)
        context_keys.append(bin_column)

    enriched["base_context_local"] = enriched.groupby(context_keys, dropna=False).ngroup() + 1
    zone_ids = pd.Series(index=enriched.index, dtype="string")
    context_rows: list[dict[str, Any]] = []

    for local_context_id, context_frame in enriched.groupby("base_context_local", sort=True):
        sample_count = int(context_frame.shape[0])
        cluster_count = max(1, round(sample_count / params.target_zone_size))
        cluster_count = min(cluster_count, max(1, sample_count // 5)) if sample_count >= 10 else 1

        feature_frame = context_frame[list(params.cluster_features)].copy()
        feature_frame = feature_frame.fillna(feature_frame.median(numeric_only=True))
        unique_rows = max(1, int(feature_frame.drop_duplicates().shape[0]))
        cluster_count = min(cluster_count, unique_rows)

        if cluster_count <= 1:
            labels = np.zeros(sample_count, dtype=int)
        else:
            scaled = StandardScaler().fit_transform(feature_frame)
            labels = KMeans(n_clusters=cluster_count, random_state=RANDOM_STATE, n_init=10).fit_predict(scaled)

        base_context_id = f"{params.source_prefix}::ctx_{int(local_context_id):03d}"
        for row_index, cluster_label in zip(context_frame.index, labels):
            zone_ids.loc[row_index] = f"{params.source_prefix}::zone_{int(local_context_id):03d}_{int(cluster_label):02d}"

        context_rows.append(
            {
                "base_context_local": int(local_context_id),
                "base_context_id": base_context_id,
                "context_sample_count": sample_count,
                "context_cluster_count": int(cluster_count),
            }
        )

    enriched["zone_id"] = zone_ids
    context_summary = pd.DataFrame(context_rows)
    enriched = enriched.merge(context_summary, on="base_context_local", how="left")
    return enriched


def build_zone_statistics_generic(point_df: pd.DataFrame, params: PseudoZoneParams) -> tuple[pd.DataFrame, pd.DataFrame]:
    zone_stats = point_df.groupby("zone_id").agg(
        base_context_id=("base_context_id", "first"),
        source_dataset=("source_dataset", "first"),
        source_region=("source_region", "first"),
        integration_strategy=("integration_strategy", "first"),
        sample_count=("point_id", "size"),
        context_sample_count=("context_sample_count", "first"),
        context_cluster_count=("context_cluster_count", "first"),
        label_nunique=("target_crop", "nunique"),
    )
    zone_stats[ZONE_TARGET_COLUMN] = point_df.groupby("zone_id")["target_crop"].agg(dominant_value)
    zone_stats["zone_label_dominance_ratio"] = (
        point_df.groupby("zone_id")["target_crop"].value_counts(normalize=True).groupby(level=0).max()
    )
    zone_stats["sample_count_risk_flag"] = np.where(
        zone_stats["sample_count"] < params.min_samples_per_zone,
        "low_support",
        "ok",
    )

    kept = zone_stats.loc[
        (zone_stats["sample_count"] >= params.min_samples_per_zone)
        & (zone_stats["zone_label_dominance_ratio"] >= params.min_dominance_ratio)
    ].copy()
    class_counts = kept[ZONE_TARGET_COLUMN].value_counts()
    kept = kept.loc[kept[ZONE_TARGET_COLUMN].isin(class_counts[class_counts >= params.min_zones_per_class].index)].copy()
    return zone_stats.reset_index(), kept.reset_index()


def build_zone_frames_from_points(point_df: pd.DataFrame, kept_zone_stats: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    filtered_points = point_df.loc[point_df["zone_id"].isin(kept_zone_stats["zone_id"])].copy()
    base_columns = [
        "zone_id",
        "base_context_id",
        "source_dataset",
        "source_region",
        "integration_strategy",
        "sample_count",
        "context_sample_count",
        "context_cluster_count",
        "label_nunique",
        "zone_label_dominance_ratio",
        "sample_count_risk_flag",
        ZONE_TARGET_COLUMN,
    ]
    zone_df = kept_zone_stats[base_columns].copy().set_index("zone_id")
    numeric_aggregates = aggregate_numeric_features(filtered_points, "zone_id", FINAL_NUMERIC_FAMILIES)
    zone_df = zone_df.join(numeric_aggregates, how="left").reset_index()
    minimal_df = zone_df[FINAL_MINIMAL_COLUMNS].copy()
    extended_df = zone_df[FINAL_EXTENDED_COLUMNS].copy()
    return minimal_df, extended_df


def build_kaggle_zone_frames() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    params = PseudoZoneParams(source_prefix="kaggle")
    kaggle_points = load_kaggle_points()
    kaggle_points = assign_pseudo_zone_ids(kaggle_points, params)
    candidate_zone_stats, kept_zone_stats = build_zone_statistics_generic(kaggle_points, params)
    minimal_df, extended_df = build_zone_frames_from_points(kaggle_points, kept_zone_stats)
    diagnostics = {
        "source_points": int(kaggle_points.shape[0]),
        "candidate_zone_count": int(candidate_zone_stats.shape[0]),
        "kept_zone_count": int(kept_zone_stats.shape[0]),
        "candidate_class_distribution": candidate_zone_stats[ZONE_TARGET_COLUMN].value_counts().to_dict(),
        "kept_class_distribution": kept_zone_stats[ZONE_TARGET_COLUMN].value_counts().to_dict(),
        "dominance_summary": kept_zone_stats["zone_label_dominance_ratio"].describe().to_dict()
        if not kept_zone_stats.empty
        else {},
    }
    return minimal_df, extended_df, diagnostics


def local_csv_profile(path: Path) -> dict[str, Any]:
    profile: dict[str, Any] = {
        "row_count": np.nan,
        "column_count": np.nan,
        "columns": "",
        "crop_classes_available": "",
    }
    if not path.exists():
        return profile
    try:
        frame = pd.read_csv(path)
    except Exception:
        return profile

    profile["row_count"] = int(frame.shape[0])
    profile["column_count"] = int(frame.shape[1])
    profile["columns"] = ", ".join(frame.columns.astype(str).tolist())
    for candidate_target in ["Crop", "crop", "target_crop", "CROPS", "species", "Crop_Type", "Fertility"]:
        if candidate_target in frame.columns:
            value_counts = frame[candidate_target].astype(str).value_counts()
            profile["crop_classes_available"] = ", ".join(value_counts.head(15).index.tolist())
            break
    return profile


def build_screening_frame() -> pd.DataFrame:
    records = [
        {
            "dataset_id": "ref_active_zone",
            "dataset_name": "Current active zone dataset",
            "provider": "Local processed project dataset",
            "source_type": "active_zone_dataset",
            "region_scope": "Ethiopia",
            "original_url": "",
            "download_url": "",
            "local_path": str(ACTIVE_ZONE_DATASET_ID_PATH.relative_to(PROJECT_ROOT)),
            "classes_or_targets": "Jelai, Jagung, Teff, Gandum",
            "features_summary": "zone-level aggregates for pH, N, P, K, zinc, sulfur, temperature, rainfall, soil moisture, pressure",
            "has_n": 1,
            "has_p": 1,
            "has_k": 1,
            "has_ph": 1,
            "has_temperature": 1,
            "has_rainfall": 1,
            "has_soil_moisture": 1,
            "is_tabular": 1,
            "target_label_clear": 1,
            "supervised_usable": 1,
            "compatible_with_zone_pipeline": 1,
            "selected_for_main_integration": 1,
            "integration_role": "base_anchor_dataset",
            "primary_risks": "Small dataset; Ethiopian domain; pseudo-zones not geospatially validated.",
            "notes": "Kept as the anchor dataset for the expanded Indonesian-label training set.",
        },
        {
            "dataset_id": "cand_kaggle_crop_recommendation",
            "dataset_name": "Crop Recommendation dataset (Kaggle-origin mirror)",
            "provider": "Kaggle / GitHub mirror",
            "source_type": "kaggle_benchmark_tabular",
            "region_scope": "Global/generalized benchmark",
            "original_url": "https://www.kaggle.com/datasets/irakozekelly/crop-recommendation-dataset",
            "download_url": "https://raw.githubusercontent.com/nileshiq/Crop-Recommendation/main/Crop_Recommendation.csv",
            "local_path": str(KAGGLE_MIRROR_PATH.relative_to(PROJECT_ROOT)),
            "classes_or_targets": "Rice, Maize, Banana, Coconut, Coffee, Mango, Orange, Papaya, Watermelon, MungBean and others",
            "features_summary": "N, P, K, temperature, humidity, pH, rainfall, crop label",
            "has_n": 1,
            "has_p": 1,
            "has_k": 1,
            "has_ph": 1,
            "has_temperature": 1,
            "has_rainfall": 1,
            "has_soil_moisture": 0,
            "is_tabular": 1,
            "target_label_clear": 1,
            "supervised_usable": 1,
            "compatible_with_zone_pipeline": 1,
            "selected_for_main_integration": 1,
            "integration_role": "selected_additional_source",
            "primary_risks": "Benchmark provenance rather than field-operational deployment data; no explicit spatial field zones.",
            "notes": "Selected. Converted into pseudo-zones without using labels during zone formation; humidity was excluded from final unified schema due semantic mismatch with active specific_humidity feature.",
        },
        {
            "dataset_id": "cand_mendeley_vynxnppr7j",
            "dataset_name": "Crop recommendation (integrated multi-source + CTGAN)",
            "provider": "Mendeley Data",
            "source_type": "mendeley_ctgan_augmented",
            "region_scope": "India (Tamil Nadu)",
            "original_url": "https://data.mendeley.com/datasets/vynxnppr7j/1",
            "download_url": "https://data.mendeley.com/public-files/datasets/vynxnppr7j/files/cdc23a7e-8306-48d0-be6d-b355aea63c92/file_downloaded",
            "local_path": str(MENDELEY_VYNX_PATH.relative_to(PROJECT_ROOT)),
            "classes_or_targets": "rice, maize, soyabean, groundnut, sugarcane, onion, chillies and many others",
            "features_summary": "N, P, K, soil_pH, temperature, relative_humidity, soil, season, water_source, crop duration, water required, crop label",
            "has_n": 1,
            "has_p": 1,
            "has_k": 1,
            "has_ph": 1,
            "has_temperature": 1,
            "has_rainfall": 0,
            "has_soil_moisture": 0,
            "is_tabular": 1,
            "target_label_clear": 1,
            "supervised_usable": 1,
            "compatible_with_zone_pipeline": 0,
            "selected_for_main_integration": 0,
            "integration_role": "experimental_only",
            "primary_risks": "Record explicitly states CTGAN-based synthetic expansion; rainfall not present; direct merge would require aggressive imputation and stronger assumptions.",
            "notes": "Rejected for main merge, but important as evidence that Indonesian-relevant labels do exist in public augmented datasets.",
        },
        {
            "dataset_id": "cand_zenodo_rice_fertility",
            "dataset_name": "Machine Learning Training Data (Rice)",
            "provider": "Zenodo",
            "source_type": "single_crop_fertility_classification",
            "region_scope": "Not clearly specified",
            "original_url": "https://zenodo.org/records/15307297",
            "download_url": "https://zenodo.org/records/15307297/files/Machine%20Learning-Training%20Data%20%28Rice%29.csv?download=1",
            "local_path": str(RICE_FERTILITY_ZENODO_PATH.relative_to(PROJECT_ROOT)),
            "classes_or_targets": "Fertility class only",
            "features_summary": "Nitrogen, Phosphorus, Potassium, fertility target",
            "has_n": 1,
            "has_p": 1,
            "has_k": 1,
            "has_ph": 0,
            "has_temperature": 0,
            "has_rainfall": 0,
            "has_soil_moisture": 0,
            "is_tabular": 1,
            "target_label_clear": 0,
            "supervised_usable": 0,
            "compatible_with_zone_pipeline": 0,
            "selected_for_main_integration": 0,
            "integration_role": "rejected",
            "primary_risks": "Target is fertility class, not crop recommendation.",
            "notes": "Useful only as crop-specific fertility auxiliary data for rice, not for adding a Padi class to multiclass crop recommendation.",
        },
        {
            "dataset_id": "cand_github_sugarcane",
            "dataset_name": "Sugarcane yield prediction dataset",
            "provider": "GitHub repository",
            "source_type": "yield_prediction_tabular",
            "region_scope": "Brazil",
            "original_url": "https://github.com/raulpoppiel/sugarcane-yield-prediction",
            "download_url": "https://raw.githubusercontent.com/raulpoppiel/sugarcane-yield-prediction/main/01_input_data/sugarcane_data.csv",
            "local_path": str(SUGARCANE_GITHUB_PATH.relative_to(PROJECT_ROOT)),
            "classes_or_targets": "Yield target only",
            "features_summary": "weather, remote sensing, management, variety; no consistent NPK/pH schema",
            "has_n": 0,
            "has_p": 0,
            "has_k": 0,
            "has_ph": 0,
            "has_temperature": 1,
            "has_rainfall": 1,
            "has_soil_moisture": 0,
            "is_tabular": 1,
            "target_label_clear": 0,
            "supervised_usable": 0,
            "compatible_with_zone_pipeline": 0,
            "selected_for_main_integration": 0,
            "integration_role": "rejected",
            "primary_risks": "Single-crop yield task, not multiclass crop recommendation; feature semantics differ strongly.",
            "notes": "Not appropriate for class expansion even though it is agronomically rich.",
        },
        {
            "dataset_id": "cand_zenodo_17_crop_points",
            "dataset_name": "Global training samples bundle for 17 crops",
            "provider": "Zenodo",
            "source_type": "geolocated_crop_points",
            "region_scope": "Global",
            "original_url": "https://zenodo.org/records/17666722",
            "download_url": "https://zenodo.org/api/records/17666722/files/Training_samples_for_17_crops.zip/content",
            "local_path": str(ZENODO_17_CROPS_PATH.relative_to(PROJECT_ROOT)),
            "classes_or_targets": "Barley, Cassava, Maize, Paddy rice, Peanut, Soybean, Sugarcane, Wheat and others",
            "features_summary": "species label + latitude/longitude only",
            "has_n": 0,
            "has_p": 0,
            "has_k": 0,
            "has_ph": 0,
            "has_temperature": 0,
            "has_rainfall": 0,
            "has_soil_moisture": 0,
            "is_tabular": 1,
            "target_label_clear": 1,
            "supervised_usable": 0,
            "compatible_with_zone_pipeline": 0,
            "selected_for_main_integration": 0,
            "integration_role": "future_spatial_join_candidate",
            "primary_risks": "Needs a full soil and climate spatial join pipeline before it can support supervised crop recommendation.",
            "notes": "Strong future expansion path for cassava, soybean, peanut, paddy rice, and sugarcane if global covariate extraction is implemented.",
        },
        {
            "dataset_id": "cand_agriculture_gist",
            "dataset_name": "Small agriculture gist dataset",
            "provider": "GitHub Gist",
            "source_type": "toy_tabular",
            "region_scope": "Unknown",
            "original_url": "https://gist.githubusercontent.com/ontipulikesava153/4dff8a942fb9983f526b6b042514cff0/raw/agriculture_dataset.csv",
            "download_url": "https://gist.githubusercontent.com/ontipulikesava153/4dff8a942fb9983f526b6b042514cff0/raw/agriculture_dataset.csv",
            "local_path": str(AGRICULTURE_GIST_PATH.relative_to(PROJECT_ROOT)),
            "classes_or_targets": "Crop type",
            "features_summary": "farm area, irrigation, fertilizer used, soil type, season, yield",
            "has_n": 0,
            "has_p": 0,
            "has_k": 0,
            "has_ph": 0,
            "has_temperature": 0,
            "has_rainfall": 0,
            "has_soil_moisture": 0,
            "is_tabular": 1,
            "target_label_clear": 1,
            "supervised_usable": 0,
            "compatible_with_zone_pipeline": 0,
            "selected_for_main_integration": 0,
            "integration_role": "rejected",
            "primary_risks": "Very small and missing core nutrient features.",
            "notes": "Rejected as a toy/example dataset.",
        },
        {
            "dataset_id": "cand_crop_recommend_gist",
            "dataset_name": "Small crop recommendation gist",
            "provider": "GitHub Gist",
            "source_type": "toy_tabular",
            "region_scope": "Unknown",
            "original_url": "https://gist.githubusercontent.com/Deeraj7/32fa6d434a14e34776b3d32d6a94a49e/raw/crop_recommend.csv",
            "download_url": "https://gist.githubusercontent.com/Deeraj7/32fa6d434a14e34776b3d32d6a94a49e/raw/crop_recommend.csv",
            "local_path": str(CROP_RECOMMEND_GIST_PATH.relative_to(PROJECT_ROOT)),
            "classes_or_targets": "Crop Type",
            "features_summary": "soil type, temperature, humidity, pH, rainfall, crop type",
            "has_n": 0,
            "has_p": 0,
            "has_k": 0,
            "has_ph": 1,
            "has_temperature": 1,
            "has_rainfall": 1,
            "has_soil_moisture": 0,
            "is_tabular": 1,
            "target_label_clear": 1,
            "supervised_usable": 0,
            "compatible_with_zone_pipeline": 0,
            "selected_for_main_integration": 0,
            "integration_role": "rejected",
            "primary_risks": "Very small and missing NPK; likely demonstrative/toy.",
            "notes": "Rejected because it would mostly add noise.",
        },
    ]

    screening_df = pd.DataFrame(records)
    profile_map = {
        "ref_active_zone": ACTIVE_ZONE_DATASET_ID_PATH,
        "cand_kaggle_crop_recommendation": KAGGLE_MIRROR_PATH,
        "cand_mendeley_vynxnppr7j": MENDELEY_VYNX_PATH,
        "cand_zenodo_rice_fertility": RICE_FERTILITY_ZENODO_PATH,
        "cand_github_sugarcane": SUGARCANE_GITHUB_PATH,
        "cand_zenodo_17_crop_points": ZENODO_17_CROPS_PATH,
        "cand_agriculture_gist": AGRICULTURE_GIST_PATH,
        "cand_crop_recommend_gist": CROP_RECOMMEND_GIST_PATH,
    }
    profile_rows = []
    for _, row in screening_df.iterrows():
        profile = local_csv_profile(profile_map[row["dataset_id"]])
        profile_rows.append(profile)
    profile_df = pd.DataFrame(profile_rows)
    screening_df = pd.concat([screening_df, profile_df], axis=1)
    screening_df.to_csv(SCREENING_PATH, index=False)
    return screening_df


def translate_label(label: str) -> str:
    return LABEL_MAPPING_EXPANDED_ID.get(label, label)


def write_decision_doc(
    screening_df: pd.DataFrame,
    kaggle_diagnostics: dict[str, Any],
    final_distribution: dict[str, int],
) -> None:
    selected = screening_df.loc[screening_df["selected_for_main_integration"] == 1, "dataset_name"].tolist()
    experimental = screening_df.loc[screening_df["integration_role"] == "experimental_only", "dataset_name"].tolist()
    future = screening_df.loc[screening_df["integration_role"] == "future_spatial_join_candidate", "dataset_name"].tolist()
    decision_text = f"""# Dataset Expansion Decision

## Selected Main Integration Sources

{chr(10).join(f"- {name}" for name in selected)}

## Why These Were Selected

1. **Current active zone dataset** remains the anchor because it is the only dataset already aligned with the current zone-based training pipeline.
2. **Kaggle-origin crop recommendation benchmark** was selected because it overlaps on the core features `N`, `P`, `K`, `pH`, `temperature`, and `rainfall`, and it adds multiple crops that are genuinely common in Indonesia, especially `Rice`.
3. The Kaggle dataset was not merged row-to-row. It was first converted into pseudo-zones using climate-context grouping and soil clustering without using target labels during zone formation.

## Selected Additional Classes

Kelas baru yang benar-benar ditambahkan ke dataset final:

- Padi
- Pisang
- Kelapa
- Kopi
- Mangga
- Jeruk
- Pepaya
- Semangka
- Kacang Hijau

`Jagung` sudah ada sebelumnya dan mendapat tambahan support dari source baru.

## Main Rejections

- **Mendeley vynxnppr7j**: sangat kaya label Indonesia-relevant (`soyabean`, `groundnut`, `sugarcane`, `onion`, `chillies`), tetapi record-nya eksplisit memakai CTGAN dan tidak punya rainfall. Saya simpan sebagai kandidat eksperimen, bukan merge utama.
- **Zenodo rice fertility**: target-nya `fertility`, bukan crop class.
- **GitHub sugarcane yield**: target-nya yield untuk satu crop, bukan multiclass recommendation.
- **Zenodo 17-crop training samples**: sangat menarik untuk `cassava`, `soybean`, `peanut`, `sugarcane`, tetapi masih perlu join spasial soil + climate sebelum valid untuk supervised learning tabular.
- **Gist kecil**: ditolak karena toy-scale dan tidak punya fitur inti.

## Kaggle Contribution

Kaggle berhasil memberi dataset yang **relevan dan usable** untuk ekspansi kelas. Dataset itulah yang menjadi sumber tambahan utama pada tahap ini.

## Pseudo-Zone Diagnostics for Kaggle Source

- Source points retained for selected crops: {kaggle_diagnostics['source_points']}
- Candidate pseudo-zones: {kaggle_diagnostics['candidate_zone_count']}
- Final kept pseudo-zones: {kaggle_diagnostics['kept_zone_count']}
- Final class distribution from Kaggle pseudo-zones: {kaggle_diagnostics['kept_class_distribution']}

## Final Class Distribution After Main Integration

{final_distribution}
"""
    DECISION_PATH.write_text(decision_text, encoding="utf-8")


def write_integration_strategy_doc(
    final_distribution: dict[str, int],
    feature_columns: list[str],
    source_distribution: dict[str, int],
) -> None:
    strategy_text = f"""# Dataset Integration Strategy

## Integration Outcome

Pendekatan yang dipakai adalah **harmonisasi schema + concat zone datasets**, bukan merge row-level antar sumber.

## Why Direct Merge Was Rejected

- Dataset zona aktif sudah berada pada level zona, sedangkan source tambahan utama berada pada level titik.
- Tidak ada primary key, field boundary, atau koordinat yang bisa dipakai untuk merge baris-ke-baris dengan dataset aktif.
- Karena itu, source tambahan diubah dulu menjadi pseudo-zone yang konsisten secara metodologis.

## Main Pipeline

1. Ambil dataset zona aktif sebagai anchor.
2. Ambil dataset crop recommendation bergaya Kaggle pada level titik.
3. Bentuk `base_context_id` dari bin kuantil `temperature`, `rainfall`, dan `humidity`.
4. Di dalam setiap konteks, cluster titik berdasarkan `ph`, `nitrogen`, `phosphorus`, dan `potassium`.
5. Bentuk `zone_id`, lalu hitung agregat zona.
6. Pertahankan hanya zona dengan:
   - minimal 8 titik
   - dominant label ratio minimal 0.60
   - minimal 3 zona per kelas
7. Harmonisasi ke schema zona bersama.
8. Concat dengan dataset zona aktif.

## Unified Schema

Fitur inti yang dipertahankan pada dataset final:

{chr(10).join(f"- {column}" for column in feature_columns)}

## Feature Compatibility Decisions

- `humidity` dari Kaggle **tidak** dibawa ke schema final karena fitur aktif yang serupa adalah `specific_humidity_mean`, dan semantik keduanya tidak aman untuk disamakan langsung.
- `rainfall` dipertahankan karena tersedia pada dataset aktif dan Kaggle.
- `zinc`, `sulfur`, `soil_color`, `soil_moisture_surface`, dan fitur lain yang tidak overlap antar sumber tidak dipakai pada schema final utama.

## Source Composition

{source_distribution}

## Consequence

Dataset final lebih sempit pada sisi fitur dibanding dataset zona aktif asli, tetapi lebih kuat untuk ekspansi label karena hanya mempertahankan fitur yang benar-benar kompatibel secara lintas sumber.
"""
    INTEGRATION_STRATEGY_PATH.write_text(strategy_text, encoding="utf-8")


def write_retraining_readiness_doc(final_df: pd.DataFrame, metadata: dict[str, Any]) -> None:
    class_distribution = final_df[ZONE_TARGET_COLUMN].value_counts()
    risk_lines = "\n".join(f"- {item}" for item in metadata["quality_risks"])
    text = f"""# Retraining Readiness (Expanded)

## Dataset Size

- Total zones: {final_df.shape[0]}
- Total classes: {class_distribution.shape[0]}
- Class distribution: {class_distribution.to_dict()}

## Readiness Assessment

- Supervised learning framing: **layak**, sebagai multiclass classification pada level zona.
- Main metric recommendation: **macro F1**, karena distribusi kelas masih tidak seimbang dan jumlah zona per kelas kecil.
- Split recommendation: **group-aware holdout + group CV** memakai `base_context_id`.

## Data Quality Notes

- Fitur final dibatasi pada overlap antar sumber, sehingga completeness tinggi pada fitur yang dipakai untuk training.
- Kelas tambahan dari Kaggle bukan zona geospasial nyata; mereka adalah pseudo-zones berbasis climate-context + soil clustering.
- Kelas baru dari dataset CTGAN Tamil Nadu tidak dimasukkan ke merge utama karena risiko domain dan semantic mismatch masih terlalu besar.

## Recommendation

Retraining **boleh dilakukan** untuk baseline ekspansi tahap 2, tetapi hasilnya harus diposisikan sebagai:

1. baseline eksploratif untuk ekspansi kelas Indonesia-relevant
2. belum setara dengan model produksi yang telah divalidasi pada zona lapangan Indonesia

## Main Risks

{risk_lines}
"""
    READINESS_PATH.write_text(text, encoding="utf-8")


def build_metadata(
    final_minimal_df: pd.DataFrame,
    final_extended_df: pd.DataFrame,
    kaggle_diagnostics: dict[str, Any],
) -> dict[str, Any]:
    metadata = {
        "created_at_utc": pd.Timestamp.now("UTC").isoformat(),
        "dataset_name": "zone_dataset_expanded_id",
        "source_datasets_used": [
            str(ACTIVE_ZONE_DATASET_ID_PATH.relative_to(PROJECT_ROOT)),
            str(KAGGLE_MIRROR_PATH.relative_to(PROJECT_ROOT)),
        ],
        "source_datasets_considered_but_not_merged": [
            str(MENDELEY_VYNX_PATH.relative_to(PROJECT_ROOT)),
            str(RICE_FERTILITY_ZENODO_PATH.relative_to(PROJECT_ROOT)),
            str(SUGARCANE_GITHUB_PATH.relative_to(PROJECT_ROOT)),
            str(ZENODO_17_CROPS_PATH.relative_to(PROJECT_ROOT)),
        ],
        "target_column": ZONE_TARGET_COLUMN,
        "number_of_zones": int(final_extended_df.shape[0]),
        "number_of_classes": int(final_extended_df[ZONE_TARGET_COLUMN].nunique()),
        "class_distribution": final_extended_df[ZONE_TARGET_COLUMN].value_counts().to_dict(),
        "minimal_dataset_columns": final_minimal_df.columns.tolist(),
        "extended_dataset_columns": final_extended_df.columns.tolist(),
        "feature_families": FINAL_NUMERIC_FAMILIES,
        "selected_label_mapping": LABEL_MAPPING_EXPANDED_ID,
        "integration_strategy": {
            "type": "schema_harmonization_plus_zone_concat",
            "selected_additional_dataset": str(KAGGLE_MIRROR_PATH.relative_to(PROJECT_ROOT)),
            "external_zone_adaptation": "quantile-binned climate contexts + within-context KMeans clustering over pH/N/P/K without using labels during zone formation",
            "kaggle_pseudo_zone_diagnostics": kaggle_diagnostics,
        },
        "cleaning_notes": [
            "The final expanded dataset keeps only overlapping feature families between the active zone dataset and the selected Kaggle benchmark.",
            "Relative humidity was excluded from the final schema because it is not semantically equivalent to the active dataset's specific humidity feature.",
            "Only Indonesia-relevant crops from the Kaggle source were considered for the main merge.",
            "The final target labels are stored in Bahasa Indonesia.",
        ],
        "quality_risks": [
            "The active anchor data is still Ethiopian and pseudo-zone based, not Indonesia field data.",
            "The Kaggle source is a benchmark dataset and not a geospatially explicit zone dataset.",
            "The merged dataset now mixes native pseudo-zones and externally constructed pseudo-zones.",
            "Several added classes still have only 3-6 zones, so per-class robustness remains limited.",
            "Requested crops such as Kedelai, Kacang Tanah, Tebu, Cabai, and Bawang Merah were found in a CTGAN-augmented source, but were intentionally excluded from the main merge because the semantic risk was too high.",
        ],
        "source_distribution": final_extended_df["source_dataset"].value_counts().to_dict(),
    }
    EXPANDED_METADATA_PATH.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return metadata


def build_feature_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    metadata_columns = set(FINAL_EXTENDED_BASE_COLUMNS)
    for column in frame.columns:
        series = frame[column]
        row: dict[str, Any] = {
            "feature_name": column,
            "dtype": str(series.dtype),
            "non_null_count": int(series.notna().sum()),
            "missing_ratio": float(series.isna().mean()),
            "unique_count": int(series.nunique(dropna=True)),
            "is_target": int(column == ZONE_TARGET_COLUMN),
            "is_metadata": int(column in metadata_columns),
            "aggregation_family": "base",
        }
        for suffix in ["_mean", "_std", "_min", "_max", "_median", "_count", "_range", "_cv", "_missing_ratio"]:
            if column.endswith(suffix):
                row["aggregation_family"] = suffix.strip("_")
                break
        if pd.api.types.is_numeric_dtype(series):
            row["mean"] = float(series.mean()) if series.notna().any() else None
            row["std"] = float(series.std()) if series.notna().any() else None
            row["min"] = float(series.min()) if series.notna().any() else None
            row["max"] = float(series.max()) if series.notna().any() else None
            row["top_value"] = None
            row["top_ratio"] = None
        else:
            counts = series.value_counts(dropna=True, normalize=True)
            row["mean"] = None
            row["std"] = None
            row["min"] = None
            row["max"] = None
            row["top_value"] = counts.index[0] if not counts.empty else None
            row["top_ratio"] = float(counts.iloc[0]) if not counts.empty else None
        rows.append(row)
    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(EXPANDED_FEATURE_SUMMARY_PATH, index=False)
    return summary_df


def main() -> dict[str, Any]:
    ensure_project_dirs()
    LABEL_MAPPING_EXPANDED_PATH.write_text(
        json.dumps(LABEL_MAPPING_EXPANDED_ID, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    screening_df = build_screening_frame()
    active_minimal_df, active_extended_df = load_active_zone_standardized()
    kaggle_minimal_df, kaggle_extended_df, kaggle_diagnostics = build_kaggle_zone_frames()

    merged_minimal_df = pd.concat([active_minimal_df, kaggle_minimal_df], ignore_index=True)
    merged_extended_df = pd.concat([active_extended_df, kaggle_extended_df], ignore_index=True)

    merged_minimal_df[ZONE_TARGET_COLUMN] = merged_minimal_df[ZONE_TARGET_COLUMN].map(translate_label)
    merged_extended_df[ZONE_TARGET_COLUMN] = merged_extended_df[ZONE_TARGET_COLUMN].map(translate_label)

    class_counts = merged_extended_df[ZONE_TARGET_COLUMN].value_counts()
    valid_classes = class_counts[class_counts >= 3].index.tolist()
    merged_minimal_df = merged_minimal_df.loc[merged_minimal_df[ZONE_TARGET_COLUMN].isin(valid_classes)].reset_index(drop=True)
    merged_extended_df = merged_extended_df.loc[merged_extended_df[ZONE_TARGET_COLUMN].isin(valid_classes)].reset_index(drop=True)

    merged_minimal_df.to_csv(EXPANDED_DATASET_MINIMAL_PATH, index=False)
    merged_extended_df.to_csv(EXPANDED_DATASET_PATH, index=False)

    final_distribution = merged_extended_df[ZONE_TARGET_COLUMN].value_counts().to_dict()
    write_decision_doc(screening_df, kaggle_diagnostics, final_distribution)
    write_integration_strategy_doc(
        final_distribution=final_distribution,
        feature_columns=[column for column in FINAL_EXTENDED_COLUMNS if column != ZONE_TARGET_COLUMN],
        source_distribution=merged_extended_df["source_dataset"].value_counts().to_dict(),
    )
    metadata = build_metadata(merged_minimal_df, merged_extended_df, kaggle_diagnostics)
    build_feature_summary(merged_extended_df)
    write_retraining_readiness_doc(merged_extended_df, metadata)

    summary = {
        "screening_path": str(SCREENING_PATH.relative_to(PROJECT_ROOT)),
        "expanded_dataset_path": str(EXPANDED_DATASET_PATH.relative_to(PROJECT_ROOT)),
        "expanded_dataset_minimal_path": str(EXPANDED_DATASET_MINIMAL_PATH.relative_to(PROJECT_ROOT)),
        "expanded_metadata_path": str(EXPANDED_METADATA_PATH.relative_to(PROJECT_ROOT)),
        "final_zone_count": int(merged_extended_df.shape[0]),
        "final_class_distribution": final_distribution,
        "selected_additional_source": str(KAGGLE_MIRROR_PATH.relative_to(PROJECT_ROOT)),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    main()
