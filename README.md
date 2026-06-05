# Vera AI

Vera AI adalah aplikasi rekomendasi vegetasi berbasis zona lahan. Sistem menerima beberapa titik sampling tanah dari satu zona, menghitung agregasi zona, menjalankan model klasifikasi tanaman, lalu menampilkan rekomendasi tanaman, monitoring sensor, informasi cuaca, notifikasi batas aman, dan saran penanganan tanaman.

## Struktur Project

```text
DATAHACTHON/
├── API/              # FastAPI untuk inference model, forecast, dan AI advice
├── INTERFACE/        # Laravel UI untuk petani dan admin
├── docker-compose.yml
└── README.md
```

Folder `docs/` hanya dipakai sebagai dokumen lokal dan tidak disimpan ke GitHub.

## Komponen Sistem

- `INTERFACE`: dashboard Laravel untuk login, manajemen zona, sampling tanah, device, monitoring realtime, rekomendasi vegetasi, notifikasi, dan saran penanganan tanaman.
- `API`: service FastAPI untuk prediksi vegetasi berbasis zona, strategi zona, AI adaptive advice, dan forecast cuaca berbasis artifact ARIMA.
- `MQTT`: digunakan untuk menerima telemetry sensor dari device per zona. Data realtime bisa dibaca langsung dari broker; penyimpanan historis bersifat konfigurabel.
- `BMKG Weather`: digunakan pada halaman monitoring untuk cuaca saat ini dan prediksi 3 hari berdasarkan kode wilayah BMKG.
- `Azure OpenAI`: digunakan untuk membuat saran penanganan tanaman. Jika tidak dikonfigurasi, API memakai fallback lokal agar demo tetap berjalan.
- `SQLite`: database default untuk deployment sederhana dan demo Azure tanpa layanan database terpisah.

## Model Aktif

- Dataset aktif: `API/data/processed/zone_dataset_expanded_id.csv`
- Model aktif: `API/artifacts/models/best_zone_model_expanded.joblib`
- Pipeline aktif: `API/artifacts/pipelines/best_zone_pipeline_expanded.joblib`
- Framing: klasifikasi tanaman berbasis zona.
- Input model: fitur agregasi dari banyak titik sampling, bukan satu titik sensor.
- Fitur zona: `mean`, `std`, `min`, `max`, `range`, `median`, `count`, dan fitur variasi lain sesuai kontrak training.

## Alur Utama

1. Petani atau admin membuat zona lahan dan menghubungkan device sensor jika tersedia.
2. Sampling tanah dimasukkan manual atau disinkronkan dari device.
3. Laravel mengirim raw samples ke FastAPI melalui `POST /predict/zone`.
4. FastAPI menghitung agregasi zona dan menjalankan model rekomendasi.
5. Petani memilih tanaman rekomendasi sebagai tanaman aktif.
6. Monitoring zona membaca telemetry MQTT, cuaca BMKG, dan batas aman unsur hara.
7. Sistem mengirim konteks tanah, tanaman aktif, threshold, dan cuaca ke endpoint AI advice jika perubahan kondisi melewati ambang yang ditentukan.

## Menjalankan Lokal Dengan Docker

Jalankan stack utama:

```bash
APP_PORT=8080 API_PORT=8002 docker compose up -d --build app web api
```

Jalankan worker tambahan jika perlu queue, scheduler, atau MQTT subscriber:

```bash
docker compose --profile workers --profile mqtt up -d --build
```

Akses aplikasi:

```text
Laravel UI : http://127.0.0.1:8080
FastAPI   : http://127.0.0.1:8002/docs
```

Credential seeder:

```text
Admin  : admin@veraai.test / password
Petani : petani@veraai.test / password
```

## Konfigurasi Penting

Environment dapat diberikan melalui shell atau file `.env` lokal. File `.env` tidak disimpan ke GitHub.

```text
APP_PORT=8080
API_PORT=8002
DB_CONNECTION=sqlite
DB_DATABASE=/var/www/html/database/database.sqlite
RUN_MIGRATIONS=true
RUN_SEEDERS=true
AI_ADVISOR_BASE_URL=http://api:8000
AZURE_OPENAI_ENABLED=false
BMKG_WEATHER_DEFAULT_ADM4=31.71.01.1001
AZURE_IOT_LIVE_BUFFER_LIMIT=120
AZURE_IOT_PERSIST_TELEMETRY=false
```

Untuk Azure OpenAI, isi:

```text
AZURE_OPENAI_ENABLED=true
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Endpoint API Penting

- `GET /health`: status service API dan model.
- `GET /model/info`: kontrak fitur dan metadata model aktif.
- `POST /predict/zone`: prediksi rekomendasi tanaman dari raw samples zona.
- `POST /predict/zone/debug`: prediksi dengan detail agregasi fitur.
- `POST /advice/care`: saran penanganan tanaman berdasarkan history unsur hara, threshold, tanaman aktif, dan cuaca.
- `POST /insights/zone-strategy`: insight strategis berbasis hasil prediksi zona.
- `POST /forecast/weather`: forecast suhu bulanan dari artifact ARIMA pendukung.

## Device dan MQTT

Device didaftarkan dari menu Device Management di Laravel. Setiap device menyimpan konfigurasi koneksi MQTT, termasuk host, port, TLS, client id, username, password, dan topic telemetry.

Format payload telemetry yang diterima:

```json
{
  "zone_slug": "zona-utara",
  "point_id": "Titik-1",
  "client_id": "sensor-zona-utara-01",
  "ph": 6.4,
  "nitrogen": 100,
  "phosphorus": 42,
  "potassium": 80,
  "soil_moisture": 55
}
```

## Deployment Azure

Stack ini dapat dideploy sebagai dua container utama:

- Laravel container untuk UI.
- FastAPI container untuk model service.

Database tetap SQLite, sehingga tidak wajib memakai Azure Database. Pastikan volume/container storage cukup untuk file SQLite, log, cache, dan upload runtime. Untuk deployment production jangka panjang, gunakan persistent storage agar database tidak hilang saat revision/container dibuat ulang.

## Catatan Teknis

- Jangan mengirim satu titik sensor langsung ke model. API utama menerima daftar titik mentah lalu menghitung representasi zona.
- Prediksi cuaca ARIMA di API masih pendukung dan belum spasial; BMKG 3 hari tetap menjadi konteks cuaca utama untuk monitoring dan advice harian.
- Model rekomendasi perlu retraining jika fitur cuaca historis ingin dijadikan fitur training utama, bukan hanya konteks advice.
