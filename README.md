# Vera AI

Vera AI adalah sistem rekomendasi vegetasi/tanaman berbasis zona lahan. Aplikasi menerima beberapa titik sampling tanah dalam satu zona, mengagregasi variasi internal zona, lalu menghasilkan rekomendasi tanaman dan saran penanganan berbasis kondisi unsur hara.

## Struktur Project

```text
DATAHACTHON/
├── API/        # FastAPI service untuk model zona dan AI advisory
├── INTERFACE/  # Laravel web app untuk petani/admin
└── docker-compose.yml
```

## Komponen Utama

- `API`: inference service berbasis FastAPI untuk rekomendasi tanaman zona dan saran penanganan.
- `INTERFACE`: dashboard Laravel untuk manajemen zona, input sampling, hasil rekomendasi, monitoring, dan admin.
- `docker-compose.yml`: stack lokal untuk menjalankan API, PHP-FPM, Nginx, Vite, queue, dan scheduler.

## Model Aktif

- Dataset aktif: `API/data/processed/zone_dataset_expanded_id.csv`
- Model aktif: `API/artifacts/models/best_zone_model_expanded.joblib`
- Pipeline aktif: `API/artifacts/pipelines/best_zone_pipeline_expanded.joblib`
- Problem framing: klasifikasi tanaman berbasis representasi zona.
- Pendekatan fitur: agregasi zona dari banyak titik sampling, termasuk mean dan fitur variasi seperti std/min/max/range/count.

## Menjalankan Lokal Dengan Docker

```bash
APP_PORT=8080 API_PORT=8002 docker compose up -d --build app web api
```

Laravel:

```text
http://127.0.0.1:8080
```

FastAPI:

```text
http://127.0.0.1:8002/docs
```

Credential demo setelah seeder berjalan:

```text
Admin:  admin@veraai.test / password
Petani: petani@veraai.test / password
```

## Endpoint API Penting

- `GET /health`
- `GET /model/info`
- `POST /predict/zone`
- `POST /predict/zone/debug`
- `POST /advice/care`
- `POST /insights/zone-strategy`

## Catatan Final Round

Project ini sudah melewati tahap prototype dan diarahkan menjadi solusi demo yang reproducible. Fokus penyempurnaan berikutnya adalah kestabilan deployment Azure, validasi end-to-end, dokumentasi kontrak API, observability sederhana, dan transparansi keterbatasan model.
