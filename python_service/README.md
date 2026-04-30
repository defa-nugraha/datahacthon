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

## Konfigurasi Azure OpenAI

Primary path untuk `POST /advice/care` menggunakan Azure OpenAI. Jika konfigurasi Azure belum tersedia, service otomatis fallback ke advice lokal berbasis rule agar UI Laravel tetap dapat dirender dan diuji.

Environment yang dipakai:

```bash
AZURE_OPENAI_ENABLED=true
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_TEMPERATURE=0.2
AZURE_OPENAI_MAX_OUTPUT_TOKENS=900
```

Jika ingin memakai Entra ID, set:

```bash
AZURE_OPENAI_USE_ENTRA_ID=true
```

Dalam mode Entra ID, container/host harus memiliki credential Azure yang valid.

## Contoh request advice

```bash
curl -X POST http://127.0.0.1:8001/advice/care \
  -H "Content-Type: application/json" \
  -d '{
    "zone_id": "1",
    "zone_name": "Zona A",
    "current_crop": "Jagung",
    "history_window_minutes": 60,
    "nutrient_history": [
      {"timestamp": "2026-04-30T08:00:00+07:00", "ph": 6.1, "nitrogen": 82, "phosphorus": 19, "potassium": 78, "soil_moisture": 28},
      {"timestamp": "2026-04-30T08:30:00+07:00", "ph": 6.0, "nitrogen": 80, "phosphorus": 18, "potassium": 76, "soil_moisture": 26}
    ],
    "threshold_context": {
      "trigger_reason": "critical_low_phosphorus"
    }
  }'
```

Response berisi `summary`, `urgency`, daftar `recommendations`, `observation_focus`, `risk_flags`, dan `provider`.
