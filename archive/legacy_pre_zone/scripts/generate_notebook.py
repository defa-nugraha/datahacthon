from __future__ import annotations

from textwrap import dedent

import sys
from pathlib import Path

import nbformat as nbf

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import DEFAULT_NOTEBOOK_PATH, ensure_project_dirs


def markdown_cell(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip() + "\n")


def code_cell(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip() + "\n")


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "colab": {
            "name": "vegetation_recommendation_model.ipynb",
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
            # Vegetation Recommendation Modeling Notebook

            Notebook ini menyiapkan dataset final, melakukan EDA, membandingkan beberapa model tabular, melakukan tuning secukupnya, lalu menyimpan artifact model untuk sistem rekomendasi vegetasi/tanaman berbasis kondisi tanah dan lingkungan.

            Notebook ini juga disiapkan agar kompatibel dengan Google Colab. Jika dijalankan di Colab, simpan seluruh project folder ke `/content/DATAHACTHON` atau mount Google Drive lalu arahkan `COLAB_PROJECT_ROOT` ke folder project Anda.
            """
        ),
        markdown_cell(
            """
            ## Colab Setup

            Jika notebook ini dibuka di Google Colab:

            1. Pastikan seluruh isi project tersedia, bukan hanya file notebook.
            2. Opsi termudah adalah meletakkan project di `/content/DATAHACTHON`.
            3. Jika project ada di Google Drive, ubah `MOUNT_GOOGLE_DRIVE = True` dan isi `COLAB_PROJECT_ROOT`.
            4. Jalankan cell setup berikut sebelum cell lainnya.
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
                        "scikit-learn",
                        "matplotlib",
                        "seaborn",
                        "joblib",
                        "nbformat",
                    ]
                )


            def _is_project_root(path: Path) -> bool:
                return (path / "scripts").exists() and (path / "datasets").exists()


            def resolve_project_root(explicit_root: str | None = None) -> Path:
                if explicit_root:
                    candidate = Path(explicit_root).expanduser().resolve()
                    if _is_project_root(candidate):
                        return candidate
                    raise FileNotFoundError(
                        f"COLAB_PROJECT_ROOT tidak valid: {candidate}. "
                        "Folder harus mengandung `scripts/` dan `datasets/`."
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
                    candidate_str = str(candidate)
                    if candidate_str in seen:
                        continue
                    seen.add(candidate_str)
                    if candidate.exists() and _is_project_root(candidate):
                        return candidate

                search_bases = [Path("/content"), Path("/content/drive/MyDrive")]
                search_patterns = [
                    "*/scripts/common.py",
                    "*/*/scripts/common.py",
                    "*/*/*/scripts/common.py",
                ]
                for base in search_bases:
                    if not base.exists():
                        continue
                    for pattern in search_patterns:
                        for match in base.glob(pattern):
                            candidate = match.parents[1]
                            if _is_project_root(candidate):
                                return candidate

                raise FileNotFoundError(
                    "Project root tidak ditemukan. "
                    "Jika di Colab, upload seluruh folder project ke /content/DATAHACTHON "
                    "atau set COLAB_PROJECT_ROOT ke folder project yang benar."
                )


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
            ## 1. Project Overview

            **Goal**

            Membangun baseline realistis untuk memetakan kondisi tanah dan lingkungan ke rekomendasi tanaman.

            **Problem formulation**

            Baseline diframing sebagai *multiclass classification*, bukan recommender system tradisional, karena dataset yang tersedia memiliki satu label tanaman per observasi dan tidak memiliki user-item interaction atau graded relevance.

            **Dataset summary**

            Final training dataset dipilih dari sumber berlabel paling kuat dan tidak dipaksa merge dengan sumber lain yang tidak punya kunci join yang andal.
            """
        ),
        code_cell(
            """
            import json

            import numpy as np
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt
            from IPython.display import display

            plt.style.use("seaborn-v0_8-whitegrid")
            sns.set_palette("deep")

            from scripts.data_preparation import prepare_datasets
            from scripts.train_model import create_data_splits, infer_feature_types, run_training
            from scripts.inference import predict_from_payload
            from scripts.common import FINAL_DATASET_PATH, FINAL_METADATA_PATH, MODEL_METRICS_PATH

            RANDOM_STATE = 42
            """
        ),
        markdown_cell(
            """
            ## 2. Prepare And Load Dataset

            Cell ini menjalankan pipeline preparation agar file processed dan artifact audit selalu sinkron dengan notebook.
            """
        ),
        code_cell(
            """
            prep_summary = prepare_datasets()
            dataset = pd.read_csv(FINAL_DATASET_PATH)
            metadata = json.loads(FINAL_METADATA_PATH.read_text(encoding="utf-8"))

            print(prep_summary)
            print("Dataset shape:", dataset.shape)
            display(dataset.head())
            """
        ),
        code_cell(
            """
            print("Columns:")
            print(dataset.columns.tolist())
            print("\\nClass distribution:")
            display(dataset["target_crop"].value_counts().rename_axis("target_crop").reset_index(name="count"))
            print("\\nMissing values:")
            display(
                dataset.isna()
                .sum()
                .sort_values(ascending=False)
                .rename_axis("column")
                .reset_index(name="missing_count")
            )
            """
        ),
        markdown_cell(
            """
            ## 3. Exploratory Data Analysis

            Fokus EDA adalah memeriksa distribusi target, ketersediaan data, hubungan antar fitur numerik, dan kualitas sinyal fitur inti.
            """
        ),
        code_cell(
            """
            fig, axes = plt.subplots(1, 2, figsize=(18, 5))
            target_counts = dataset["target_crop"].value_counts()
            sns.barplot(x=target_counts.values, y=target_counts.index, ax=axes[0])
            axes[0].set_title("Target Class Distribution")
            axes[0].set_xlabel("Count")
            axes[0].set_ylabel("Crop")

            missing_share = dataset.isna().mean().sort_values(ascending=False)
            sns.barplot(x=missing_share.values, y=missing_share.index, ax=axes[1])
            axes[1].set_title("Missing Value Share")
            axes[1].set_xlabel("Share of Missing Values")
            axes[1].set_ylabel("Feature")
            plt.tight_layout()

            imbalance_ratio = target_counts.max() / target_counts.min()
            print(f"Class imbalance ratio (max/min): {imbalance_ratio:.2f}")
            print("Key insight: missing values are negligible, but class imbalance is material enough to justify macro metrics and class-balanced models.")
            """
        ),
        code_cell(
            """
            numeric_cols = dataset.select_dtypes(include=["number"]).columns.tolist()
            corr = dataset[numeric_cols].corr()

            plt.figure(figsize=(12, 8))
            sns.heatmap(corr, cmap="coolwarm", center=0)
            plt.title("Numeric Feature Correlation Heatmap")
            plt.tight_layout()

            core_features = [
                "nitrogen",
                "phosphorus",
                "potassium",
                "ph",
                "temperature_mean",
                "rainfall_mean",
                "soil_moisture_surface",
            ]
            dataset[core_features].hist(figsize=(14, 10), bins=20)
            plt.suptitle("Core Feature Distributions", y=1.02)
            plt.tight_layout()

            strongest_pairs = (
                corr.where(~np.eye(len(corr), dtype=bool))
                .abs()
                .unstack()
                .sort_values(ascending=False)
                .drop_duplicates()
                .head(10)
            )
            print("Top absolute correlations:")
            print(strongest_pairs)
            """
        ),
        markdown_cell(
            """
            ## 4. Data Preprocessing

            Split dilakukan secara stratified. Preprocessing aktual dijalankan di dalam scikit-learn pipeline untuk menghindari data leakage.
            """
        ),
        code_cell(
            """
            splits = create_data_splits(dataset, random_state=RANDOM_STATE)
            numeric_features, categorical_features = infer_feature_types(splits["X_train"])

            split_summary = pd.DataFrame(
                {
                    "split": ["train", "validation", "test"],
                    "rows": [len(splits["X_train"]), len(splits["X_val"]), len(splits["X_test"])],
                }
            )
            display(split_summary)
            print("Numeric features:", numeric_features)
            print("Categorical features:", categorical_features)
            """
        ),
        markdown_cell(
            """
            ## 5. Baseline Models And Comparison

            Notebook menggunakan fungsi reusable dari `scripts/train_model.py` agar hasil notebook dan artifact CLI tetap identik.
            """
        ),
        code_cell(
            """
            results = run_training(save_artifacts=True, random_state=RANDOM_STATE)
            comparison_df = results["comparison_df"]
            display(comparison_df)
            print("Best model from CV:", results["metrics_payload"]["best_model_name"])
            print("Best CV macro F1:", round(results["metrics_payload"]["best_cv_macro_f1"], 4))
            """
        ),
        markdown_cell(
            """
            ## 6. Hyperparameter Tuning And Final Evaluation

            Hanya model terbaik dari CV yang ditune. Evaluasi akhir dilakukan pada hold-out test set setelah model ditrain ulang pada gabungan train + validation.
            """
        ),
        code_cell(
            """
            metrics_payload = results["metrics_payload"]
            print("Best params:")
            print(metrics_payload["best_model_params"])

            validation_metrics = pd.DataFrame([metrics_payload["validation_metrics"]], index=["validation"])
            test_metrics = pd.DataFrame([metrics_payload["test_metrics"]], index=["test"])
            display(pd.concat([validation_metrics, test_metrics]))
            """
        ),
        code_cell(
            """
            labels = metrics_payload["confusion_matrix_labels"]
            cm = pd.DataFrame(metrics_payload["confusion_matrix"], index=labels, columns=labels)

            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, cmap="Blues", annot=False)
            plt.title("Confusion Matrix - Hold-out Test Set")
            plt.ylabel("Actual")
            plt.xlabel("Predicted")
            plt.tight_layout()

            report_df = pd.DataFrame(metrics_payload["classification_report"]).transpose()
            display(report_df)
            """
        ),
        markdown_cell(
            """
            ## 7. Feature Importance / Explainability

            Permutation importance dipakai agar interpretasi tetap konsisten pada model pipeline penuh dan fitur kategori hasil encoding.
            """
        ),
        code_cell(
            """
            feature_importance_df = results["feature_importance_df"].head(15)
            display(feature_importance_df)

            plt.figure(figsize=(10, 6))
            sns.barplot(data=feature_importance_df, x="importance_mean", y="feature")
            plt.title("Top 15 Permutation Importances")
            plt.xlabel("Importance Mean (macro F1 drop)")
            plt.ylabel("Feature")
            plt.tight_layout()
            """
        ),
        markdown_cell(
            """
            ## 8. Error Analysis

            Fokus error analysis adalah melihat kelas yang sulit dibedakan dan contoh misclassifications di test set.
            """
        ),
        code_cell(
            """
            prediction_df = results["prediction_df"]
            misclassified = prediction_df.loc[prediction_df["is_correct"] == 0].copy()
            print("Misclassified rows:", len(misclassified))
            display(misclassified.head(15))

            confusion_summary = (
                misclassified.groupby(["actual_target", "predicted_target"]).size().reset_index(name="count")
                .sort_values("count", ascending=False)
            )
            display(confusion_summary.head(15))
            """
        ),
        markdown_cell(
            """
            ## 9. Final Recommendation

            Model terbaik dipilih berdasarkan macro F1, bukan accuracy saja, untuk mengurangi bias terhadap kelas mayoritas. Jika baseline ini ingin dipindahkan ke konteks Indonesia, langkah berikutnya harus berupa domain adaptation dengan backbone soil/climate Indonesia, bukan sekadar deploy model apa adanya.
            """
        ),
        code_cell(
            """
            print("Best model:", metrics_payload["best_model_name"])
            print("Test metrics:", metrics_payload["test_metrics"])
            print("Top features:", results["feature_importance_df"].head(10)["feature"].tolist())
            print(
                "Recommendation: keep this classifier as the baseline engine, "
                "and use EcoCrop/GAEZ-style rules as a deployment-time plausibility filter."
            )
            """
        ),
        markdown_cell(
            """
            ## 10. Inference Example

            Contoh inferensi sederhana menggunakan median numeric values dan mode categorical value dari dataset final.
            """
        ),
        code_cell(
            """
            example_payload = {}
            for column in dataset.columns:
                if column in {"record_id", "source_dataset", "target_crop"}:
                    continue
                if pd.api.types.is_numeric_dtype(dataset[column]):
                    example_payload[column] = float(dataset[column].median())
                else:
                    example_payload[column] = dataset[column].mode().iloc[0]

            inference_result = predict_from_payload(example_payload, top_k=3)
            inference_result
            """
        ),
        markdown_cell(
            """
            ## 11. Saved Artifacts

            Semua artifact inti disimpan ke folder `artifacts/` dan bisa dipakai ulang tanpa retraining penuh.
            """
        ),
        code_cell(
            """
            metrics = json.loads(MODEL_METRICS_PATH.read_text(encoding="utf-8"))
            print("Artifacts generated:")
            for path in [
                "artifacts/model_metrics.json",
                "artifacts/feature_importance.csv",
                "artifacts/prediction_samples.csv",
                "artifacts/models/best_model.joblib",
                "artifacts/pipelines/preprocessing_pipeline.joblib",
                "artifacts/modeling_strategy.md",
            ]:
                print("-", path)

            print("\\nTest macro F1:", metrics["test_metrics"]["f1_macro"])
            """
        ),
    ]
    return nb


def main() -> None:
    ensure_project_dirs()
    notebook = build_notebook()
    DEFAULT_NOTEBOOK_PATH.write_text(nbf.writes(notebook), encoding="utf-8")
    print(DEFAULT_NOTEBOOK_PATH)


if __name__ == "__main__":
    main()
