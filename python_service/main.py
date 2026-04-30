from __future__ import annotations

import json
import logging
import os
from statistics import mean, median, pstdev
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

try:
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency at runtime
    DefaultAzureCredential = None
    get_bearer_token_provider = None
    OpenAI = None


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vera-ai-service")

app = FastAPI(title="Vera AI Service", version="1.0.0")


class ZoneSample(BaseModel):
    point_id: str = Field(..., min_length=1)
    ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    soil_moisture: float | None = None
    sampled_at: str | None = None

    @field_validator("ph", "nitrogen", "phosphorus", "potassium", "soil_moisture")
    @classmethod
    def validate_numbers(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("Nilai harus berupa angka yang valid.")
        return value


class ZonePredictRequest(BaseModel):
    zone_id: str
    zone_name: str | None = None
    current_crop: str | None = None
    samples: list[ZoneSample] = Field(..., min_length=1)


class LegacyPredictRequest(BaseModel):
    ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    soil_moisture: float | None = None


class NutrientHistoryPoint(BaseModel):
    timestamp: str | None = None
    ph: float
    nitrogen: float
    phosphorus: float
    potassium: float
    soil_moisture: float | None = None


class CareAdviceRequest(BaseModel):
    zone_id: str
    zone_name: str | None = None
    current_crop: str = Field(..., min_length=1)
    history_window_minutes: int = Field(default=60, ge=15, le=360)
    nutrient_history: list[NutrientHistoryPoint] = Field(..., min_length=1)
    current_snapshot: dict[str, Any] | None = None
    threshold_context: dict[str, Any] | None = None


class CareRecommendationSchema(BaseModel):
    title: str
    detail: str
    priority: str = Field(..., pattern="^(low|medium|high)$")
    timing_hours: float


class CareAdviceSchema(BaseModel):
    summary: str
    urgency: str = Field(..., pattern="^(low|medium|high)$")
    recommendations: list[CareRecommendationSchema]
    observation_focus: list[str]
    risk_flags: list[str]


def aggregate_metric(values: list[float]) -> dict[str, float]:
    if not values:
        return {
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "median": 0.0,
            "count": 0,
            "range": 0.0,
        }

    std = pstdev(values) if len(values) > 1 else 0.0
    return {
        "mean": round(mean(values), 2),
        "std": round(std, 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "median": round(median(values), 2),
        "count": len(values),
        "range": round(max(values) - min(values), 2),
    }


def aggregate_zone_samples(samples: list[ZoneSample | NutrientHistoryPoint]) -> dict[str, Any]:
    metrics = {
        "ph": [sample.ph for sample in samples],
        "nitrogen": [sample.nitrogen for sample in samples],
        "phosphorus": [sample.phosphorus for sample in samples],
        "potassium": [sample.potassium for sample in samples],
        "soil_moisture": [sample.soil_moisture for sample in samples if sample.soil_moisture is not None],
    }
    aggregated = {f"{metric}_stats": aggregate_metric(values) for metric, values in metrics.items()}
    aggregated["sample_count"] = len(samples)
    return aggregated


def score_crop(profile: dict[str, Any], aggregated: dict[str, Any]) -> float:
    ph = aggregated["ph_stats"]["mean"]
    nitrogen = aggregated["nitrogen_stats"]["mean"]
    phosphorus = aggregated["phosphorus_stats"]["mean"]
    potassium = aggregated["potassium_stats"]["mean"]
    moisture = aggregated["soil_moisture_stats"]["mean"] or profile["moisture"]

    distance = (
        abs(profile["ph"] - ph) * 12
        + abs(profile["nitrogen"] - nitrogen) / 6
        + abs(profile["phosphorus"] - phosphorus) / 4
        + abs(profile["potassium"] - potassium) / 6
        + abs(profile["moisture"] - moisture) / 5
    )
    return max(0.18, 1 - min(distance / 35, 0.82))


def build_crop_prediction(aggregated: dict[str, Any], current_crop: str | None) -> dict[str, Any]:
    crop_profiles = [
        {
            "label": "Jagung",
            "ph": 6.4,
            "nitrogen": 100,
            "phosphorus": 40,
            "potassium": 82,
            "moisture": 38,
            "water_need": "Sedang",
            "harvest_time_days": 95,
            "risk_factor": "Rendah",
        },
        {
            "label": "Padi",
            "ph": 6.2,
            "nitrogen": 108,
            "phosphorus": 44,
            "potassium": 86,
            "moisture": 55,
            "water_need": "Tinggi",
            "harvest_time_days": 110,
            "risk_factor": "Sedang",
        },
        {
            "label": "Kedelai",
            "ph": 6.5,
            "nitrogen": 78,
            "phosphorus": 38,
            "potassium": 72,
            "moisture": 35,
            "water_need": "Sedang",
            "harvest_time_days": 85,
            "risk_factor": "Sedang",
        },
        {
            "label": "Cabai",
            "ph": 6.3,
            "nitrogen": 88,
            "phosphorus": 34,
            "potassium": 90,
            "moisture": 36,
            "water_need": "Sedang",
            "harvest_time_days": 105,
            "risk_factor": "Menengah",
        },
        {
            "label": "Bawang Merah",
            "ph": 6.1,
            "nitrogen": 82,
            "phosphorus": 30,
            "potassium": 94,
            "moisture": 32,
            "water_need": "Sedang",
            "harvest_time_days": 75,
            "risk_factor": "Menengah",
        },
    ]

    scored = []
    for profile in crop_profiles:
        score = score_crop(profile, aggregated)
        reasoning = (
            f"pH {aggregated['ph_stats']['mean']} dan rasio NPK zona "
            f"{aggregated['nitrogen_stats']['mean']}/{aggregated['phosphorus_stats']['mean']}/{aggregated['potassium_stats']['mean']} "
            f"paling dekat dengan pola {profile['label']}."
        )
        scored.append(
            {
                "label": profile["label"],
                "probability": round(score, 4),
                "reasoning": reasoning,
                "water_need": profile["water_need"],
                "harvest_time_days": profile["harvest_time_days"],
                "risk_factor": profile["risk_factor"] if current_crop != profile["label"] else "Sangat rendah",
                "suitability_score": round(score * 100, 1),
            }
        )

    scored.sort(key=lambda item: item["probability"], reverse=True)
    primary = scored[0]
    return {
        "recommended_label": primary["label"],
        "confidence": primary["probability"],
        "reasoning": primary["reasoning"],
        "water_need": primary["water_need"],
        "harvest_time_days": primary["harvest_time_days"],
        "risk_factor": primary["risk_factor"],
        "suitability_score": primary["suitability_score"],
        "top_k": [
            {"label": item["label"], "probability": item["probability"]}
            for item in scored[:5]
        ],
    }


def fallback_care_advice(payload: CareAdviceRequest, reason: str | None = None) -> dict[str, Any]:
    aggregated = aggregate_zone_samples(payload.nutrient_history)
    recommendations: list[dict[str, Any]] = []
    urgency = "medium"
    observation_focus: list[str] = []
    risk_flags: list[str] = []

    if aggregated["soil_moisture_stats"]["count"] and aggregated["soil_moisture_stats"]["mean"] < 30:
        recommendations.append(
            {
                "title": "Aktifkan irigasi bertahap",
                "detail": "Kelembapan rata-rata 1 jam terakhir berada di bawah rentang aman. Jalankan irigasi ringan 10-15 menit, lalu ukur ulang.",
                "priority": "high",
                "timing_hours": 0,
            }
        )
        observation_focus.append("Pantau rebound kelembapan 30-60 menit setelah irigasi.")
        risk_flags.append("Kelembapan rendah")
        urgency = "high"

    if aggregated["ph_stats"]["mean"] < 6:
        recommendations.append(
            {
                "title": "Evaluasi pengapuran korektif",
                "detail": "pH cenderung asam. Pertimbangkan intervensi bertahap agar penyerapan fosfor dan akar tetap optimal.",
                "priority": "medium",
                "timing_hours": 24,
            }
        )
        observation_focus.append("Amati gejala daun pucat dan akar lemah.")

    if aggregated["phosphorus_stats"]["mean"] < 20:
        recommendations.append(
            {
                "title": "Prioritaskan suplai fosfor",
                "detail": f"Fosfor rendah untuk tanaman {payload.current_crop}. Sesuaikan pemupukan susulan dengan fase tumbuh saat ini.",
                "priority": "high",
                "timing_hours": 12,
            }
        )
        risk_flags.append("Fosfor rendah")
        urgency = "high"

    if aggregated["nitrogen_stats"]["mean"] < 80:
        recommendations.append(
            {
                "title": "Tinjau kebutuhan nitrogen",
                "detail": "Nitrogen relatif rendah. Evaluasi dosis pupuk dan potensi kehilangan karena pencucian.",
                "priority": "medium",
                "timing_hours": 12,
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "title": "Pertahankan monitoring rutin",
                "detail": "Profil hara 1 jam terakhir relatif stabil. Fokus pada konsistensi irigasi dan inspeksi visual tanaman.",
                "priority": "low",
                "timing_hours": 24,
            }
        )
        urgency = "low"

    return {
        "summary": f"Fallback lokal menyarankan tindakan untuk {payload.current_crop} berdasarkan tren 1 jam terakhir di {payload.zone_name or payload.zone_id}.",
        "urgency": urgency,
        "recommendations": recommendations,
        "observation_focus": observation_focus or ["Lanjutkan sampling berkala untuk menjaga stabilitas zona."],
        "risk_flags": risk_flags,
        "provider": "local-fallback",
        "warning": reason,
    }


def build_azure_openai_client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError("Package openai/azure-identity belum terpasang.")

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    use_entra_id = os.getenv("AZURE_OPENAI_USE_ENTRA_ID", "false").lower() == "true"

    if not endpoint or not deployment:
        raise RuntimeError("AZURE_OPENAI_ENDPOINT dan AZURE_OPENAI_DEPLOYMENT wajib diisi.")

    if use_entra_id:
        if DefaultAzureCredential is None or get_bearer_token_provider is None:
            raise RuntimeError("azure-identity belum tersedia untuk autentikasi Entra ID.")
        credential = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )
    else:
        if not api_key:
            raise RuntimeError("AZURE_OPENAI_API_KEY wajib diisi jika Entra ID tidak dipakai.")
        credential = api_key

    return OpenAI(
        base_url=f"{endpoint}/openai/v1/",
        api_key=credential,
    )


def generate_azure_care_advice(payload: CareAdviceRequest) -> dict[str, Any]:
    if os.getenv("AZURE_OPENAI_ENABLED", "false").lower() != "true":
        raise RuntimeError("Azure OpenAI dinonaktifkan lewat konfigurasi.")

    client = build_azure_openai_client()
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    temperature = float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.2"))
    max_tokens = int(os.getenv("AZURE_OPENAI_MAX_OUTPUT_TOKENS", "900"))
    aggregated = aggregate_zone_samples(payload.nutrient_history)
    latest = payload.nutrient_history[-1]

    user_prompt = f"""
Anda adalah agronom AI untuk sistem pemantauan zona lahan.
Berikan rekomendasi penanganan praktis, singkat, dan bisa dieksekusi di lapangan.
Fokus pada tindakan 1-24 jam ke depan untuk tanaman aktif.
Gunakan hanya konteks berikut:
- Zona: {payload.zone_name or payload.zone_id}
- Tanaman aktif: {payload.current_crop}
- Jendela histori: {payload.history_window_minutes} menit
- Snapshot agregat: {json.dumps(aggregated, ensure_ascii=False)}
- Titik terbaru: {json.dumps(latest.model_dump(), ensure_ascii=False)}
- Konteks threshold Laravel: {json.dumps(payload.threshold_context or {}, ensure_ascii=False)}

Jika data tampak tidak cukup, katakan secara hati-hati dan beri langkah observasi tambahan.
Hindari saran medis, legal, atau klaim hasil pasti. Gunakan bahasa Indonesia.
Kembalikan response sesuai schema JSON yang diminta.
""".strip()

    completion = client.beta.chat.completions.parse(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "Anda adalah agronom AI. Berikan rekomendasi konservatif, "
                    "praktis, dan berbasis data sensor tanah. Jangan membuat klaim hasil pasti."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
        response_format=CareAdviceSchema,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError("Azure OpenAI tidak mengembalikan JSON sesuai schema.")

    data = parsed.model_dump()
    data["provider"] = "azure-openai"
    data["model"] = deployment
    return data


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict")
def predict_legacy(sample: LegacyPredictRequest) -> dict[str, Any]:
    samples = [
        ZoneSample(
            point_id="legacy-1",
            ph=sample.ph,
            nitrogen=sample.nitrogen,
            phosphorus=sample.phosphorus,
            potassium=sample.potassium,
            soil_moisture=sample.soil_moisture,
        ),
        ZoneSample(
            point_id="legacy-2",
            ph=sample.ph,
            nitrogen=sample.nitrogen,
            phosphorus=sample.phosphorus,
            potassium=sample.potassium,
            soil_moisture=sample.soil_moisture,
        ),
        ZoneSample(
            point_id="legacy-3",
            ph=sample.ph,
            nitrogen=sample.nitrogen,
            phosphorus=sample.phosphorus,
            potassium=sample.potassium,
            soil_moisture=sample.soil_moisture,
        ),
    ]
    payload = ZonePredictRequest(zone_id="legacy", zone_name="Legacy Zone", samples=samples)
    return predict_zone(payload)


@app.post("/predict/zone")
def predict_zone(payload: ZonePredictRequest) -> dict[str, Any]:
    if len(payload.samples) < 3:
        raise HTTPException(status_code=400, detail="Zona membutuhkan minimal 3 titik sampling.")

    aggregated = aggregate_zone_samples(payload.samples)
    prediction = build_crop_prediction(aggregated, payload.current_crop)

    return {
        "status": "success",
        "zone_id": payload.zone_id,
        "zone_name": payload.zone_name,
        "sample_count": len(payload.samples),
        "aggregated_features": aggregated,
        "prediction": prediction,
        "model_info": {
            "model_name": os.getenv("CROP_RECOMMENDATION_MODEL_NAME", "zone-heuristic-baseline"),
            "feature_set_type": "zone_aggregated",
        },
        "warnings": [] if len(payload.samples) >= 4 else ["Zona masih memiliki sampling terbatas."],
    }


@app.post("/advice/care")
def care_advice(payload: CareAdviceRequest) -> dict[str, Any]:
    try:
        return generate_azure_care_advice(payload)
    except Exception as exc:
        logger.warning("Azure OpenAI unavailable, using fallback care advice: %s", exc)
        return fallback_care_advice(payload, str(exc))
