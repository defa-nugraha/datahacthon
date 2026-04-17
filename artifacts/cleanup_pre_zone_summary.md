# Cleanup Pre-Zone Summary

## Tujuan

Membersihkan project dari dataset, code, notebook, artifact, dan referensi lama yang berasal dari pipeline sebelum sistem zona dipakai, tanpa merusak pipeline zona aktif.

## File/Folder Yang Dipindahkan Ke Archive

Semua file legacy dipindahkan ke `archive/legacy_pre_zone/` agar masih bisa diaudit bila diperlukan.

### Data Processed Legacy

- `data/processed/final_dataset.csv`
- `data/processed/final_dataset_minimal.csv`
- `data/processed/final_dataset_extended.csv`
- `data/processed/final_dataset_metadata.json`

### Artifact Legacy

- `artifacts/dataset_audit_summary.csv`
- `artifacts/dataset_schema_report.md`
- `artifacts/feature_importance.csv`
- `artifacts/model_metrics.json`
- `artifacts/modeling_strategy.md`
- `artifacts/prediction_samples.csv`
- `artifacts/models/best_model.joblib`
- `artifacts/pipelines/preprocessing_pipeline.joblib`

### Notebook Legacy

- `notebooks/vegetation_recommendation_model.ipynb`

### Script Legacy

- `scripts/data_preparation.py`
- `scripts/generate_notebook.py`
- `scripts/inference.py`
- `scripts/train_model.py`

### Dataset dan Referensi Non-Aktif

Dipindahkan ke archive untuk mengurangi clutter project aktif:

- seluruh `datasets/raw/*`
- seluruh `datasets/csv/*` kecuali `datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`
- `datasets/dataset_sources.csv`
- `datasets/papers_summary.csv`

## File/Folder Yang Dipertahankan

### Pipeline Zona Aktif

- `scripts/common.py`
- `scripts/zone_utils.py`
- `scripts/build_zone_dataset.py`
- `scripts/train_zone_model.py`
- `scripts/generate_zone_notebook.py`

### Data dan Artifact Zona Aktif

- `data/processed/zone_dataset.csv`
- `data/processed/zone_dataset_minimal.csv`
- `data/processed/zone_dataset_extended.csv`
- `data/processed/zone_dataset_metadata.json`
- `artifacts/zone_modeling_strategy.md`
- `artifacts/zone_feature_summary.csv`
- `artifacts/zone_model_metrics.json`
- `artifacts/zone_feature_importance.csv`
- `artifacts/zone_prediction_samples.csv`
- `artifacts/models/best_zone_model.joblib`
- `artifacts/pipelines/zone_preprocessing_pipeline.joblib`

### API dan Testing Aktif

- `app/`
- `tests/`
- `README_FASTAPI.md`
- `README.md`
- `.env.example`
- `requirements-api.txt`
- `Dockerfile`
- `docker-compose.yml`

### Source Dataset Aktif

- `datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`

## File/Folder Yang Dihapus

Penghapusan permanen hanya dilakukan untuk cache/generated runtime yang aman di-regenerate:

- seluruh `__pycache__/`
- cache pytest lama

## Referensi/Path Yang Diperbarui

### Import Yang Diubah

- `scripts/build_zone_dataset.py`
  - dari `scripts.data_preparation` menjadi `scripts.zone_utils`
- `app/services/feature_engineering.py`
  - dari `scripts.data_preparation` menjadi `scripts.zone_utils`

### Refactor Pendukung

- ditambahkan `scripts/zone_utils.py` untuk mengekstrak util normalisasi yang masih dipakai sistem zona
- `scripts/common.py` dipangkas agar tidak lagi memuat konstanta point-based legacy
- ditambahkan `README.md` root yang hanya menjelaskan pipeline zona aktif
- `.dockerignore` diperbarui untuk mengecualikan `archive/`

## Alasan Utama Cleanup

- menghilangkan ambiguitas antara pipeline point-based lama dan pipeline zone-based aktif
- menyederhanakan struktur project agar source of truth hanya ada pada artifact dan script zona
- mengurangi risiko salah load dataset/model/artifact lama
- menjaga file lama tetap tersedia melalui archive, bukan delete membabi buta

## File Ambigu Yang Sengaja Dipertahankan

- `scripts/train_zone_model.py` masih memuat evaluasi `point_to_zone_baseline`
  - alasan: ini bagian dari eksperimen pembanding dalam pipeline zona saat ini, bukan script training point-based lama yang berdiri sendiri
- `datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`
  - alasan: ini masih menjadi source dataset aktif untuk membangun zone dataset

## Validasi Pasca Cleanup

Berhasil dijalankan ulang setelah cleanup:

- `python scripts/build_zone_dataset.py`
- `python scripts/train_zone_model.py`
- `python scripts/generate_zone_notebook.py`
- `pytest -q`
- eksekusi notebook `notebooks/zone_based_vegetation_recommendation.ipynb`

## Catatan Risiko

- archive masih menyimpan dataset dan artifact lama dalam jumlah besar; ini disengaja untuk auditability
- API inferensi dan notebook aktif sekarang sepenuhnya mengarah ke artifact zona, tetapi archive tetap dapat membingungkan bila dipakai manual tanpa konteks
- commit git tidak dibuat karena workspace ini tidak terdeteksi sebagai repository git yang valid saat cleanup dilakukan
