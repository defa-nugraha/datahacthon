# Main Branch Cleanup Summary

Cleanup ini memfokuskan branch `main` pada pipeline model zona expanded yang dipakai untuk penilaian saat ini.

## Dipertahankan

- API FastAPI di `app/`
- tests API di `tests/`
- dataset expanded aktif di `data/processed/zone_dataset_expanded_id.csv`
- metadata expanded aktif di `data/processed/zone_dataset_expanded_id_metadata.json`
- model aktif di `artifacts/models/best_zone_model_expanded.joblib`
- pipeline aktif di `artifacts/pipelines/best_zone_pipeline_expanded.joblib`
- notebook penilaian di `notebooks/zone_model_submission_assessment.ipynb`
- artefak penilaian expanded seperti `submission_scorecard.md`, `eda_zone_expanded.md`, `per_class_metrics_expanded.csv`, dan `feature_importance_best_model_expanded.csv`

## Dihapus

- archive legacy pre-zone
- cache Python, cache Laravel, log runtime, dan SQLite lokal
- output training CatBoost lokal
- model dan artifact lama non-expanded
- notebook lama yang bukan notebook penilaian aktif
- script generator notebook lama dan script training label Indonesia intermediate

## Alasan

- Mengurangi noise branch `main`
- Menjaga fokus pada kriteria penilaian: EDA, kualitas model, Azure/AI, dan insight strategis
- Memastikan API dan notebook hanya mengarah ke model expanded yang sedang dipakai

## Catatan Risiko

- Dataset expanded masih menyimpan jejak provenance kandidat dataset lama dalam metadata dan screening artifact karena itu bagian dari audit ekspansi data.
- Script helper lama `build_zone_dataset.py` dan `train_zone_model.py` tetap dipertahankan karena masih menyediakan fungsi yang diimpor oleh pipeline expanded.
