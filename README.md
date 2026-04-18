# DATAHACTHON Zone-Based Pipeline

Project ini sekarang difokuskan hanya pada **pipeline rekomendasi vegetasi/tanaman berbasis zona**.

Komponen aktif:

- dataset proses zona di `data/processed/zone_*`
- artifact model zona di `artifacts/zone_*`
- model API default di `artifacts/models/best_zone_model_expanded.joblib`
- preprocessing API default di `artifacts/pipelines/best_zone_pipeline_expanded.joblib`
- notebook aktif di `notebooks/zone_based_vegetation_recommendation.ipynb`
- API inferensi zona di `app/`
- script pipeline zona di `scripts/build_zone_dataset.py`, `scripts/train_zone_model.py`, `scripts/prepare_zone_dataset_expanded.py`, dan `scripts/train_zone_model_expanded.py`

Source dataset aktif:

- `datasets/csv/mendeley_8v757rr4st_crop_recommendation_soil_weather.csv`

File dan artifact dari pipeline sebelum sistem zona dipindahkan ke:

- `archive/legacy_pre_zone/`

Dokumentasi API:

- [README_FASTAPI.md](README_FASTAPI.md)
