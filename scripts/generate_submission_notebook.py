from __future__ import annotations

from textwrap import dedent

import sys
from pathlib import Path

import nbformat as nbf

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import ZONE_SUBMISSION_NOTEBOOK_PATH, ensure_project_dirs


def markdown_cell(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip() + "\n")


def code_cell(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip() + "\n")


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.12",
        },
    }

    nb["cells"] = [
        markdown_cell(
            """
            # Pembuatan Model Rekomendasi Vegetasi Berbasis Zona

            Notebook ini berisi proses pembuatan model klasifikasi tanaman berbasis zona, mulai dari pemuatan dataset, eksplorasi data, rekayasa fitur, pemilihan model, evaluasi, hingga penyimpanan artifact.
            """
        ),
        markdown_cell(
            """
            ## 1. Setup Environment
            """
        ),
        code_cell(
            """
            import os
            import sys
            from pathlib import Path


            def _is_project_root(path: Path) -> bool:
                return (path / "scripts").exists() and (path / "data").exists() and (path / "artifacts").exists()


            def resolve_project_root() -> Path:
                cwd = Path.cwd().resolve()
                for candidate in [cwd, *cwd.parents]:
                    if _is_project_root(candidate):
                        return candidate
                raise FileNotFoundError("Project root tidak ditemukan.")


            PROJECT_ROOT = resolve_project_root()
            os.chdir(PROJECT_ROOT)
            if str(PROJECT_ROOT) not in sys.path:
                sys.path.insert(0, str(PROJECT_ROOT))

            print("PROJECT_ROOT =", PROJECT_ROOT)
            """
        ),
        code_cell(
            """
            import json

            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            from IPython.display import display

            plt.style.use("seaborn-v0_8-whitegrid")
            sns.set_palette("deep")
            pd.set_option("display.max_columns", 120)
            pd.set_option("display.width", 180)

            from scripts.prepare_zone_dataset_expanded import main as prepare_zone_dataset_expanded
            from scripts.train_zone_model_expanded import main as train_zone_model_expanded
            """
        ),
        markdown_cell(
            """
            ## 2. Konfigurasi Pipeline

            Gunakan `REBUILD_DATASET=True` untuk membangun ulang dataset zona expanded. Gunakan `FIT_MODEL=True` untuk melatih ulang model dan menulis ulang artifact evaluasi.
            """
        ),
        code_cell(
            """
            REBUILD_DATASET = False
            FIT_MODEL = False
            RANDOM_STATE = 42

            DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "zone_dataset_expanded_id.csv"
            METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "zone_dataset_expanded_id_metadata.json"
            METRICS_PATH = PROJECT_ROOT / "artifacts" / "best_model_metrics_expanded.json"
            COMPARISON_PATH = PROJECT_ROOT / "artifacts" / "model_comparison_expanded.csv"
            REPORT_PATH = PROJECT_ROOT / "artifacts" / "classification_report_best_model_expanded.txt"
            MODEL_PATH = PROJECT_ROOT / "artifacts" / "models" / "best_zone_model_expanded.joblib"
            PIPELINE_PATH = PROJECT_ROOT / "artifacts" / "pipelines" / "best_zone_pipeline_expanded.joblib"
            """
        ),
        markdown_cell(
            """
            ## 3. Persiapan Dataset Zona
            """
        ),
        code_cell(
            """
            if REBUILD_DATASET:
                prepare_zone_dataset_expanded()

            zone_df = pd.read_csv(DATASET_PATH)
            metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

            print("Dataset shape:", zone_df.shape)
            print("Jumlah kelas:", zone_df["zone_target"].nunique())
            display(zone_df.head())
            """
        ),
        code_cell(
            """
            dataset_summary = pd.DataFrame(
                [
                    {"item": "jumlah_zona", "value": zone_df.shape[0]},
                    {"item": "jumlah_kolom", "value": zone_df.shape[1]},
                    {"item": "jumlah_kelas", "value": zone_df["zone_target"].nunique()},
                    {"item": "jumlah_context_group", "value": zone_df["base_context_id"].nunique()},
                    {"item": "target_column", "value": "zone_target"},
                ]
            )
            display(dataset_summary)

            display(pd.Series(metadata.get("source_distribution", {}), name="zone_count").rename_axis("source_dataset").reset_index())
            """
        ),
        markdown_cell(
            """
            ## 4. Exploratory Data Analysis
            """
        ),
        code_cell(
            """
            target_counts = zone_df["zone_target"].value_counts()

            plt.figure(figsize=(10, 6))
            sns.barplot(x=target_counts.values, y=target_counts.index)
            plt.title("Distribusi Kelas Tanaman")
            plt.xlabel("Jumlah Zona")
            plt.ylabel("Kelas")
            plt.tight_layout()

            display(target_counts.rename_axis("zone_target").reset_index(name="zone_count"))
            """
        ),
        code_cell(
            """
            fig, axes = plt.subplots(1, 2, figsize=(15, 5))

            sns.histplot(zone_df["sample_count"], bins=12, ax=axes[0])
            axes[0].set_title("Distribusi Sample per Zona")
            axes[0].set_xlabel("sample_count")

            if "zone_label_dominance_ratio" in zone_df.columns:
                sns.histplot(zone_df["zone_label_dominance_ratio"], bins=10, ax=axes[1])
                axes[1].set_title("Dominansi Label per Zona")
                axes[1].set_xlabel("zone_label_dominance_ratio")
            else:
                axes[1].axis("off")

            plt.tight_layout()
            """
        ),
        code_cell(
            """
            core_features = [
                "ph_mean",
                "nitrogen_mean",
                "phosphorus_mean",
                "potassium_mean",
                "temperature_mean_mean",
                "rainfall_mean_mean",
            ]
            core_features = [column for column in core_features if column in zone_df.columns]

            fig, axes = plt.subplots(2, 3, figsize=(18, 8))
            axes = axes.flatten()
            for ax, column in zip(axes, core_features):
                sns.histplot(zone_df[column], kde=True, ax=ax)
                ax.set_title(column)
            for ax in axes[len(core_features):]:
                ax.axis("off")
            plt.tight_layout()
            """
        ),
        code_cell(
            """
            missing_summary = (
                zone_df.isna()
                .mean()
                .sort_values(ascending=False)
                .rename("missing_ratio")
                .reset_index()
                .rename(columns={"index": "column"})
            )
            display(missing_summary.head(20))
            """
        ),
        code_cell(
            """
            corr_matrix = zone_df[core_features].corr(numeric_only=True)

            plt.figure(figsize=(8, 6))
            sns.heatmap(corr_matrix, annot=True, cmap="YlGnBu", fmt=".2f")
            plt.title("Korelasi Fitur Inti")
            plt.tight_layout()
            """
        ),
        markdown_cell(
            """
            ## 5. Rekayasa Fitur Zona

            Dataset model menggunakan dua skenario fitur:

            - `zone_mean_only`: fitur rata-rata zona
            - `zone_mean_plus_variability`: fitur rata-rata ditambah variasi internal zona seperti `std`, `min`, `max`, `median`, `range`, `cv`, dan `missing_ratio`
            """
        ),
        code_cell(
            """
            metrics_payload = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

            scenario_summary = pd.DataFrame(
                [
                    {
                        "scenario": "zone_mean_only",
                        "feature_count": len(metrics_payload["zone_mean_only"]["feature_columns"]),
                    },
                    {
                        "scenario": "zone_mean_plus_variability",
                        "feature_count": len(metrics_payload["zone_mean_plus_variability"]["feature_columns"]),
                    },
                ]
            )
            display(scenario_summary)
            """
        ),
        markdown_cell(
            """
            ## 6. Training dan Model Selection

            Pipeline training membandingkan beberapa model tabular dan memilih model berdasarkan `macro F1` pada group-aware cross validation.
            """
        ),
        code_cell(
            """
            if FIT_MODEL:
                metrics_payload = train_zone_model_expanded()

            comparison_df = pd.read_csv(COMPARISON_PATH)
            display(
                comparison_df.sort_values(
                    ["scenario_name", "cv_f1_macro_mean", "test_f1_macro"],
                    ascending=[True, False, False],
                ).reset_index(drop=True)
            )
            """
        ),
        code_cell(
            """
            selected_scenario = metrics_payload["selected_zone_scenario"]
            selected_model = metrics_payload["selected_zone_model_name"]
            selected_metrics = metrics_payload["selected_zone_test_metrics"]

            selected_summary = pd.DataFrame(
                [
                    {"item": "selected_scenario", "value": selected_scenario},
                    {"item": "selected_model", "value": selected_model},
                    {"item": "cv_macro_f1", "value": metrics_payload["selected_zone_cv_metric_value"]},
                    {"item": "test_accuracy", "value": selected_metrics["accuracy"]},
                    {"item": "test_macro_precision", "value": selected_metrics["precision_macro"]},
                    {"item": "test_macro_recall", "value": selected_metrics["recall_macro"]},
                    {"item": "test_macro_f1", "value": selected_metrics["f1_macro"]},
                    {"item": "test_weighted_f1", "value": selected_metrics["f1_weighted"]},
                ]
            )
            display(selected_summary)
            """
        ),
        markdown_cell(
            """
            ## 7. Evaluasi Model Final
            """
        ),
        code_cell(
            """
            labels = metrics_payload["selected_zone_confusion_matrix_labels"]
            matrix = np.asarray(metrics_payload["selected_zone_confusion_matrix"])

            plt.figure(figsize=(10, 7))
            sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
            plt.title("Confusion Matrix")
            plt.xlabel("Predicted")
            plt.ylabel("Actual")
            plt.xticks(rotation=35, ha="right")
            plt.tight_layout()
            """
        ),
        code_cell(
            """
            report = metrics_payload["selected_zone_classification_report"]
            per_class_rows = []
            for label, values in report.items():
                if isinstance(values, dict) and label not in {"macro avg", "weighted avg"}:
                    per_class_rows.append(
                        {
                            "label": label,
                            "precision": values["precision"],
                            "recall": values["recall"],
                            "f1_score": values["f1-score"],
                            "support": values["support"],
                        }
                    )

            per_class_df = pd.DataFrame(per_class_rows).sort_values(["support", "f1_score"], ascending=[True, False])
            display(per_class_df)
            """
        ),
        code_cell(
            """
            print(REPORT_PATH.read_text(encoding="utf-8"))
            """
        ),
        markdown_cell(
            """
            ## 8. Penyimpanan Artifact
            """
        ),
        code_cell(
            """
            artifact_summary = pd.DataFrame(
                [
                    {"artifact": "model", "path": str(MODEL_PATH.relative_to(PROJECT_ROOT)), "exists": MODEL_PATH.exists()},
                    {"artifact": "pipeline", "path": str(PIPELINE_PATH.relative_to(PROJECT_ROOT)), "exists": PIPELINE_PATH.exists()},
                    {"artifact": "metrics", "path": str(METRICS_PATH.relative_to(PROJECT_ROOT)), "exists": METRICS_PATH.exists()},
                    {"artifact": "comparison", "path": str(COMPARISON_PATH.relative_to(PROJECT_ROOT)), "exists": COMPARISON_PATH.exists()},
                    {"artifact": "classification_report", "path": str(REPORT_PATH.relative_to(PROJECT_ROOT)), "exists": REPORT_PATH.exists()},
                ]
            )
            display(artifact_summary)
            """
        ),
    ]

    return nb


def main() -> Path:
    ensure_project_dirs()
    notebook = build_notebook()
    ZONE_SUBMISSION_NOTEBOOK_PATH.write_text(
        nbf.writes(notebook),
        encoding="utf-8",
    )
    return ZONE_SUBMISSION_NOTEBOOK_PATH


if __name__ == "__main__":
    path = main()
    print(path)
