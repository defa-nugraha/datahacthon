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
        "colab": {
            "name": ZONE_SUBMISSION_NOTEBOOK_PATH.name,
            "provenance": [],
        },
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
            # Zone Model Submission Assessment Notebook

            Notebook ini mendokumentasikan **proses pembuatan model zona aktif saat ini** beserta EDA, evaluasi, rekayasa fitur, pemilihan model, pemanfaatan AI/Azure, dan insight strategis.

            Fokus notebook:
            - hanya memakai **dataset zona aktif expanded** yang sedang dipakai model saat ini
            - menampilkan artefak yang relevan untuk penilaian lomba
            - tetap memberi opsi untuk **rebuild dataset** dan **retrain model** bila diperlukan
            """
        ),
        markdown_cell(
            """
            ## Kriteria Penilaian yang Ditargetkan

            Notebook ini disusun agar mudah dipetakan ke rubric:

            1. **Metodologi dan Eksplorasi Data**
            2. **Performa Model dan Kualitas Kode**
            3. **Pemanfaatan AI dan Layanan Microsoft Azure**
            4. **Insight dan Solusi Strategis**

            Metrik seleksi utama tetap **macro F1**, karena dataset expanded masih imbalance dan beberapa kelas memiliki support rendah.
            """
        ),
        markdown_cell(
            """
            ## Setup Lokal / Colab

            Jika dijalankan di Google Colab:
            - upload atau mount seluruh folder project, bukan file notebook saja
            - simpan project di `/content/DATAHACTHON` atau di Google Drive
            - bila perlu set `COLAB_PROJECT_ROOT`
            """
        ),
        code_cell(
            """
            import os
            import subprocess
            import sys
            from pathlib import Path

            IN_COLAB = "google.colab" in sys.modules
            MOUNT_GOOGLE_DRIVE = False
            COLAB_PROJECT_ROOT = None
            # Contoh:
            # MOUNT_GOOGLE_DRIVE = True
            # COLAB_PROJECT_ROOT = "/content/drive/MyDrive/DATAHACTHON"

            if IN_COLAB and MOUNT_GOOGLE_DRIVE:
                from google.colab import drive
                drive.mount("/content/drive")

            if IN_COLAB:
                subprocess.check_call(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-q",
                        "pandas",
                        "numpy",
                        "matplotlib",
                        "seaborn",
                        "scikit-learn",
                        "joblib",
                        "catboost",
                        "lightgbm",
                        "xgboost",
                        "openai",
                        "azure-identity",
                        "nbformat",
                    ]
                )


            def _is_project_root(path: Path) -> bool:
                return (path / "scripts").exists() and (path / "data").exists() and (path / "artifacts").exists()


            def resolve_project_root(explicit_root: str | None = None) -> Path:
                if explicit_root:
                    candidate = Path(explicit_root).expanduser().resolve()
                    if _is_project_root(candidate):
                        return candidate
                    raise FileNotFoundError(
                        f"COLAB_PROJECT_ROOT tidak valid: {candidate}. "
                        "Folder harus mengandung `scripts/`, `data/`, dan `artifacts/`."
                    )

                cwd = Path.cwd().resolve()
                direct_candidates = [
                    cwd,
                    *cwd.parents,
                    Path("/content/DATAHACTHON"),
                    Path("/content/drive/MyDrive/DATAHACTHON"),
                    Path("/content/drive/MyDrive/Colab Notebooks/DATAHACTHON"),
                ]
                seen = set()
                for candidate in direct_candidates:
                    key = str(candidate)
                    if key in seen:
                        continue
                    seen.add(key)
                    if candidate.exists() and _is_project_root(candidate):
                        return candidate
                raise FileNotFoundError("Project root tidak ditemukan. Set COLAB_PROJECT_ROOT bila perlu.")


            PROJECT_ROOT = resolve_project_root(COLAB_PROJECT_ROOT)
            os.chdir(PROJECT_ROOT)
            if str(PROJECT_ROOT) not in sys.path:
                sys.path.insert(0, str(PROJECT_ROOT))

            print("IN_COLAB =", IN_COLAB)
            print("PROJECT_ROOT =", PROJECT_ROOT)
            """
        ),
        markdown_cell(
            """
            ## Konfigurasi Eksekusi

            - `REBUILD_DATASET`: membangun ulang dataset expanded dari pipeline integrasi data
            - `RETRAIN_MODEL`: melatih ulang model expanded aktif
            - `REFRESH_ASSESSMENT_ARTIFACTS`: menyegarkan EDA summary, scorecard, per-class metrics, dan feature importance

            Default notebook memakai artifact aktif agar lebih cepat dibuka, tetapi tetap merepresentasikan pipeline model saat ini.
            """
        ),
        code_cell(
            """
            REBUILD_DATASET = False
            RETRAIN_MODEL = False
            REFRESH_ASSESSMENT_ARTIFACTS = True
            RANDOM_STATE = 42
            """
        ),
        code_cell(
            """
            import json
            from pprint import pprint

            import joblib
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import seaborn as sns
            from IPython.display import Markdown, display

            plt.style.use("seaborn-v0_8-whitegrid")
            sns.set_palette("deep")
            pd.set_option("display.max_columns", 120)
            pd.set_option("display.width", 180)

            from app.core.config import Settings
            from scripts.assess_zone_submission import main as assess_submission
            from scripts.common import PROJECT_ROOT as CODE_PROJECT_ROOT
            from scripts.prepare_zone_dataset_expanded import main as prepare_zone_dataset_expanded
            from scripts.train_zone_model_expanded import main as train_zone_model_expanded
            """
        ),
        markdown_cell(
            """
            ## 1. Rebuild Pipeline Opsional

            Cell ini membuat notebook tetap jujur terhadap proses model saat ini. Jika flag diaktifkan:
            - dataset expanded akan dibangun ulang
            - model expanded akan dilatih ulang
            - artefak penilaian akan disegarkan
            """
        ),
        code_cell(
            """
            if REBUILD_DATASET:
                preparation_summary = prepare_zone_dataset_expanded()
                print("Dataset expanded rebuilt.")
                pprint(preparation_summary if preparation_summary is not None else {})

            if RETRAIN_MODEL:
                training_summary = train_zone_model_expanded()
                print("Expanded model retrained.")
                pprint(training_summary if training_summary is not None else {})

            if REFRESH_ASSESSMENT_ARTIFACTS:
                assess_submission()
                print("Assessment artifacts refreshed.")
            """
        ),
        markdown_cell(
            """
            ## 2. Load Dataset dan Artifact Aktif

            Dataset dan artefak yang dipakai notebook ini:
            - `data/processed/zone_dataset_expanded_id.csv`
            - `data/processed/zone_dataset_expanded_id_metadata.json`
            - `artifacts/best_model_metrics_expanded.json`
            - `artifacts/model_comparison_expanded.csv`
            - `artifacts/per_class_metrics_expanded.csv`
            - `artifacts/feature_importance_best_model_expanded.csv`
            - `artifacts/submission_scorecard.md`
            """
        ),
        code_cell(
            """
            DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "zone_dataset_expanded_id.csv"
            METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "zone_dataset_expanded_id_metadata.json"
            METRICS_PATH = PROJECT_ROOT / "artifacts" / "best_model_metrics_expanded.json"
            COMPARISON_PATH = PROJECT_ROOT / "artifacts" / "model_comparison_expanded.csv"
            PER_CLASS_PATH = PROJECT_ROOT / "artifacts" / "per_class_metrics_expanded.csv"
            IMPORTANCE_PATH = PROJECT_ROOT / "artifacts" / "feature_importance_best_model_expanded.csv"
            SCORECARD_PATH = PROJECT_ROOT / "artifacts" / "submission_scorecard.md"

            zone_df = pd.read_csv(DATASET_PATH)
            metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
            metrics_payload = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
            comparison_df = pd.read_csv(COMPARISON_PATH)
            per_class_df = pd.read_csv(PER_CLASS_PATH)
            importance_df = pd.read_csv(IMPORTANCE_PATH)

            selected_scenario = metrics_payload["selected_zone_scenario"]
            selected_metrics = metrics_payload["selected_zone_test_metrics"]
            selected_feature_columns = metrics_payload[selected_scenario]["feature_columns"]

            print("Dataset shape:", zone_df.shape)
            print("Selected scenario:", selected_scenario)
            print("Selected model:", metrics_payload["selected_zone_model_name"])
            print("Feature count:", len(selected_feature_columns))
            """
        ),
        markdown_cell(
            """
            ## 3. Snapshot Dataset Aktif

            Section ini menjawab bagian audit dasar:
            - target aktif
            - jumlah kelas
            - distribusi sumber data
            - ukuran dataset
            - struktur zona dan group split
            """
        ),
        code_cell(
            """
            snapshot_df = pd.DataFrame(
                [
                    {"item": "dataset_path", "value": str(DATASET_PATH.relative_to(PROJECT_ROOT))},
                    {"item": "target_column", "value": metrics_payload["target_column"]},
                    {"item": "jumlah_zona", "value": zone_df.shape[0]},
                    {"item": "jumlah_kelas", "value": zone_df[metrics_payload["target_column"]].nunique()},
                    {"item": "jumlah_konteks", "value": zone_df["base_context_id"].nunique()},
                    {"item": "selected_scenario", "value": selected_scenario},
                    {"item": "selected_model", "value": metrics_payload["selected_zone_model_name"]},
                    {"item": "group_split", "value": metrics_payload["split_strategy"]["group_column"]},
                ]
            )
            display(snapshot_df)
            display(zone_df.head())
            """
        ),
        markdown_cell(
            """
            ## 4. EDA: Distribusi Kelas dan Sumber Data

            Ini bagian utama untuk penilaian **Metodologi dan Eksplorasi Data**.
            """
        ),
        code_cell(
            """
            fig, axes = plt.subplots(1, 2, figsize=(16, 5))

            target_counts = zone_df[metrics_payload["target_column"]].value_counts()
            sns.barplot(x=target_counts.values, y=target_counts.index, ax=axes[0])
            axes[0].set_title("Distribusi Kelas Zona")
            axes[0].set_xlabel("Jumlah Zona")
            axes[0].set_ylabel("Label")

            source_counts = zone_df["source_dataset"].value_counts()
            sns.barplot(x=source_counts.values, y=source_counts.index, ax=axes[1])
            axes[1].set_title("Distribusi Sumber Dataset")
            axes[1].set_xlabel("Jumlah Zona")
            axes[1].set_ylabel("Source Dataset")

            plt.tight_layout()
            display(target_counts.rename_axis("label").reset_index(name="zone_count"))
            display(source_counts.rename_axis("source_dataset").reset_index(name="zone_count"))
            """
        ),
        code_cell(
            """
            fig, axes = plt.subplots(1, 2, figsize=(16, 5))

            sns.histplot(zone_df["sample_count"], bins=12, ax=axes[0])
            axes[0].set_title("Distribusi Jumlah Sample per Zona")
            axes[0].set_xlabel("sample_count")

            if "zone_label_dominance_ratio" in zone_df.columns:
                sns.histplot(zone_df["zone_label_dominance_ratio"], bins=10, ax=axes[1])
                axes[1].set_title("Dominance Ratio Label per Zona")
                axes[1].set_xlabel("zone_label_dominance_ratio")
            else:
                axes[1].axis("off")

            plt.tight_layout()
            """
        ),
        markdown_cell(
            """
            ## 5. EDA: Kualitas Fitur dan Missing Values

            Karena model aktif memakai feature schema fixed, kualitas fitur dan kelengkapan kolom perlu ditampilkan secara eksplisit.
            """
        ),
        code_cell(
            """
            missing_df = (
                zone_df[selected_feature_columns]
                .isna()
                .mean()
                .sort_values(ascending=False)
                .rename("missing_ratio")
                .reset_index()
                .rename(columns={"index": "feature"})
            )

            quality_summary = pd.DataFrame(
                [
                    {"metric": "feature_count", "value": len(selected_feature_columns)},
                    {"metric": "mean_missing_ratio", "value": float(zone_df[selected_feature_columns].isna().mean().mean())},
                    {"metric": "max_missing_ratio", "value": float(zone_df[selected_feature_columns].isna().mean().max())},
                    {"metric": "group_column_unique", "value": int(zone_df["base_context_id"].nunique())},
                ]
            )
            display(quality_summary)
            display(missing_df.head(15))
            """
        ),
        code_cell(
            """
            core_mean_features = [
                column
                for column in [
                    "ph_mean",
                    "nitrogen_mean",
                    "phosphorus_mean",
                    "potassium_mean",
                    "temperature_mean_mean",
                    "rainfall_mean_mean",
                ]
                if column in zone_df.columns
            ]

            fig, axes = plt.subplots(2, 3, figsize=(18, 8))
            axes = axes.flatten()
            for ax, column in zip(axes, core_mean_features):
                sns.histplot(zone_df[column], kde=True, ax=ax)
                ax.set_title(column)
            for ax in axes[len(core_mean_features):]:
                ax.axis("off")
            plt.tight_layout()
            """
        ),
        code_cell(
            """
            corr_columns = [column for column in core_mean_features if zone_df[column].nunique() > 1]
            corr_matrix = zone_df[corr_columns].corr(numeric_only=True)

            plt.figure(figsize=(8, 6))
            sns.heatmap(corr_matrix, annot=True, cmap="YlGnBu", fmt=".2f")
            plt.title("Korelasi Fitur Mean Inti")
            plt.tight_layout()
            """
        ),
        markdown_cell(
            """
            ## 6. Rekayasa Fitur dan Strategi Integrasi

            Ringkasan feature engineering model saat ini:
            - unit analisis: **zona**
            - skenario terpilih: **mean plus variability**
            - fitur yang dipakai tidak hanya mean, tetapi juga `std`, `min`, `max`, `median`, `count`, `range`, `cv`, `missing_ratio`
            - split evaluasi memakai `base_context_id` agar kebocoran antarkonteks ditekan
            """
        ),
        code_cell(
            """
            scenario_summary = pd.DataFrame(
                [
                    {
                        "scenario": "zone_mean_only",
                        "feature_count": len(metrics_payload["zone_mean_only"]["feature_columns"]),
                        "best_model": metrics_payload["zone_mean_only"]["best_model_name"],
                        "cv_macro_f1": metrics_payload["zone_mean_only"]["tuned_cv_f1_macro"],
                        "test_macro_f1": metrics_payload["zone_mean_only"]["test_metrics"]["f1_macro"],
                    },
                    {
                        "scenario": "zone_mean_plus_variability",
                        "feature_count": len(metrics_payload["zone_mean_plus_variability"]["feature_columns"]),
                        "best_model": metrics_payload["zone_mean_plus_variability"]["best_model_name"],
                        "cv_macro_f1": metrics_payload["zone_mean_plus_variability"]["tuned_cv_f1_macro"],
                        "test_macro_f1": metrics_payload["zone_mean_plus_variability"]["test_metrics"]["f1_macro"],
                    },
                ]
            )
            display(scenario_summary)
            """
        ),
        markdown_cell(
            """
            ## 7. Perbandingan Model

            Section ini menjawab bagian **Performa Model dan Kualitas Kode**.

            Kandidat yang dibandingkan pada pipeline expanded:
            - Logistic Regression
            - Random Forest
            - Extra Trees
            - LightGBM
            - CatBoost
            - XGBoost
            """
        ),
        code_cell(
            """
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
            best_row = comparison_df.loc[comparison_df["is_final_selected"] == True].copy()
            display(best_row)

            selected_metrics_df = pd.DataFrame(
                [
                    {"metric": "accuracy", "value": selected_metrics["accuracy"]},
                    {"metric": "precision_macro", "value": selected_metrics["precision_macro"]},
                    {"metric": "recall_macro", "value": selected_metrics["recall_macro"]},
                    {"metric": "f1_macro", "value": selected_metrics["f1_macro"]},
                    {"metric": "f1_weighted", "value": selected_metrics["f1_weighted"]},
                    {"metric": "cv_f1_macro", "value": metrics_payload["selected_zone_cv_metric_value"]},
                ]
            )
            display(selected_metrics_df)
            """
        ),
        markdown_cell(
            """
            ## 8. Evaluasi Final Model Terpilih

            Macro F1 tetap dijadikan acuan utama karena distribusi kelas tidak seimbang dan beberapa kelas hanya memiliki support rendah.
            """
        ),
        code_cell(
            """
            labels = metrics_payload["selected_zone_confusion_matrix_labels"]
            matrix = np.asarray(metrics_payload["selected_zone_confusion_matrix"])

            plt.figure(figsize=(10, 7))
            sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
            plt.title("Confusion Matrix Best Expanded Zone Model")
            plt.xlabel("Predicted")
            plt.ylabel("Actual")
            plt.xticks(rotation=35, ha="right")
            plt.tight_layout()
            """
        ),
        code_cell(
            """
            display(per_class_df)

            low_support_df = per_class_df.loc[per_class_df["support"] <= 4].copy()
            print("Kelas dengan support rendah (<=4 zona pada holdout):")
            display(low_support_df)
            """
        ),
        markdown_cell(
            """
            ## 9. Feature Importance dan Interpretabilitas

            Ini membantu menghubungkan model ke insight yang bisa ditindaklanjuti.
            """
        ),
        code_cell(
            """
            display(importance_df.head(20))

            plt.figure(figsize=(10, 6))
            top_imp = importance_df.head(15).sort_values("importance_mean", ascending=True)
            plt.barh(top_imp["feature"], top_imp["importance_mean"])
            plt.title("Top 15 Permutation Importance")
            plt.xlabel("Importance Mean (Macro F1 Drop)")
            plt.tight_layout()
            """
        ),
        markdown_cell(
            """
            ## 10. Pemanfaatan AI dan Azure

            Model prediksi inti tetap model tabular supervised. Di atasnya, project saat ini menambahkan **layer strategic advisor** berbasis Azure OpenAI untuk menerjemahkan output model menjadi rekomendasi tindakan yang lebih operasional.
            """
        ),
        code_cell(
            """
            settings = Settings.from_env()
            azure_summary = pd.DataFrame(
                [
                    {"setting": "azure_openai_enabled", "value": settings.azure_openai_enabled},
                    {"setting": "azure_openai_endpoint", "value": settings.azure_openai_endpoint},
                    {"setting": "azure_openai_deployment", "value": settings.azure_openai_deployment},
                    {"setting": "azure_openai_use_entra_id", "value": settings.azure_openai_use_entra_id},
                    {"setting": "active_zone_scenario", "value": settings.active_zone_scenario},
                    {"setting": "zone_model_path", "value": str(settings.zone_model_path.relative_to(settings.project_root))},
                ]
            )
            display(azure_summary)
            """
        ),
        code_cell(
            """
            azure_architecture = pd.DataFrame(
                [
                    {
                        "layer": "Tabular zone classifier",
                        "implementation": metrics_payload["selected_zone_model_name"],
                        "artifact": "artifacts/models/best_zone_model_expanded.joblib",
                    },
                    {
                        "layer": "Inference API",
                        "implementation": "FastAPI /predict/zone",
                        "artifact": "app/main.py",
                    },
                    {
                        "layer": "Strategic advisor",
                        "implementation": "FastAPI /insights/zone-strategy + Azure OpenAI fallback",
                        "artifact": "app/services/strategic_advisor.py",
                    },
                ]
            )
            display(azure_architecture)
            """
        ),
        markdown_cell(
            """
            ## 11. Insight dan Solusi Strategis

            Section ini menautkan output model ke dampak praktis. Notebook memuat scorecard internal dan artefak insight yang bisa langsung dipresentasikan.
            """
        ),
        code_cell(
            """
            display(Markdown(SCORECARD_PATH.read_text(encoding="utf-8")))
            """
        ),
        code_cell(
            """
            final_summary = pd.DataFrame(
                [
                    {"item": "Best Model", "value": metrics_payload["selected_zone_model_name"]},
                    {"item": "Best Scenario", "value": metrics_payload["selected_zone_scenario"]},
                    {"item": "Best Accuracy", "value": metrics_payload["selected_zone_test_metrics"]["accuracy"]},
                    {"item": "Best Macro F1", "value": metrics_payload["selected_zone_test_metrics"]["f1_macro"]},
                    {"item": "Best Macro Precision", "value": metrics_payload["selected_zone_test_metrics"]["precision_macro"]},
                    {"item": "Best Macro Recall", "value": metrics_payload["selected_zone_test_metrics"]["recall_macro"]},
                    {"item": "Selected CV Metric", "value": metrics_payload["selected_zone_cv_metric_value"]},
                ]
            )
            display(final_summary)
            """
        ),
        markdown_cell(
            """
            ## 12. Kesimpulan

            Notebook ini menunjukkan bahwa model aktif saat ini:
            - menggunakan **dataset zona expanded**
            - memilih model berdasarkan **macro F1** dan **group-aware CV**
            - mendukung **AI strategic layer** berbasis Azure OpenAI
            - memiliki artefak evaluasi yang lebih siap presentasi dibanding pipeline sebelumnya

            Keterbatasan yang tetap harus dijelaskan secara jujur:
            - sebagian zona masih pseudo-zone, belum boundary lapangan Indonesia yang nyata
            - beberapa kelas masih low-support
            - integrasi Azure sudah ada, tetapi belum deployment penuh ke layanan Azure produksi
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
