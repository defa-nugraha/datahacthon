# FastAPI Zone Inference Service

Service ini menyediakan inferensi untuk model rekomendasi vegetasi/tanaman berbasis **zona**. Client mengirim **raw point samples** dari satu zona, lalu API menghitung agregasi fitur zona secara otomatis sebelum memanggil model.

## Artifact Yang Dipakai

- Model: `artifacts/models/best_zone_model_expanded.joblib`
- Preprocessing pipeline: `artifacts/pipelines/best_zone_pipeline_expanded.joblib`
- Metrics/feature contract: `artifacts/best_model_metrics_expanded.json`
- Metadata zona: `data/processed/zone_dataset_expanded_id_metadata.json`
- Feature summary: `artifacts/zone_feature_summary_expanded.csv`

Model aktif default mengikuti artifact saat ini:

- `active_scenario`: `zone_mean_plus_variability`
- `model_name`: `extra_trees_zone_mean_plus_variability`
- `feature_set_type`: `mean_plus_variability`

## Kenapa Input API Berupa Titik Mentah

Model training saat ini bekerja pada fitur level zona, bukan satu titik. Karena itu:

1. client mengirim `samples`
2. service menghitung agregasi zona
3. service menyusun feature vector sesuai urutan training
4. service melakukan prediksi

API **tidak** memakai fitur agregasi dari client sebagai mode utama.

## Menjalankan Service

Instal dependency:

```bash
.venv/bin/pip install -r requirements-api.txt
```

Jalankan service:

```bash
.venv/bin/uvicorn app.main:app --reload
```

Dokumentasi interaktif tersedia di:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Menjalankan Dengan Docker

Build image:

```bash
docker build -t zone-inference-api .
```

Jalankan container:

```bash
docker run --rm -p 8000:8000 zone-inference-api
```

Atau gunakan Docker Compose:

```bash
docker compose up --build
```

Image Docker ini hanya membawa file yang diperlukan untuk inferensi:

- `app/`
- `scripts/`
- `artifacts/`
- `data/`
- `.env.example`
- `README_FASTAPI.md`

Folder berat yang tidak dibutuhkan untuk runtime seperti `datasets/raw`, `datasets/csv`, `notebooks`, `tests`, dan `.venv` dikecualikan lewat `.dockerignore`.

## Endpoint

### `GET /health`

Cek readiness service.

### `GET /model/info`

Mengembalikan metadata model aktif:

- `model_name`
- `model_version`
- `feature_set_type`
- `feature_columns`
- `required_raw_fields`
- `optional_raw_fields`
- `target_labels`
- threshold sample minimum

### `POST /predict/zone`

Endpoint inferensi utama.

Input:

- `zone_id`: string
- `samples`: daftar titik mentah dalam satu zona
- `top_k`: opsional, default `3`

### `POST /predict/zone/debug`

Sama seperti endpoint utama, tetapi menambahkan:

- full numeric aggregations
- full categorical aggregations
- daftar fitur model yang diimputasi

### `POST /insights/zone-strategy`

Endpoint ini menjalankan prediksi zona lalu mengubah hasilnya menjadi rekomendasi strategis yang bisa ditindaklanjuti.

Respons selalu memuat:

- hasil prediksi model zona
- urgency
- alasan utama
- daftar aksi prioritas
- fokus monitoring
- daftar risiko

Provider insight:

- `azure_openai` jika Azure OpenAI aktif dan berhasil
- `local_fallback` jika Azure tidak aktif atau gagal

## Request Schema

Top-level:

- `zone_id`: wajib
- `samples`: wajib
- `top_k`: opsional
- `current_crop`: opsional, khusus endpoint strategis
- `time_horizon_days`: opsional, khusus endpoint strategis

Setiap elemen `samples`:

- `point_id`: wajib, unik dalam satu request
- `ph`: wajib
- `nitrogen`: wajib
- `phosphorus`: wajib
- `potassium`: wajib
- `zinc`: opsional
- `sulfur`: opsional
- `soil_color`: opsional
- `soil_moisture_surface`: opsional
- `wind_speed_10m`: opsional
- `specific_humidity_mean`: opsional
- `temperature_mean`: opsional
- `temperature_seasonal_range`: opsional
- `rainfall_mean`: opsional
- `rainfall_total_proxy`: opsional
- `cloud_amount`: opsional
- `surface_pressure`: opsional

Aturan penamaan fitur input:

- gunakan **snake_case**
- jangan kirim alias seperti `N`, `P`, `K`, `Ph`, atau `soilColor`

## Aturan Minimum Sample

Service memakai dua threshold:

- minimum keras untuk menerima request: `3`
- minimum yang direkomendasikan sesuai artifact training: `8`

Perilaku:

- `< 3` sample: request ditolak `400`
- `3-7` sample: prediksi tetap jalan, tetapi response berisi warning
- `>= 8` sample: sesuai threshold training

## Aturan Agregasi

Service menghitung agregasi internal per fitur numerik:

- `mean`
- `std`
- `min`
- `max`
- `median`
- `count`
- `range`
- `cv`
- `missing_ratio`

Namun, karena model aktif saat ini adalah `zone_mean_plus_variability`, API mengirim fitur berikut ke pipeline:

- `sample_count`
- `context_sample_count`
- `context_cluster_count`
- semua agregasi `ph_*`
- semua agregasi `nitrogen_*`
- semua agregasi `phosphorus_*`
- semua agregasi `potassium_*`
- semua agregasi `temperature_mean_*`
- semua agregasi `rainfall_mean_*`

Secara total, model aktif memakai `57` feature columns.

## Asumsi Penting Inferensi

Karena request client hanya mewakili satu zona siap prediksi:

- `sample_count` dihitung dari jumlah `samples`
- `context_sample_count` diaproksimasi sebagai `sample_count`
- `context_cluster_count` di-set `1`

Jika fitur opsional seperti iklim atau `soil_color` tidak diberikan:

- service tetap berjalan
- feature terkait dibiarkan missing
- preprocessing pipeline akan mengimputasi nilai tersebut
- response akan mengembalikan warning

## Azure OpenAI

Service ini mendukung integrasi **Azure OpenAI** untuk menghasilkan strategic insight di atas hasil model tabular.

Konfigurasi environment:

```bash
AZURE_OPENAI_ENABLED=true
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE-NAME.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=YOUR_MODEL_DEPLOYMENT_NAME
AZURE_OPENAI_API_KEY=...
```

Atau gunakan Microsoft Entra ID:

```bash
AZURE_OPENAI_ENABLED=true
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE-NAME.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=YOUR_MODEL_DEPLOYMENT_NAME
AZURE_OPENAI_USE_ENTRA_ID=true
```

Catatan implementasi:

- endpoint strategis memakai structured output agar respons tetap ter-parse ke schema yang konsisten
- jika kredensial atau deployment Azure belum siap, service otomatis turun ke fallback lokal
- model klasifikasi inti tidak berubah; Azure hanya dipakai untuk lapisan reasoning dan recommendation

## Contoh Request Sukses

```bash
curl -X POST "http://127.0.0.1:8000/predict/zone" \
  -H "Content-Type: application/json" \
  -d '{
    "zone_id": "zona_a",
    "top_k": 3,
    "samples": [
      {"point_id": "A1", "ph": 6.5, "nitrogen": 100, "phosphorus": 40, "potassium": 70, "zinc": 1.2, "sulfur": 10},
      {"point_id": "A2", "ph": 6.4, "nitrogen": 102, "phosphorus": 39, "potassium": 68, "zinc": 1.1, "sulfur": 11},
      {"point_id": "A3", "ph": 6.6, "nitrogen": 98, "phosphorus": 41, "potassium": 72, "zinc": 1.2, "sulfur": 9},
      {"point_id": "A4", "ph": 6.5, "nitrogen": 101, "phosphorus": 40, "potassium": 71, "zinc": 1.3, "sulfur": 10},
      {"point_id": "A5", "ph": 6.3, "nitrogen": 99, "phosphorus": 38, "potassium": 69, "zinc": 1.1, "sulfur": 10},
      {"point_id": "A6", "ph": 6.4, "nitrogen": 100, "phosphorus": 39, "potassium": 70, "zinc": 1.2, "sulfur": 11},
      {"point_id": "A7", "ph": 6.5, "nitrogen": 103, "phosphorus": 42, "potassium": 73, "zinc": 1.3, "sulfur": 10},
      {"point_id": "A8", "ph": 6.4, "nitrogen": 97, "phosphorus": 37, "potassium": 67, "zinc": 1.0, "sulfur": 9}
    ]
  }'
```

## Contoh Response Sukses

```json
{
  "status": "success",
  "zone_id": "zona_a",
  "sample_count": 8,
  "aggregated_features": {
    "sample_count": 8,
    "context_sample_count": 8,
    "context_cluster_count": 1,
    "soil_color_mode": null,
    "soil_color_dominant_ratio": 0.0,
    "ph_mean": 6.45,
    "nitrogen_mean": 100.0
  },
  "prediction": {
    "recommended_label": "Wheat",
    "confidence": 0.3167,
    "top_k": [
      {"label": "Wheat", "probability": 0.3167},
      {"label": "Maize", "probability": 0.3083},
      {"label": "Teff", "probability": 0.2083}
    ]
  },
  "model_info": {
    "model_name": "extra_trees_zone_mean_plus_variability",
    "feature_set_type": "mean_plus_variability",
    "active_scenario": "zone_mean_plus_variability"
  },
  "warnings": [
    "context_sample_count is not derivable from request payload and was approximated with sample_count."
  ]
}
```

## Contoh Strategic Insight

```bash
curl -X POST "http://127.0.0.1:8000/insights/zone-strategy" \
  -H "Content-Type: application/json" \
  -d '{
    "zone_id": "zona_strategi_a",
    "current_crop": "Jagung",
    "time_horizon_days": 14,
    "top_k": 3,
    "samples": [
      {"point_id": "A1", "ph": 6.5, "nitrogen": 100, "phosphorus": 40, "potassium": 70, "temperature_mean": 19.3, "rainfall_mean": 6.2},
      {"point_id": "A2", "ph": 6.4, "nitrogen": 102, "phosphorus": 39, "potassium": 68, "temperature_mean": 19.1, "rainfall_mean": 6.1},
      {"point_id": "A3", "ph": 6.6, "nitrogen": 98, "phosphorus": 41, "potassium": 72, "temperature_mean": 19.4, "rainfall_mean": 6.3}
    ]
  }'
```

## Contoh Error: Sample Terlalu Sedikit

```json
{
  "status": "error",
  "error": {
    "code": "business_validation_error",
    "message": "sample_count is below the minimum accepted threshold for zone inference.",
    "details": {
      "sample_count": 2,
      "minimum_samples_required": 3
    }
  }
}
```

## Contoh Error: Field Wajib Hilang

```json
{
  "status": "error",
  "error": {
    "code": "request_validation_error",
    "message": "Request validation failed.",
    "details": [
      {
        "location": "body.samples.0.phosphorus",
        "message": "Field required",
        "type": "missing"
      }
    ]
  }
}
```

## Menjalankan Test

```bash
.venv/bin/pytest -q
```

## Struktur Kode

- `app/main.py`: entry FastAPI
- `app/schemas.py`: request/response schema
- `app/core/config.py`: konfigurasi dan path artifact
- `app/core/exceptions.py`: custom exception dan handler
- `app/services/model_loader.py`: load artifact model dan metadata
- `app/services/feature_engineering.py`: agregasi raw points ke feature zona
- `app/services/predictor.py`: orchestration inferensi
- `tests/test_api.py`: test dasar kontrak service
