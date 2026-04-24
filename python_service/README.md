# Python AI Service

Service ini menyediakan dua endpoint utama:

- `POST /predict/zone` untuk rekomendasi tanaman berbasis multi-point sampling per zona.
- `POST /advice/care` untuk rekomendasi penanganan tanaman aktif berbasis histori unsur hara 1 jam terakhir.

## Menjalankan lokal

```bash
python3 -m venv .venv-ai
source .venv-ai/bin/activate
pip install -r python_service/requirements.txt
uvicorn python_service.main:app --host 0.0.0.0 --port 8001
```

## Menjalankan via Docker Compose

```bash
docker compose --env-file .env.docker up -d ai
```

## Konfigurasi Vertex AI

Primary path untuk `POST /advice/care` menggunakan Vertex AI melalui Google Gen AI SDK.

Environment yang dipakai:

```bash
VERTEX_AI_ENABLED=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
VERTEX_MODEL=gemini-2.5-flash
```

Opsional untuk express-mode/testing:

```bash
VERTEX_API_KEY=your-vertex-api-key
```

Jika konfigurasi Vertex AI belum tersedia, service akan otomatis fallback ke advice lokal berbasis rule agar UI Laravel tetap dapat dirender dan diuji.
