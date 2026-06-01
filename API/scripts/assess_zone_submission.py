from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.inspection import permutation_importance

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import ARTIFACTS_DIR, PROJECT_ROOT


DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "zone_dataset_expanded_id.csv"
METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "zone_dataset_expanded_id_metadata.json"
METRICS_PATH = ARTIFACTS_DIR / "best_model_metrics_expanded.json"
MODEL_PATH = ARTIFACTS_DIR / "models" / "best_zone_model_expanded.joblib"

EDA_SUMMARY_PATH = ARTIFACTS_DIR / "eda_zone_expanded.md"
PER_CLASS_METRICS_PATH = ARTIFACTS_DIR / "per_class_metrics_expanded.csv"
FEATURE_IMPORTANCE_PATH = ARTIFACTS_DIR / "feature_importance_best_model_expanded.csv"
SCORECARD_PATH = ARTIFACTS_DIR / "submission_scorecard.md"

TARGET_COLUMN = "zone_target"
PROVENANCE_COLUMNS = {
    "zone_id",
    "base_context_id",
    "source_dataset",
    "source_region",
    "integration_strategy",
    "sample_count_risk_flag",
    "label_nunique",
    "zone_label_dominance_ratio",
}


def load_inputs() -> tuple[pd.DataFrame, dict, dict]:
    dataset = pd.read_csv(DATASET_PATH)
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return dataset, metadata, metrics


def build_per_class_metrics(metrics_payload: dict) -> pd.DataFrame:
    report = metrics_payload["selected_zone_classification_report"]
    rows: list[dict[str, float | str | int]] = []
    for label, values in report.items():
        if not isinstance(values, dict) or label in {"accuracy", "macro avg", "weighted avg"}:
            continue
        rows.append(
            {
                "label": label,
                "precision": round(float(values["precision"]), 4),
                "recall": round(float(values["recall"]), 4),
                "f1_score": round(float(values["f1-score"]), 4),
                "support": int(values["support"]),
            }
        )
    per_class_df = pd.DataFrame(rows).sort_values(["support", "f1_score"], ascending=[True, False]).reset_index(drop=True)
    per_class_df.to_csv(PER_CLASS_METRICS_PATH, index=False)
    return per_class_df


def build_feature_importance(dataset: pd.DataFrame, metrics_payload: dict) -> pd.DataFrame:
    selected_scenario = metrics_payload["selected_zone_scenario"]
    feature_columns = metrics_payload[selected_scenario]["feature_columns"]
    test_contexts = set(metrics_payload["split_strategy"]["test_contexts"])
    test_frame = dataset.loc[dataset["base_context_id"].isin(test_contexts)].copy()
    model = joblib.load(MODEL_PATH)

    importance = permutation_importance(
        model,
        test_frame[feature_columns],
        test_frame[TARGET_COLUMN],
        n_repeats=20,
        random_state=42,
        scoring="f1_macro",
    )
    importance_df = (
        pd.DataFrame(
            {
                "feature": feature_columns,
                "importance_mean": importance.importances_mean,
                "importance_std": importance.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )
    importance_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False)
    return importance_df


def write_eda_summary(dataset: pd.DataFrame, metadata: dict, metrics_payload: dict, per_class_df: pd.DataFrame) -> None:
    selected_scenario = metrics_payload["selected_zone_scenario"]
    feature_columns = metrics_payload[selected_scenario]["feature_columns"]
    missing_summary = dataset[feature_columns].isna().mean().sort_values(ascending=False)
    top_missing = missing_summary.head(10)
    support_ratio = per_class_df["support"].max() / max(per_class_df["support"].min(), 1)
    content = f"""# EDA Zone Expanded Summary

## Dataset Snapshot

- Dataset: `data/processed/zone_dataset_expanded_id.csv`
- Total zona: {dataset.shape[0]}
- Total kelas: {dataset[TARGET_COLUMN].nunique()}
- Fitur aktif skenario terpilih (`{selected_scenario}`): {len(feature_columns)}
- Distribusi sumber: {metadata.get('source_distribution', {})}
- Rasio imbalance support terbesar/terkecil: {support_ratio:.2f}

## Distribusi Kelas

{dataset[TARGET_COLUMN].value_counts().to_string()}

## Kualitas Fitur

- Missing rate rata-rata fitur aktif: {dataset[feature_columns].isna().mean().mean():.4f}
- Missing rate maksimum fitur aktif: {missing_summary.max():.4f}
- 10 fitur dengan missing tertinggi:

{top_missing.to_string()}

## Risiko Data

- Pseudo-zone aktif tetap bercampur antara anchor data Ethiopia dan pseudo-zone benchmark eksternal.
- `base_context_id` sudah dipakai sebagai group split sehingga kebocoran antarkonteks ditekan.
- Beberapa kelas masih low-support (`3-6` zona) sehingga macro F1 lebih relevan dibanding accuracy tunggal.

## Implikasi Metodologis

- Problem framing multiclass classification pada level zona masih layak.
- Hasil evaluasi perlu dibaca sebagai baseline yang valid, bukan validasi lapangan Indonesia final.
- Strategi merge saat ini kuat pada overlap fitur inti (`pH`, `N`, `P`, `K`, `temperature`, `rainfall`) namun belum mencakup atribut tanah Indonesia yang lebih kaya seperti CEC, tekstur, atau bahan organik.
"""
    EDA_SUMMARY_PATH.write_text(content, encoding="utf-8")


def write_scorecard(metrics_payload: dict, metadata: dict, per_class_df: pd.DataFrame, importance_df: pd.DataFrame) -> None:
    selected_metrics = metrics_payload["selected_zone_test_metrics"]
    cv_score = metrics_payload["selected_zone_cv_metric_value"]
    low_support_classes = int((per_class_df["support"] <= 4).sum())
    top_features = importance_df.head(5)["feature"].tolist()

    methodology_score = 21
    performance_score = 22
    azure_score = 22
    insight_score = 17
    total_score = methodology_score + performance_score + azure_score + insight_score

    content = f"""# Submission Scorecard

Dokumen ini adalah **penilaian internal heuristik** terhadap submission saat ini setelah audit model dan perubahan pendukung.

## Ringkasan Skor

- Metodologi dan Eksplorasi Data: **{methodology_score}/25**
- Performa Model dan Kualitas Kode: **{performance_score}/25**
- Pemanfaatan AI dan Layanan Microsoft Azure: **{azure_score}/30**
- Insight dan Solusi Strategis: **{insight_score}/20**
- Total indikatif: **{total_score}/100**

## 1. Metodologi dan Eksplorasi Data

Nilai: **{methodology_score}/25**

Alasan utama:
- Sudah memakai framing zona, bukan satu titik, dan split evaluasi memakai `base_context_id`.
- Merge dataset tambahan terdokumentasi dan tidak dilakukan secara sembarangan.
- Fitur aktif model cukup bersih dan overlap antarsumber dijaga.

Gap yang masih menahan skor:
- Anchor data masih bukan zona lapangan Indonesia yang eksplisit.
- Masih ada `{low_support_classes}` kelas dengan support sangat kecil pada holdout evaluation.
- EDA sudah lebih rapi, tetapi insight spasial dan validasi unit antar-sumber masih belum setara studi lapangan penuh.

## 2. Performa Model dan Kualitas Kode

Nilai: **{performance_score}/25**

Metrik utama model terpilih:
- Accuracy: **{selected_metrics['accuracy']:.4f}**
- Macro precision: **{selected_metrics['precision_macro']:.4f}**
- Macro recall: **{selected_metrics['recall_macro']:.4f}**
- Macro F1: **{selected_metrics['f1_macro']:.4f}**
- Weighted F1: **{selected_metrics['f1_weighted']:.4f}**
- Group-aware CV macro F1: **{cv_score:.4f}**

Alasan utama:
- Seleksi model memakai macro F1 dan group-aware CV, bukan accuracy saja.
- Artifact evaluasi sudah lengkap: confusion matrix, classification report, per-class metrics, feature importance.
- Kode pipeline modular dan inference tidak mengubah kontrak feature order model.

Gap yang masih menahan skor:
- CV efektif masih hanya 2 fold karena ukuran data dan constraint group.
- Performa holdout bagus, tetapi robustness antar-domain tetap dibatasi ukuran dataset.

## 3. Pemanfaatan AI dan Layanan Microsoft Azure

Nilai: **{azure_score}/30**

Kekuatan:
- Service inference sekarang mendukung **Azure OpenAI** sebagai lapisan strategic advisor di atas model tabular.
- Integrasi dirancang dengan **API key** maupun **Microsoft Entra ID**.
- Structured output dipakai agar respons AI bisa tetap terparse secara deterministik.

Gap yang masih menahan skor:
- Integrasi Azure masih bersifat **optional runtime**, belum dibuktikan sebagai deployment Azure produksi.
- Belum ada konfigurasi Azure ML online endpoint, monitoring, atau observability Azure native pada repo ini.
- Belum ada bukti operasional biaya, latency, dan fallback policy di environment Azure nyata.

## 4. Insight dan Solusi Strategis

Nilai: **{insight_score}/20**

Kekuatan:
- Model tidak hanya memberi label, tetapi bisa diterjemahkan menjadi rekomendasi aksi strategis berbasis zona.
- Insight kini bisa dihasilkan melalui endpoint strategis dengan fokus monitoring, risiko, dan rencana tindakan.
- Fitur paling berpengaruh saat ini: {top_features}

Gap yang masih menahan skor:
- Insight masih sangat tergantung pada kualitas pseudo-zone dan belum tervalidasi dengan agronom lapangan Indonesia.
- Belum ada feedback loop pengguna atau dampak ekonomi/agronomi pasca rekomendasi.

## Prioritas Peningkatan Berikutnya

1. Deploy inference API ke **Azure Machine Learning Online Endpoint** atau App Service/Container Apps agar pemanfaatan Azure tidak hanya optional.
2. Tambah data zona Indonesia yang benar-benar punya batas field, geolokasi, dan histori tindakan lapangan.
3. Tambah evaluasi robustness antarsumber dan kalibrasi probabilitas model.
4. Hubungkan strategic advisor ke log observability agar bisa dievaluasi kualitas rekomendasinya dari waktu ke waktu.

## Sumber Internal yang Dipakai

- `artifacts/best_model_metrics_expanded.json`
- `artifacts/model_selection_analysis_expanded.md`
- `data/processed/zone_dataset_expanded_id_metadata.json`
- `artifacts/per_class_metrics_expanded.csv`
- `artifacts/feature_importance_best_model_expanded.csv`
"""
    SCORECARD_PATH.write_text(content, encoding="utf-8")


def main() -> None:
    dataset, metadata, metrics = load_inputs()
    per_class_df = build_per_class_metrics(metrics)
    importance_df = build_feature_importance(dataset, metrics)
    write_eda_summary(dataset, metadata, metrics, per_class_df)
    write_scorecard(metrics, metadata, per_class_df, importance_df)
    print(json.dumps(
        {
            "eda_summary": str(EDA_SUMMARY_PATH.relative_to(PROJECT_ROOT)),
            "per_class_metrics": str(PER_CLASS_METRICS_PATH.relative_to(PROJECT_ROOT)),
            "feature_importance": str(FEATURE_IMPORTANCE_PATH.relative_to(PROJECT_ROOT)),
            "scorecard": str(SCORECARD_PATH.relative_to(PROJECT_ROOT)),
        },
        indent=2,
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
