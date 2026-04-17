from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import (
    CSV_DIR,
    DATASET_AUDIT_SUMMARY_PATH,
    DATASET_SCHEMA_REPORT_PATH,
    DATASETS_DIR,
    FINAL_DATASET_EXTENDED_PATH,
    FINAL_DATASET_MINIMAL_PATH,
    FINAL_DATASET_PATH,
    FINAL_METADATA_PATH,
    PRIMARY_DATASET_PATH,
    PROJECT_ROOT,
    TARGET_COLUMN,
    ensure_project_dirs,
)


FEATURE_ALIASES = {
    "nitrogen": ["nitrogen", " n", "n", "no3", "nh4", "tn"],
    "phosphorus": ["phosphorus", " p", "p", "op", "tp", "exp"],
    "potassium": ["potassium", " k", "k", "ak", "exk"],
    "ph": ["ph"],
    "temperature": ["temp", "t2m", "temperature"],
    "rainfall": ["rain", "prec", "waterrequired", "prectotcorr"],
    "soil_moisture": ["moisture", "gwettop", "swc"],
    "organic_matter": ["orgc", "soc", "organic", "om", "oc"],
    "ec_salinity": ["ec", "salinity", "elco"],
    "soil_texture": ["clay", "silt", "sand", "soiltexture", "soil texture"],
    "cec": ["cec", "ktk"],
    "geolocation": ["latitude", "longitude", "location", "region"],
}

TARGET_CANDIDATES = {
    "crop",
    "crops",
    "label",
    "vegetation types",
    "species",
    "classified_area",
    "crop_name",
}

PRIMARY_RENAME_MAP = {
    "Soilcolor": "soil_color",
    "Ph": "ph",
    "K": "potassium",
    "P": "phosphorus",
    "N": "nitrogen",
    "Zn": "zinc",
    "S": "sulfur",
    "QV2M-W": "specific_humidity_winter",
    "QV2M-Sp": "specific_humidity_spring",
    "QV2M-Su": "specific_humidity_summer",
    "QV2M-Au": "specific_humidity_autumn",
    "T2M_MAX-W": "temperature_max_winter",
    "T2M_MAX-Sp": "temperature_max_spring",
    "T2M_MAX-Su": "temperature_max_summer",
    "T2M_MAX-Au": "temperature_max_autumn",
    "T2M_MIN-W": "temperature_min_winter",
    "T2M_MIN-Sp": "temperature_min_spring",
    "T2M_MIN-Su": "temperature_min_summer",
    "T2M_MIN-Au": "temperature_min_autumn",
    "PRECTOTCORR-W": "rainfall_winter",
    "PRECTOTCORR-Sp": "rainfall_spring",
    "PRECTOTCORR-Su": "rainfall_summer",
    "PRECTOTCORR-Au": "rainfall_autumn",
    "WD10M": "wind_speed_10m",
    "GWETTOP": "soil_moisture_surface",
    "CLOUD_AMT": "cloud_amount",
    "WS2M_RANGE": "wind_speed_range_2m",
    "PS": "surface_pressure",
    "label": TARGET_COLUMN,
}

PRIMARY_MINIMAL_COLUMNS = [
    "record_id",
    "source_dataset",
    "soil_color",
    "ph",
    "nitrogen",
    "phosphorus",
    "potassium",
    "temperature_mean",
    "rainfall_mean",
    "soil_moisture_surface",
    TARGET_COLUMN,
]

PRIMARY_DEFAULT_COLUMNS = [
    "record_id",
    "source_dataset",
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
    TARGET_COLUMN,
]

PRIMARY_EXTENDED_COLUMNS = [
    "record_id",
    "source_dataset",
    "soil_color",
    "ph",
    "nitrogen",
    "phosphorus",
    "potassium",
    "zinc",
    "sulfur",
    "specific_humidity_winter",
    "specific_humidity_spring",
    "specific_humidity_summer",
    "specific_humidity_autumn",
    "temperature_max_winter",
    "temperature_max_spring",
    "temperature_max_summer",
    "temperature_max_autumn",
    "temperature_min_winter",
    "temperature_min_spring",
    "temperature_min_summer",
    "temperature_min_autumn",
    "rainfall_winter",
    "rainfall_spring",
    "rainfall_summer",
    "rainfall_autumn",
    "wind_speed_10m",
    "soil_moisture_surface",
    "cloud_amount",
    "wind_speed_range_2m",
    "surface_pressure",
    "specific_humidity_mean",
    "temperature_mean",
    "temperature_seasonal_range",
    "rainfall_mean",
    "rainfall_total_proxy",
    TARGET_COLUMN,
]


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return "unknown"
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def snake_case(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown"


def feature_presence(columns: list[str]) -> dict[str, int]:
    lowered = [f" {snake_case(col)} " for col in columns]
    flags: dict[str, int] = {}
    for feature_name, aliases in FEATURE_ALIASES.items():
        present = any(any(alias in column for alias in aliases) for column in lowered)
        flags[f"has_{feature_name}"] = int(present)
    return flags


def find_target_candidate(columns: list[str]) -> str:
    lowered = {col.strip().lower(): col for col in columns}
    for candidate in TARGET_CANDIDATES:
        if candidate in lowered:
            return lowered[candidate]
    return ""


def path_lookup_from_inventory() -> dict[str, dict[str, Any]]:
    inventory_path = DATASETS_DIR / "dataset_sources.csv"
    if not inventory_path.exists():
        return {}

    inventory = pd.read_csv(inventory_path)
    lookup: dict[str, dict[str, Any]] = {}
    for row in inventory.to_dict(orient="records"):
        for key in ["local_raw_path", "local_csv_path"]:
            raw_value = str(row.get(key, "") or "")
            for item in [part.strip() for part in raw_value.split(";") if part.strip()]:
                try:
                    rel_path = str(Path(item).resolve().relative_to(PROJECT_ROOT))
                except ValueError:
                    continue
                lookup[rel_path] = row
                lookup[Path(rel_path).name] = row
    return lookup


def classify_file_role(relative_path: str, file_format: str) -> tuple[str, str, str]:
    file_name = Path(relative_path).name.lower()

    if relative_path in {"datasets/dataset_sources.csv", "datasets/papers_summary.csv"}:
        return "metadata_inventory", "n_a", "Project-level metadata inventory."
    if "mendeley_8v757rr4st_crop_recommendation_soil_weather.csv" in file_name:
        return "primary_training_candidate", "single_source_selected", "Best directly supervised crop-label dataset."
    if "github_nileshiq_crop_recommendation.csv" in file_name:
        return "benchmark_training_candidate", "append_only_possible_but_rejected", "Useful benchmark, but crop taxonomy and source shift differ materially."
    if "mendeley_vynxnppr7j_crop_recommendation.csv" in file_name:
        return "synthetic_training_candidate", "append_only_possible_but_rejected", "High-volume synthetic-augmented crop dataset; kept out of final training set."
    if "mendeley_v9r8c2cyp2" in file_name:
        return "alternative_vegetation_label_dataset", "label_space_incompatible", "Vegetation-type classification dataset, not crop recommendation."
    if "ecocrop" in file_name:
        return "rule_base_support", "label_level_only", "Useful for rule-assisted suitability filtering, not direct supervised training."
    if "wosis" in file_name:
        return "supporting_soil_backbone", "no_direct_label_key", "Good Indonesia soil backbone but lacks crop labels for direct supervised merge."
    if "worldclim" in file_name or "pdsi" in file_name or "soil_moisture" in file_name:
        return "supporting_climate_or_raster", "requires_geospatial_join", "Auxiliary climate or moisture source; needs geospatial alignment."
    if "training_samples" in file_name or "gaez" in file_name:
        return "supporting_spatial_label_dataset", "requires_spatial_join", "Useful for spatial weak supervision or future geospatial modeling."
    if file_format in {"zip", "tif", "geojson"}:
        return "raw_supporting_asset", "requires_conversion_or_spatial_processing", "Raw non-tabular asset retained for later processing."
    if relative_path.startswith("datasets/raw/") and (DATASETS_DIR / "csv" / Path(relative_path).name).exists():
        return "raw_duplicate_or_source_format", "n_a", "Raw counterpart retained alongside converted CSV."
    return "supporting_or_not_selected", "manual_review_needed", "No direct role selected for the current baseline."


def inspect_file(path: Path, inventory_lookup: dict[str, dict[str, Any]]) -> dict[str, Any]:
    relative_path = str(path.relative_to(PROJECT_ROOT))
    file_format = path.suffix.lower().lstrip(".")
    inventory_row = inventory_lookup.get(relative_path) or inventory_lookup.get(path.name) or {}

    info: dict[str, Any] = {
        "relative_path": relative_path,
        "file_name": path.name,
        "file_format": file_format or "unknown",
        "provider": inventory_row.get("provider", ""),
        "dataset_id": inventory_row.get("dataset_id", ""),
        "dataset_name": inventory_row.get("dataset_name", ""),
        "rows": None,
        "columns_count": None,
        "column_names": "",
        "target_candidate": "",
    }

    try:
        if file_format == "csv":
            df = pd.read_csv(path)
            info["rows"] = int(df.shape[0])
            info["columns_count"] = int(df.shape[1])
            info["column_names"] = " | ".join(df.columns.astype(str).tolist())
            info["target_candidate"] = find_target_candidate(df.columns.astype(str).tolist())
            info.update(feature_presence(df.columns.astype(str).tolist()))
        elif file_format in {"xlsx", "xls"}:
            df = pd.read_excel(path)
            info["rows"] = int(df.shape[0])
            info["columns_count"] = int(df.shape[1])
            info["column_names"] = " | ".join(df.columns.astype(str).tolist())
            info["target_candidate"] = find_target_candidate(df.columns.astype(str).tolist())
            info.update(feature_presence(df.columns.astype(str).tolist()))
        else:
            for feature_name in FEATURE_ALIASES:
                info[f"has_{feature_name}"] = 0
    except Exception as exc:  # pragma: no cover - defensive audit logging
        info["notes"] = f"Read error during audit: {exc}"
        for feature_name in FEATURE_ALIASES:
            info.setdefault(f"has_{feature_name}", 0)

    role, merge_feasibility, role_note = classify_file_role(relative_path, file_format)
    info["recommended_role"] = role
    info["merge_feasibility"] = merge_feasibility
    info["selected_for_final_dataset"] = int(path.resolve() == PRIMARY_DATASET_PATH.resolve())
    info["notes"] = " ".join(
        part
        for part in [str(info.get("notes", "")).strip(), str(inventory_row.get("notes", "")).strip(), role_note]
        if part
    ).strip()
    return info


def normalize_soil_color(value: Any) -> str:
    text = normalize_text(value).lower()
    text = text.replace(";", " ")
    text = text.replace("redish", "reddish")
    text = text.replace("reddis", "reddish")
    text = text.replace("broown", "brown")
    text = text.replace("lihgtish", "light")
    text = text.replace("darkbrown", "dark brown")
    text = text.replace("replacement of inaccessible target", "")
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text or text == "other":
        return "other"
    if "yellowish brown" in text:
        return "yellowish_brown"
    if "very dark brown" in text:
        return "very_dark_brown"
    if "very dark gray" in text:
        return "very_dark_gray"
    if "dark grayish brown" in text:
        return "dark_grayish_brown"
    if "grayish brown" in text:
        return "grayish_brown"
    if "dark reddish brown" in text or "reddish brown" in text or ("red" in text and "brown" in text):
        return "reddish_brown"
    if "dark brown" in text:
        return "dark_brown"
    if "brown" in text:
        return "brown"
    if "yellowish" in text:
        return "yellowish"
    if "black" in text or "vertisol" in text:
        return "black"
    if "dark gray" in text or "dark grey" in text:
        return "dark_gray"
    if "gray" in text or "grey" in text:
        return "gray"
    if "red" in text or "reddish" in text or "luvisol" in text:
        return "red"
    return snake_case(text)


def normalize_target_label(value: Any) -> str:
    text = normalize_text(value)
    text = text.replace("seed", "Seed")
    text = text.replace("pepper", "Pepper")
    text = text.title()
    text = text.replace("Niger Seed", "Niger Seed")
    return text


def build_final_datasets() -> dict[str, Any]:
    df = pd.read_csv(PRIMARY_DATASET_PATH).copy()
    rows_before = int(df.shape[0])

    df = df.rename(columns=PRIMARY_RENAME_MAP)
    df[TARGET_COLUMN] = df[TARGET_COLUMN].map(normalize_target_label)
    df["soil_color"] = df["soil_color"].map(normalize_soil_color)

    numeric_columns = [column for column in df.columns if column not in {"soil_color", TARGET_COLUMN}]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    humidity_columns = [
        "specific_humidity_winter",
        "specific_humidity_spring",
        "specific_humidity_summer",
        "specific_humidity_autumn",
    ]
    temp_max_columns = [
        "temperature_max_winter",
        "temperature_max_spring",
        "temperature_max_summer",
        "temperature_max_autumn",
    ]
    temp_min_columns = [
        "temperature_min_winter",
        "temperature_min_spring",
        "temperature_min_summer",
        "temperature_min_autumn",
    ]
    rainfall_columns = [
        "rainfall_winter",
        "rainfall_spring",
        "rainfall_summer",
        "rainfall_autumn",
    ]

    seasonal_means = pd.concat(
        [(df[max_col] + df[min_col]) / 2 for max_col, min_col in zip(temp_max_columns, temp_min_columns)],
        axis=1,
    )
    df["specific_humidity_mean"] = df[humidity_columns].mean(axis=1)
    df["temperature_mean"] = seasonal_means.mean(axis=1)
    df["temperature_seasonal_range"] = df[temp_max_columns].max(axis=1) - df[temp_min_columns].min(axis=1)
    df["rainfall_mean"] = df[rainfall_columns].mean(axis=1)
    df["rainfall_total_proxy"] = df[rainfall_columns].sum(axis=1)

    domain_masks = {
        "ph": df["ph"].between(0, 14),
        "soil_moisture_surface": df["soil_moisture_surface"].between(0, 1),
        "nitrogen": df["nitrogen"] >= 0,
        "phosphorus": df["phosphorus"] >= 0,
        "potassium": df["potassium"] >= 0,
        "rainfall_mean": df["rainfall_mean"] >= 0,
        "rainfall_total_proxy": df["rainfall_total_proxy"] >= 0,
    }
    for column, valid_mask in domain_masks.items():
        df.loc[~valid_mask, column] = pd.NA

    df = df[df[TARGET_COLUMN] != "Fallow"].copy()
    df = df.drop_duplicates().reset_index(drop=True)
    df.insert(0, "record_id", [f"rec_{index + 1:05d}" for index in range(len(df))])
    df.insert(1, "source_dataset", "mendeley_8v757rr4st")

    minimal_df = df[PRIMARY_MINIMAL_COLUMNS].copy()
    summary_df = df[PRIMARY_DEFAULT_COLUMNS].copy()
    extended_df = df[PRIMARY_EXTENDED_COLUMNS].copy()
    final_df = summary_df.copy()

    minimal_df.to_csv(FINAL_DATASET_MINIMAL_PATH, index=False)
    final_df.to_csv(FINAL_DATASET_PATH, index=False)
    extended_df.to_csv(FINAL_DATASET_EXTENDED_PATH, index=False)

    metadata = {
        "dataset_name": "Vegetation Recommendation Final Dataset",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "target_column": TARGET_COLUMN,
        "problem_framing": "multiclass_classification",
        "rows_before_cleaning": rows_before,
        "rows_after_cleaning": int(final_df.shape[0]),
        "removed_rows": rows_before - int(final_df.shape[0]),
        "n_features_final_dataset": int(final_df.shape[1] - 3),
        "n_features_minimal_dataset": int(minimal_df.shape[1] - 3),
        "n_features_extended_dataset": int(extended_df.shape[1] - 3),
        "source_datasets_used": [
            {
                "path": str(PRIMARY_DATASET_PATH.relative_to(PROJECT_ROOT)),
                "role": "primary_training_source",
                "used_in_final_dataset": True,
                "reason": "Best available supervised dataset with direct crop labels and aligned soil-plus-weather features.",
            }
        ],
        "source_datasets_considered_but_not_merged": [
            {
                "path": "datasets/csv/github_nileshiq_crop_recommendation.csv",
                "reason": "Label space and feature semantics differ; concatenation would introduce source shift without reliable reconciliation.",
            },
            {
                "path": "datasets/csv/mendeley_vynxnppr7j_crop_recommendation.csv",
                "reason": "Synthetic CTGAN augmentation makes it unsuitable as the default evaluation dataset.",
            },
            {
                "path": "datasets/csv/isric_wosis_latest_*.csv",
                "reason": "Strong Indonesia soil backbone, but no crop labels or direct keys to the supervised crop dataset.",
            },
        ],
        "merge_strategy": {
            "selected_strategy": "no_cross_source_row_level_merge_for_baseline",
            "reason": "Candidate datasets do not share reliable row-level keys, aligned label spaces, or fully consistent units. The baseline keeps a single-source supervised table and treats other files as benchmark or future enrichment sources.",
        },
        "cleaning_notes": [
            "Columns were standardized to snake_case.",
            "Soil color strings were normalized into a compact categorical vocabulary.",
            "Target labels were whitespace-normalized and title-cased.",
            "Rows with the non-crop label 'Fallow' were removed because they do not represent a vegetation/crop recommendation target.",
            "No duplicate rows remained after cleaning.",
            "Domain validation was applied for pH, rainfall, soil moisture, and nutrient non-negativity.",
            "Outliers were retained unless they violated hard domain rules because extreme agronomic values may still be valid observations.",
            "The recommended `final_dataset.csv` uses the summary-feature variant because it delivered stronger validation and hold-out macro F1 than the full extended feature set in baseline experiments.",
        ],
        "final_dataset_versions": {
            "final_dataset": {
                "path": str(FINAL_DATASET_PATH.relative_to(PROJECT_ROOT)),
                "rows": int(final_df.shape[0]),
                "columns": final_df.columns.tolist(),
            },
            "final_dataset_minimal": {
                "path": str(FINAL_DATASET_MINIMAL_PATH.relative_to(PROJECT_ROOT)),
                "rows": int(minimal_df.shape[0]),
                "columns": minimal_df.columns.tolist(),
            },
            "final_dataset_extended": {
                "path": str(FINAL_DATASET_EXTENDED_PATH.relative_to(PROJECT_ROOT)),
                "rows": int(extended_df.shape[0]),
                "columns": extended_df.columns.tolist(),
            },
        },
        "missing_value_summary": final_df.isna().sum().astype(int).to_dict(),
        "class_distribution": final_df[TARGET_COLUMN].value_counts().to_dict(),
        "column_metadata": {
            "record_id": {"description": "Stable row identifier generated during preparation.", "dtype": "string"},
            "source_dataset": {"description": "Provenance marker for the selected training source.", "dtype": "string"},
            "soil_color": {"description": "Normalized soil color category derived from the raw soil color text.", "dtype": "categorical"},
            "ph": {"description": "Soil pH from the source dataset.", "dtype": "float"},
            "nitrogen": {"description": "Soil nitrogen measurement from the source dataset.", "dtype": "float"},
            "phosphorus": {"description": "Soil phosphorus measurement from the source dataset.", "dtype": "float"},
            "potassium": {"description": "Soil potassium measurement from the source dataset.", "dtype": "float"},
            "zinc": {"description": "Soil zinc measurement from the source dataset.", "dtype": "float"},
            "sulfur": {"description": "Soil sulfur measurement from the source dataset.", "dtype": "float"},
            "specific_humidity_winter": {"description": "Seasonal specific humidity feature for winter from the source dataset.", "dtype": "float"},
            "specific_humidity_spring": {"description": "Seasonal specific humidity feature for spring from the source dataset.", "dtype": "float"},
            "specific_humidity_summer": {"description": "Seasonal specific humidity feature for summer from the source dataset.", "dtype": "float"},
            "specific_humidity_autumn": {"description": "Seasonal specific humidity feature for autumn from the source dataset.", "dtype": "float"},
            "temperature_max_winter": {"description": "Seasonal maximum temperature for winter from the source dataset.", "dtype": "float"},
            "temperature_max_spring": {"description": "Seasonal maximum temperature for spring from the source dataset.", "dtype": "float"},
            "temperature_max_summer": {"description": "Seasonal maximum temperature for summer from the source dataset.", "dtype": "float"},
            "temperature_max_autumn": {"description": "Seasonal maximum temperature for autumn from the source dataset.", "dtype": "float"},
            "temperature_min_winter": {"description": "Seasonal minimum temperature for winter from the source dataset.", "dtype": "float"},
            "temperature_min_spring": {"description": "Seasonal minimum temperature for spring from the source dataset.", "dtype": "float"},
            "temperature_min_summer": {"description": "Seasonal minimum temperature for summer from the source dataset.", "dtype": "float"},
            "temperature_min_autumn": {"description": "Seasonal minimum temperature for autumn from the source dataset.", "dtype": "float"},
            "rainfall_winter": {"description": "Seasonal corrected precipitation for winter from the source dataset.", "dtype": "float"},
            "rainfall_spring": {"description": "Seasonal corrected precipitation for spring from the source dataset.", "dtype": "float"},
            "rainfall_summer": {"description": "Seasonal corrected precipitation for summer from the source dataset.", "dtype": "float"},
            "rainfall_autumn": {"description": "Seasonal corrected precipitation for autumn from the source dataset.", "dtype": "float"},
            "wind_speed_10m": {"description": "Wind speed feature at 10 meters from the source dataset.", "dtype": "float"},
            "specific_humidity_mean": {"description": "Mean seasonal specific humidity computed from the four QV2M features.", "dtype": "float"},
            "temperature_mean": {"description": "Average seasonal mean temperature computed from max/min seasonal values.", "dtype": "float"},
            "temperature_seasonal_range": {"description": "Maximum seasonal temperature minus minimum seasonal temperature.", "dtype": "float"},
            "rainfall_mean": {"description": "Mean seasonal corrected precipitation across the four source precipitation columns.", "dtype": "float"},
            "rainfall_total_proxy": {"description": "Sum of the four seasonal precipitation columns retained as a total-rainfall proxy.", "dtype": "float"},
            "soil_moisture_surface": {"description": "Top-layer soil moisture proxy from the source dataset.", "dtype": "float"},
            "cloud_amount": {"description": "Cloud amount feature from the source dataset.", "dtype": "float"},
            "wind_speed_range_2m": {"description": "Range of near-surface wind speed from the source dataset.", "dtype": "float"},
            "surface_pressure": {"description": "Surface pressure feature from the source dataset.", "dtype": "float"},
            TARGET_COLUMN: {"description": "Normalized crop label used as the supervised learning target.", "dtype": "string"},
        },
    }

    with FINAL_METADATA_PATH.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=True)

    return {
        "minimal": minimal_df,
        "default": final_df,
        "extended": extended_df,
        "metadata": metadata,
    }


def build_dataset_audit_summary() -> pd.DataFrame:
    inventory_lookup = path_lookup_from_inventory()
    records = []
    for path in sorted(DATASETS_DIR.rglob("*")):
        if not path.is_file():
            continue
        records.append(inspect_file(path, inventory_lookup))
    audit_df = pd.DataFrame(records)
    numeric_columns = [column for column in ["rows", "columns_count", "selected_for_final_dataset"] if column in audit_df.columns]
    for column in numeric_columns:
        audit_df[column] = audit_df[column].fillna(0).astype(int)
    audit_df = audit_df.sort_values(["recommended_role", "relative_path"]).reset_index(drop=True)
    audit_df.to_csv(DATASET_AUDIT_SUMMARY_PATH, index=False)
    return audit_df


def dataset_schema_markdown(audit_df: pd.DataFrame, final_bundle: dict[str, Any]) -> str:
    primary_rows = audit_df.loc[audit_df["recommended_role"] == "primary_training_candidate"].copy()
    alternative_rows = audit_df.loc[
        audit_df["recommended_role"].isin(
            [
                "benchmark_training_candidate",
                "synthetic_training_candidate",
                "alternative_vegetation_label_dataset",
                "supporting_soil_backbone",
                "supporting_climate_or_raster",
                "rule_base_support",
                "supporting_spatial_label_dataset",
            ]
        )
    ].copy()

    def markdown_table(frame: pd.DataFrame) -> list[str]:
        if frame.empty:
            return ["No rows available."]
        columns = frame.columns.tolist()
        lines = [
            "| " + " | ".join(columns) + " |",
            "| " + " | ".join(["---"] * len(columns)) + " |",
        ]
        for _, row in frame.fillna("").iterrows():
            lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
        return lines

    report_lines = [
        "# Dataset Schema Report",
        "",
        "## Executive Summary",
        "",
        f"- Total files audited under `datasets/`: {int(audit_df.shape[0])}",
        f"- Files with direct label candidates: {int((audit_df['target_candidate'] != '').sum())}",
        "- Final supervised baseline uses a single-source dataset because no trustworthy row-level merge exists across the discovered sources.",
        "- Supporting Indonesia-first soil and climate sources are retained for future geospatial enrichment, not for the current supervised baseline.",
        "",
        "## Final Dataset Decision",
        "",
        "- Selected primary dataset: `datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`",
        "- Reason: strongest direct linkage between soil chemistry, weather variables, and crop labels; complete rows; no duplicates; no missing values before hard-domain validation.",
        "- Explicitly rejected for baseline merge: benchmark mirror dataset, synthetic CTGAN dataset, Indonesia soil-only profiles, climate rasters, and rule-base resources.",
        "",
        "## Primary Training Candidate",
        "",
        *markdown_table(
            primary_rows[
                [
                    "relative_path",
                    "rows",
                    "columns_count",
                    "target_candidate",
                    "merge_feasibility",
                    "notes",
                ]
            ]
        ),
        "",
        "## Other Relevant Files",
        "",
        *markdown_table(
            alternative_rows[
                [
                    "relative_path",
                    "recommended_role",
                    "rows",
                    "columns_count",
                    "target_candidate",
                    "merge_feasibility",
                ]
            ]
        ),
        "",
        "## Merge Assessment",
        "",
        "- `ds003` + `ds001`: only safe as benchmark comparison, not as a single training table, because feature semantics and crop label spaces differ.",
        "- `ds003` + `ds002`: possible append-only experiment, but rejected for default because `ds002` includes synthetic CTGAN-expanded records.",
        "- `ds003` + Indonesia soil/climate sources: not feasible for row-level merge because the supervised crop dataset lacks lat/lon keys in the downloadable table.",
        "- WoSIS + WorldClim + ESA Soil Moisture + GAEZ/Zenodo remains a valid future Indonesia-first geospatial modeling pipeline, but it requires spatial extraction and weak-label design beyond the current baseline.",
        "",
        "## Final Dataset Schemas",
        "",
        "### `final_dataset.csv`",
        "",
        "| Column | Description |",
        "| --- | --- |",
    ]

    for column, meta in final_bundle["metadata"]["column_metadata"].items():
        if column in final_bundle["default"].columns:
            report_lines.append(f"| `{column}` | {meta['description']} |")

    report_lines.extend(
        [
            "",
            "### `final_dataset_minimal.csv`",
            "",
            f"- Columns: {', '.join(final_bundle['minimal'].columns)}",
            "",
            "### `final_dataset_extended.csv`",
            "",
            f"- Columns: {', '.join(final_bundle['extended'].columns)}",
            "",
            "## Cleaning Notes",
            "",
        ]
    )
    report_lines.extend([f"- {note}" for note in final_bundle["metadata"]["cleaning_notes"]])

    report = "\n".join(report_lines)
    DATASET_SCHEMA_REPORT_PATH.write_text(report, encoding="utf-8")
    return report


def prepare_datasets() -> dict[str, Any]:
    ensure_project_dirs()
    audit_df = build_dataset_audit_summary()
    final_bundle = build_final_datasets()
    dataset_schema_markdown(audit_df, final_bundle)
    return {
        "audit_summary_path": str(DATASET_AUDIT_SUMMARY_PATH.relative_to(PROJECT_ROOT)),
        "schema_report_path": str(DATASET_SCHEMA_REPORT_PATH.relative_to(PROJECT_ROOT)),
        "final_dataset_path": str(FINAL_DATASET_PATH.relative_to(PROJECT_ROOT)),
        "final_dataset_minimal_path": str(FINAL_DATASET_MINIMAL_PATH.relative_to(PROJECT_ROOT)),
        "final_dataset_extended_path": str(FINAL_DATASET_EXTENDED_PATH.relative_to(PROJECT_ROOT)),
        "metadata_path": str(FINAL_METADATA_PATH.relative_to(PROJECT_ROOT)),
        "rows": int(final_bundle["default"].shape[0]),
        "target_distribution": final_bundle["metadata"]["class_distribution"],
    }


if __name__ == "__main__":
    summary = prepare_datasets()
    print(json.dumps(summary, indent=2))
