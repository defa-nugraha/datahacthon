# DATAHACTHON Expanded Zone-Based Pipeline

Project ini difokuskan pada **pipeline rekomendasi vegetasi/tanaman berbasis zona** untuk kebutuhan penilaian model, API inferensi, dan insight strategis.

Komponen aktif:

- dataset model aktif di `data/processed/zone_dataset_expanded_id.csv`
- metadata model aktif di `data/processed/zone_dataset_expanded_id_metadata.json`
- model API default di `artifacts/models/best_zone_model_expanded.joblib`
- preprocessing API default di `artifacts/pipelines/best_zone_pipeline_expanded.joblib`
- notebook penilaian aktif di `notebooks/zone_model_submission_assessment.ipynb`
- API inferensi zona di `app/`
- script pipeline zona di `scripts/prepare_zone_dataset_expanded.py`, `scripts/train_zone_model_expanded.py`, `scripts/assess_zone_submission.py`, dan `scripts/generate_submission_notebook.py`

Source dataset aktif:

- `datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`
- `datasets/csv/crop_recommendation_kaggle_mirror.csv`

Dokumentasi API:

- [README_FASTAPI.md](README_FASTAPI.md)

Artifact evaluasi submission:

- `artifacts/eda_zone_expanded.md`
- `artifacts/per_class_metrics_expanded.csv`
- `artifacts/feature_importance_best_model_expanded.csv`
- `artifacts/submission_scorecard.md`

Model aktif:

- model: `ExtraTrees`
- scenario: `zone_mean_plus_variability`
- accuracy: `0.8750`
- macro F1: `0.8308`
