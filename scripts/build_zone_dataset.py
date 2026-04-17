from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import (
    PRIMARY_DATASET_PATH,
    PROJECT_ROOT,
    RANDOM_STATE,
    TARGET_COLUMN,
    ZONE_DATASET_EXTENDED_PATH,
    ZONE_DATASET_MINIMAL_PATH,
    ZONE_DATASET_PATH,
    ZONE_FEATURE_SUMMARY_PATH,
    ZONE_METADATA_PATH,
    ZONE_MODELING_STRATEGY_PATH,
    ZONE_TARGET_COLUMN,
    ensure_project_dirs,
)
from scripts.zone_utils import normalize_soil_color, normalize_target_label


WEATHER_SIGNATURE_COLUMNS = [
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
]

POINT_RENAME_MAP = {
    "Soilcolor": "soil_color",
    "Ph": "ph",
    "K": "potassium",
    "P": "phosphorus",
    "N": "nitrogen",
    "Zn": "zinc",
    "S": "sulfur",
    "WD10M": "wind_speed_10m",
    "GWETTOP": "soil_moisture_surface",
    "CLOUD_AMT": "cloud_amount",
    "WS2M_RANGE": "wind_speed_range_2m",
    "PS": "surface_pressure",
    "label": TARGET_COLUMN,
}

POINT_CLUSTER_FEATURES = ["ph", "potassium", "phosphorus", "nitrogen", "zinc", "sulfur"]
POINT_NUMERIC_FEATURES = [
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
POINT_CATEGORICAL_FEATURES = ["soil_color"]

ZONE_BUILDER_PARAMS = {
    "target_zone_size": 25,
    "min_samples_per_zone": 8,
    "min_zone_label_dominance_ratio": 0.60,
    "min_zones_per_class": 3,
    "cluster_features": POINT_CLUSTER_FEATURES,
}


def normalize_point_dataframe() -> pd.DataFrame:
    raw = pd.read_csv(PRIMARY_DATASET_PATH).copy()
    raw["base_context_id"] = raw.groupby(WEATHER_SIGNATURE_COLUMNS, dropna=False).ngroup() + 1

    point_df = raw.rename(columns=POINT_RENAME_MAP).copy()
    point_df["soil_color"] = point_df["soil_color"].map(normalize_soil_color)
    point_df[TARGET_COLUMN] = point_df[TARGET_COLUMN].map(normalize_target_label)
    point_df["source_dataset"] = PRIMARY_DATASET_PATH.stem
    point_df["point_id"] = [f"point_{index + 1:05d}" for index in range(len(point_df))]

    humidity_cols = ["QV2M-W", "QV2M-Sp", "QV2M-Su", "QV2M-Au"]
    temperature_max_cols = ["T2M_MAX-W", "T2M_MAX-Sp", "T2M_MAX-Su", "T2M_MAX-Au"]
    temperature_min_cols = ["T2M_MIN-W", "T2M_MIN-Sp", "T2M_MIN-Su", "T2M_MIN-Au"]
    rainfall_cols = ["PRECTOTCORR-W", "PRECTOTCORR-Sp", "PRECTOTCORR-Su", "PRECTOTCORR-Au"]

    point_df["specific_humidity_mean"] = point_df[humidity_cols].mean(axis=1)
    seasonal_means = pd.concat(
        [(point_df[max_col] + point_df[min_col]) / 2 for max_col, min_col in zip(temperature_max_cols, temperature_min_cols)],
        axis=1,
    )
    point_df["temperature_mean"] = seasonal_means.mean(axis=1)
    point_df["temperature_seasonal_range"] = point_df[temperature_max_cols].max(axis=1) - point_df[temperature_min_cols].min(axis=1)
    point_df["rainfall_mean"] = point_df[rainfall_cols].mean(axis=1)
    point_df["rainfall_total_proxy"] = point_df[rainfall_cols].sum(axis=1)

    numeric_cols = set(POINT_NUMERIC_FEATURES) | {
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
    }
    for column in numeric_cols:
        if column in point_df.columns:
            point_df[column] = pd.to_numeric(point_df[column], errors="coerce")

    point_df = point_df.loc[point_df[TARGET_COLUMN] != "Fallow"].copy()
    point_df = point_df.reset_index(drop=True)
    return point_df


def assign_zone_ids(point_df: pd.DataFrame, params: dict[str, Any] | None = None) -> pd.DataFrame:
    params = params or ZONE_BUILDER_PARAMS
    target_zone_size = int(params["target_zone_size"])
    cluster_features = list(params["cluster_features"])

    zone_ids = pd.Series(index=point_df.index, dtype="string")
    context_rows: list[dict[str, Any]] = []

    for base_context_id, context_frame in point_df.groupby("base_context_id", sort=True):
        sample_count = int(context_frame.shape[0])
        cluster_count = max(1, round(sample_count / target_zone_size))
        cluster_count = min(cluster_count, max(1, sample_count // 5)) if sample_count >= 10 else 1

        feature_frame = context_frame[cluster_features].copy()
        feature_frame = feature_frame.fillna(feature_frame.median(numeric_only=True))
        scaled = StandardScaler().fit_transform(feature_frame)
        labels = (
            np.zeros(sample_count, dtype=int)
            if cluster_count == 1
            else KMeans(n_clusters=cluster_count, random_state=RANDOM_STATE, n_init=10).fit_predict(scaled)
        )

        for local_index, cluster_label in zip(context_frame.index, labels):
            zone_ids.loc[local_index] = f"zone_{int(base_context_id):02d}_{int(cluster_label):02d}"

        context_rows.append(
            {
                "base_context_id": int(base_context_id),
                "context_sample_count": sample_count,
                "context_cluster_count": int(cluster_count),
            }
        )

    enriched = point_df.copy()
    enriched["zone_id"] = zone_ids
    context_summary = pd.DataFrame(context_rows)
    enriched = enriched.merge(context_summary, on="base_context_id", how="left")
    return enriched


def dominant_value(series: pd.Series) -> Any:
    modes = series.mode(dropna=True)
    if not modes.empty:
        return modes.iloc[0]
    return series.dropna().iloc[0] if series.dropna().shape[0] else np.nan


def build_zone_statistics(point_df: pd.DataFrame, params: dict[str, Any] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    params = params or ZONE_BUILDER_PARAMS
    min_samples_per_zone = int(params["min_samples_per_zone"])
    min_dominance_ratio = float(params["min_zone_label_dominance_ratio"])
    min_zones_per_class = int(params["min_zones_per_class"])

    zone_stats = point_df.groupby("zone_id").agg(
        base_context_id=("base_context_id", "first"),
        source_dataset=("source_dataset", "first"),
        sample_count=("point_id", "size"),
        context_sample_count=("context_sample_count", "first"),
        context_cluster_count=("context_cluster_count", "first"),
        label_nunique=(TARGET_COLUMN, "nunique"),
    )
    zone_stats[ZONE_TARGET_COLUMN] = point_df.groupby("zone_id")[TARGET_COLUMN].agg(dominant_value)
    zone_stats["zone_label_dominance_ratio"] = (
        point_df.groupby("zone_id")[TARGET_COLUMN].value_counts(normalize=True).groupby(level=0).max()
    )
    zone_stats["zone_quality_flag"] = np.where(
        (zone_stats["sample_count"] >= min_samples_per_zone)
        & (zone_stats["zone_label_dominance_ratio"] >= min_dominance_ratio),
        "kept",
        "filtered_ambiguous_or_small",
    )
    zone_stats["sample_count_risk_flag"] = np.where(zone_stats["sample_count"] < min_samples_per_zone, "low_support", "ok")

    kept_zone_stats = zone_stats.loc[zone_stats["zone_quality_flag"] == "kept"].copy()
    class_counts = kept_zone_stats[ZONE_TARGET_COLUMN].value_counts()
    valid_classes = class_counts[class_counts >= min_zones_per_class].index.tolist()
    kept_zone_stats["class_support_flag"] = np.where(
        kept_zone_stats[ZONE_TARGET_COLUMN].isin(valid_classes),
        "kept",
        "filtered_low_class_support",
    )
    kept_zone_stats = kept_zone_stats.loc[kept_zone_stats["class_support_flag"] == "kept"].copy()
    return zone_stats.reset_index(), kept_zone_stats.reset_index()


def aggregate_numeric_features(point_df: pd.DataFrame, group_key: str, columns: list[str]) -> pd.DataFrame:
    frames = []
    grouped = point_df.groupby(group_key)
    for column in columns:
        series_group = grouped[column]
        frame = pd.DataFrame(
            {
                f"{column}_mean": series_group.mean(),
                f"{column}_std": series_group.std().fillna(0),
                f"{column}_min": series_group.min(),
                f"{column}_max": series_group.max(),
                f"{column}_median": series_group.median(),
                f"{column}_count": series_group.count(),
                f"{column}_missing_ratio": series_group.apply(lambda values: float(values.isna().mean())),
            }
        )
        frame[f"{column}_range"] = frame[f"{column}_max"] - frame[f"{column}_min"]
        frame[f"{column}_cv"] = np.where(
            frame[f"{column}_mean"].abs() > 1e-9,
            frame[f"{column}_std"] / frame[f"{column}_mean"].abs(),
            0.0,
        )
        frames.append(frame)
    result = frames[0]
    for frame in frames[1:]:
        result = result.join(frame, how="left")
    return result


def aggregate_categorical_features(point_df: pd.DataFrame, group_key: str, columns: list[str]) -> pd.DataFrame:
    grouped = point_df.groupby(group_key)
    result = pd.DataFrame(index=grouped.size().index)
    for column in columns:
        result[f"{column}_mode"] = grouped[column].agg(dominant_value)
        result[f"{column}_nunique"] = grouped[column].nunique(dropna=True)
        dominant_ratio = grouped[column].value_counts(normalize=True).groupby(level=0).max()
        result[f"{column}_dominant_ratio"] = dominant_ratio.reindex(result.index).fillna(0)
        result[f"{column}_missing_ratio"] = grouped[column].apply(lambda values: float(values.isna().mean()))
    return result


def build_zone_datasets(point_df: pd.DataFrame, kept_zone_stats: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    kept_zone_ids = kept_zone_stats["zone_id"].tolist()
    filtered_points = point_df.loc[point_df["zone_id"].isin(kept_zone_ids)].copy()

    base_columns = [
        "zone_id",
        "base_context_id",
        "source_dataset",
        "sample_count",
        "context_sample_count",
        "context_cluster_count",
        "label_nunique",
        "zone_label_dominance_ratio",
        "sample_count_risk_flag",
        ZONE_TARGET_COLUMN,
    ]
    zone_df = kept_zone_stats[base_columns].copy().set_index("zone_id")

    numeric_aggregates = aggregate_numeric_features(filtered_points, "zone_id", POINT_NUMERIC_FEATURES)
    categorical_aggregates = aggregate_categorical_features(filtered_points, "zone_id", POINT_CATEGORICAL_FEATURES)
    zone_df = zone_df.join(numeric_aggregates, how="left").join(categorical_aggregates, how="left")
    zone_df = zone_df.reset_index()

    minimal_columns = [
        "zone_id",
        "base_context_id",
        "source_dataset",
        "sample_count",
        "context_sample_count",
        "context_cluster_count",
        "sample_count_risk_flag",
        "soil_color_mode",
        "soil_color_dominant_ratio",
        *[f"{column}_mean" for column in POINT_NUMERIC_FEATURES],
        ZONE_TARGET_COLUMN,
    ]

    extended_columns = [
        "zone_id",
        "base_context_id",
        "source_dataset",
        "sample_count",
        "context_sample_count",
        "context_cluster_count",
        "label_nunique",
        "zone_label_dominance_ratio",
        "sample_count_risk_flag",
        "soil_color_mode",
        "soil_color_nunique",
        "soil_color_dominant_ratio",
        "soil_color_missing_ratio",
    ]
    for column in POINT_NUMERIC_FEATURES:
        extended_columns.extend(
            [
                f"{column}_mean",
                f"{column}_std",
                f"{column}_min",
                f"{column}_max",
                f"{column}_median",
                f"{column}_count",
                f"{column}_range",
                f"{column}_cv",
                f"{column}_missing_ratio",
            ]
        )
    extended_columns.append(ZONE_TARGET_COLUMN)
    return zone_df[minimal_columns].copy(), zone_df[extended_columns].copy()


def build_zone_feature_summary(zone_extended_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for column in zone_extended_df.columns:
        series = zone_extended_df[column]
        row: dict[str, Any] = {
            "feature_name": column,
            "dtype": str(series.dtype),
            "non_null_count": int(series.notna().sum()),
            "missing_ratio": float(series.isna().mean()),
            "unique_count": int(series.nunique(dropna=True)),
            "is_target": int(column == ZONE_TARGET_COLUMN),
            "is_metadata": int(column in {"zone_id", "base_context_id", "source_dataset", "sample_count", "context_sample_count", "context_cluster_count", "sample_count_risk_flag"}),
            "aggregation_family": "base",
        }
        for suffix in ["_mean", "_std", "_min", "_max", "_median", "_count", "_range", "_cv", "_missing_ratio", "_mode", "_nunique", "_dominant_ratio"]:
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
    summary_df.to_csv(ZONE_FEATURE_SUMMARY_PATH, index=False)
    return summary_df


def build_zone_metadata(
    point_df: pd.DataFrame,
    all_zone_stats: pd.DataFrame,
    kept_zone_stats: pd.DataFrame,
    zone_minimal_df: pd.DataFrame,
    zone_extended_df: pd.DataFrame,
) -> dict[str, Any]:
    sample_distribution = kept_zone_stats["sample_count"].describe().to_dict()
    retained_classes = kept_zone_stats[ZONE_TARGET_COLUMN].value_counts().index.tolist()
    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_dataset": str(PRIMARY_DATASET_PATH.relative_to(PROJECT_ROOT)),
        "source_is_point_based": True,
        "zone_available_in_raw_data": False,
        "zone_construction_required": True,
        "zone_strategy_type": "fallback_pseudo_zone_from_shared_weather_context_plus_soil_clustering",
        "zone_builder_params": ZONE_BUILDER_PARAMS,
        "target_column": ZONE_TARGET_COLUMN,
        "number_of_raw_points_after_basic_cleaning": int(point_df.shape[0]),
        "number_of_candidate_zones": int(all_zone_stats.shape[0]),
        "number_of_final_zones": int(kept_zone_stats.shape[0]),
        "average_points_per_zone": float(kept_zone_stats["sample_count"].mean()),
        "points_per_zone_distribution": {key: float(value) for key, value in sample_distribution.items()},
        "class_distribution": kept_zone_stats[ZONE_TARGET_COLUMN].value_counts().to_dict(),
        "minimal_dataset_columns": zone_minimal_df.columns.tolist(),
        "extended_dataset_columns": zone_extended_df.columns.tolist(),
        "cleaning_notes": [
            "Raw point rows were normalized to snake_case-style semantic names where applicable.",
            "The non-crop class `Fallow` was removed before zone construction.",
            "Base agro-climatic contexts were inferred from exact repeated weather signatures because no explicit coordinates or field IDs were present.",
            "Within each context, KMeans clustering on soil chemistry features formed pseudo-zones without using target labels.",
            "Only zones with at least 8 points and at least 0.60 dominant-label ratio were retained.",
            "Classes represented by fewer than 3 zones were filtered out to avoid extremely fragile supervised learning targets.",
        ],
        "quality_risks": [
            "The source dataset does not contain latitude/longitude, field_id, sampling time, or explicit zone_id.",
            "Constructed zones are pseudo-zones in feature/context space, not verified cadastral or geospatial zones.",
            "Weather variability inside a constructed zone is almost zero because base contexts were defined from repeated weather signatures.",
            "Zone labels are derived from dominant point labels and therefore inherit label noise from mixed zones.",
            f"The final zone dataset is concentrated in the retained classes: {', '.join(retained_classes)}.",
        ],
    }
    ZONE_METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def write_zone_strategy_md(
    point_df: pd.DataFrame,
    all_zone_stats: pd.DataFrame,
    kept_zone_stats: pd.DataFrame,
    metadata: dict[str, Any],
) -> None:
    source_columns = point_df.columns.tolist()
    strategy = f"""# Zone Modeling Strategy

## Dataset Audit

- Raw training source: `datasets/csv/{PRIMARY_DATASET_PATH.name}`
- Initial data structure: point-based sampling records.
- Explicit `zone_id` in raw data: no
- Explicit `field_id` in raw data: no
- Latitude/longitude: no
- X/Y coordinates: no
- Sample ID: no
- Sampling time: no
- Depth: no
- Target label present: yes (`{TARGET_COLUMN}`)

Available high-signal columns include soil chemistry (`Ph`, `N`, `P`, `K`, `Zn`, `S`), soil color, and repeated weather signatures.

## Decision

1. Zona belum tersedia secara eksplisit di dataset mentah.
2. Zona perlu dibentuk agar pipeline tidak lagi memperlakukan satu titik sebagai representasi seluruh lahan.
3. Karena koordinat dan field boundary tidak tersedia, zona dibentuk dengan strategi fallback yang masih defensible:
   - langkah 1: bentuk `base_context_id` dari kombinasi signature cuaca yang identik
   - langkah 2: di dalam setiap `base_context_id`, cluster titik berdasarkan fitur tanah `ph`, `nitrogen`, `phosphorus`, `potassium`, `zinc`, `sulfur`
   - langkah 3: setiap cluster menjadi satu `zone_id`
4. Target zona cocok untuk framing klasifikasi multiclass setelah disaring berdasarkan dominasi label titik.

## Zone Construction Rules

- Jumlah base context terdeteksi: {point_df['base_context_id'].nunique()}
- Jumlah kandidat zona hasil clustering: {all_zone_stats.shape[0]}
- Jumlah zona final yang lolos filtering: {kept_zone_stats.shape[0]}
- Target zone size: {ZONE_BUILDER_PARAMS['target_zone_size']} titik
- Minimum titik per zona: {ZONE_BUILDER_PARAMS['min_samples_per_zone']}
- Minimum dominant label ratio: {ZONE_BUILDER_PARAMS['min_zone_label_dominance_ratio']:.2f}
- Minimum jumlah zona per kelas target: {ZONE_BUILDER_PARAMS['min_zones_per_class']}

## Zone Label Rule

- Label zona = label titik dominan di dalam zona.
- Zona ambigu tidak dipakai untuk training bila dominant label ratio < {ZONE_BUILDER_PARAMS['min_zone_label_dominance_ratio']:.2f}.
- Kelas yang hanya muncul pada sangat sedikit zona juga dibuang agar evaluasi supervised tetap defensible.

## Why This Is A Fallback

- Zona yang dibentuk bukan zona geospasial resmi karena dataset mentah tidak punya koordinat atau batas lahan.
- Namun, pembentukan zona ini tetap lebih realistis daripada memakai satu titik sebagai satu unit rekomendasi, karena beberapa titik dengan konteks agroklimat yang sama digabung dan variasi internal tanah dipertahankan.

## Risks

"""
    strategy += "\n".join(f"- {risk}" for risk in metadata["quality_risks"])
    strategy += "\n\n## Source Columns\n\n"
    strategy += "- " + "\n- ".join(source_columns)
    ZONE_MODELING_STRATEGY_PATH.write_text(strategy, encoding="utf-8")


def prepare_zone_datasets() -> dict[str, Any]:
    ensure_project_dirs()
    point_df = normalize_point_dataframe()
    point_df = assign_zone_ids(point_df)
    all_zone_stats, kept_zone_stats = build_zone_statistics(point_df)

    retained_zone_ids = set(kept_zone_stats["zone_id"])
    retained_classes = set(kept_zone_stats[ZONE_TARGET_COLUMN])
    filtered_points = point_df.loc[
        point_df["zone_id"].isin(retained_zone_ids) & point_df[TARGET_COLUMN].isin(retained_classes)
    ].copy()
    kept_zone_stats = kept_zone_stats.loc[kept_zone_stats["zone_id"].isin(filtered_points["zone_id"].unique())].copy()

    zone_minimal_df, zone_extended_df = build_zone_datasets(filtered_points, kept_zone_stats)
    zone_extended_df.to_csv(ZONE_DATASET_PATH, index=False)
    zone_minimal_df.to_csv(ZONE_DATASET_MINIMAL_PATH, index=False)
    zone_extended_df.to_csv(ZONE_DATASET_EXTENDED_PATH, index=False)
    build_zone_feature_summary(zone_extended_df)
    metadata = build_zone_metadata(point_df, all_zone_stats, kept_zone_stats, zone_minimal_df, zone_extended_df)
    write_zone_strategy_md(point_df, all_zone_stats, kept_zone_stats, metadata)

    return {
        "point_df": point_df,
        "filtered_point_df": filtered_points,
        "all_zone_stats": all_zone_stats,
        "kept_zone_stats": kept_zone_stats,
        "zone_minimal_df": zone_minimal_df,
        "zone_extended_df": zone_extended_df,
        "metadata": metadata,
    }


if __name__ == "__main__":
    bundle = prepare_zone_datasets()
    summary = {
        "zone_dataset_path": str(ZONE_DATASET_PATH.relative_to(PROJECT_ROOT)),
        "zone_dataset_minimal_path": str(ZONE_DATASET_MINIMAL_PATH.relative_to(PROJECT_ROOT)),
        "zone_dataset_extended_path": str(ZONE_DATASET_EXTENDED_PATH.relative_to(PROJECT_ROOT)),
        "zone_metadata_path": str(ZONE_METADATA_PATH.relative_to(PROJECT_ROOT)),
        "zone_modeling_strategy_path": str(ZONE_MODELING_STRATEGY_PATH.relative_to(PROJECT_ROOT)),
        "zone_feature_summary_path": str(ZONE_FEATURE_SUMMARY_PATH.relative_to(PROJECT_ROOT)),
        "n_points_after_basic_cleaning": int(bundle["point_df"].shape[0]),
        "n_points_in_retained_zones": int(bundle["filtered_point_df"].shape[0]),
        "n_final_zones": int(bundle["zone_extended_df"].shape[0]),
        "zone_class_distribution": bundle["zone_extended_df"][ZONE_TARGET_COLUMN].value_counts().to_dict(),
    }
    print(json.dumps(summary, indent=2))
