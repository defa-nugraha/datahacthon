from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.core.config import Settings
from app.schemas import ZonePredictionRequest


LOGGER = logging.getLogger(__name__)


class StrategyActionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    rationale: str
    timeframe: str
    expected_impact: str


class ZoneStrategySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    urgency: str
    reasoning: list[str]
    recommended_actions: list[StrategyActionSchema]
    monitoring_focus: list[str]
    risks: list[str]


class ZoneStrategicAdvisor:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(
        self,
        *,
        payload: ZonePredictionRequest,
        prediction_result: dict[str, Any],
        current_crop: str | None,
        time_horizon_days: int,
    ) -> dict[str, Any]:
        azure_warnings: list[str] = []
        if self.settings.azure_openai_enabled:
            try:
                strategic_payload = self._generate_with_azure(
                    payload=payload,
                    prediction_result=prediction_result,
                    current_crop=current_crop,
                    time_horizon_days=time_horizon_days,
                )
                strategic_payload["provider"] = "azure_openai"
                return strategic_payload
            except Exception as exc:  # pragma: no cover - network/config dependent
                LOGGER.warning("Azure OpenAI strategic advice failed: %s", exc)
                azure_warnings.append(f"Azure OpenAI fallback activated: {type(exc).__name__}: {exc}")

        fallback = self._generate_fallback(
            prediction_result=prediction_result,
            current_crop=current_crop,
            time_horizon_days=time_horizon_days,
        )
        fallback["provider"] = "local_fallback"
        if azure_warnings:
            fallback["risks"] = list(dict.fromkeys(fallback["risks"] + azure_warnings))
        return fallback

    def _generate_with_azure(
        self,
        *,
        payload: ZonePredictionRequest,
        prediction_result: dict[str, Any],
        current_crop: str | None,
        time_horizon_days: int,
    ) -> dict[str, Any]:
        if not self.settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required when Azure OpenAI is enabled.")
        if not self.settings.azure_openai_deployment:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT is required when Azure OpenAI is enabled.")

        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depends on local environment
            raise ImportError("The `openai` package is required for Azure OpenAI integration.") from exc

        credential: Any
        if self.settings.azure_openai_api_key:
            credential = self.settings.azure_openai_api_key
        elif self.settings.azure_openai_use_entra_id:
            try:
                from azure.identity import DefaultAzureCredential, get_bearer_token_provider
            except ImportError as exc:  # pragma: no cover - depends on local environment
                raise ImportError("The `azure-identity` package is required for Entra ID authentication.") from exc

            credential = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
        else:
            raise ValueError(
                "Azure OpenAI is enabled but no authentication method is configured. "
                "Set AZURE_OPENAI_API_KEY or enable AZURE_OPENAI_USE_ENTRA_ID."
            )

        client = OpenAI(
            base_url=self.settings.azure_openai_endpoint.rstrip("/") + "/openai/v1/",
            api_key=credential,
        )

        prediction_payload = {
            "zone_id": payload.zone_id,
            "sample_count": prediction_result["sample_count"],
            "current_crop": current_crop or "Belum ada",
            "recommended_label": prediction_result["prediction"]["recommended_label"],
            "confidence": prediction_result["prediction"]["confidence"],
            "top_k": prediction_result["prediction"]["top_k"],
            "aggregated_features": prediction_result["aggregated_features"],
            "warnings": prediction_result["warnings"],
            "time_horizon_days": time_horizon_days,
        }

        completion = client.beta.chat.completions.parse(
            model=self.settings.azure_openai_deployment,
            temperature=self.settings.azure_openai_temperature,
            max_tokens=self.settings.azure_openai_max_output_tokens,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an agronomic strategy assistant for a zone-based crop recommendation system. "
                        "Produce concise, actionable recommendations in Indonesian. "
                        "Ground every recommendation in the provided nutrient and prediction context. "
                        "Do not mention unsupported assumptions."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Buat insight strategis untuk satu zona lahan berdasarkan hasil model klasifikasi tanaman. "
                        "Kembalikan hanya sesuai schema.\n\n"
                        + json.dumps(prediction_payload, ensure_ascii=False, indent=2)
                    ),
                },
            ],
            response_format=ZoneStrategySchema,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI did not return a parsed structured response.")
        return parsed.model_dump()

    def _generate_fallback(
        self,
        *,
        prediction_result: dict[str, Any],
        current_crop: str | None,
        time_horizon_days: int,
    ) -> dict[str, Any]:
        aggregated = prediction_result["aggregated_features"]
        recommended_label = prediction_result["prediction"]["recommended_label"]
        ph_mean = self._get_feature(aggregated, "ph_mean")
        n_mean = self._get_feature(aggregated, "nitrogen_mean")
        p_mean = self._get_feature(aggregated, "phosphorus_mean")
        k_mean = self._get_feature(aggregated, "potassium_mean")
        rainfall_mean = self._get_feature(aggregated, "rainfall_mean_mean")
        temperature_mean = self._get_feature(aggregated, "temperature_mean_mean")

        reasoning: list[str] = []
        actions: list[dict[str, str]] = []
        monitoring_focus: list[str] = []
        risks: list[str] = []
        urgency = "medium"

        if ph_mean is not None:
            if ph_mean < 6.0:
                reasoning.append("pH zona cenderung asam, sehingga efisiensi penyerapan fosfor berisiko turun.")
                actions.append(
                    {
                        "title": "Evaluasi koreksi pH bertahap",
                        "rationale": "Kondisi terlalu asam dapat menekan respons tanaman terhadap pemupukan fosfor.",
                        "timeframe": f"1-{min(time_horizon_days, 14)} hari",
                        "expected_impact": "Profil pH lebih stabil untuk fase pertumbuhan berikutnya.",
                    }
                )
                monitoring_focus.append("Pantau pH dan respons visual daun muda.")
                risks.append("Zona berisiko mengalami hambatan penyerapan nutrisi mikro dan fosfor.")
                urgency = "high"
            elif ph_mean > 7.2:
                reasoning.append("pH zona agak basa, sehingga beberapa unsur mikro berpotensi kurang tersedia.")
                monitoring_focus.append("Pantau gejala defisiensi mikro pada pucuk dan daun muda.")

        if p_mean is not None and p_mean < 25:
            reasoning.append("Fosfor zona masih rendah dibanding rentang yang aman untuk stabilitas rekomendasi tanaman.")
            actions.append(
                {
                    "title": "Prioritaskan intervensi fosfor",
                    "rationale": "Nilai fosfor rendah paling cepat memengaruhi vigor awal dan fase generatif.",
                    "timeframe": "Secepatnya",
                    "expected_impact": "Mengurangi risiko keterlambatan pertumbuhan dan pembentukan organ produksi.",
                }
            )
            risks.append("Risiko pertumbuhan generatif tertahan bila fosfor tidak diperbaiki.")
            urgency = "high"

        if n_mean is not None and n_mean < 80:
            reasoning.append("Nitrogen zona relatif rendah untuk sebagian besar tanaman serealia dan hortikultura intensif.")
            actions.append(
                {
                    "title": "Tinjau kebutuhan nitrogen susulan",
                    "rationale": "Nitrogen rendah biasanya cepat terlihat pada pertumbuhan vegetatif dan warna daun.",
                    "timeframe": f"1-{min(time_horizon_days, 10)} hari",
                    "expected_impact": "Pertumbuhan vegetatif lebih konsisten dan warna daun lebih stabil.",
                }
            )
            monitoring_focus.append("Pantau warna daun dan laju pertumbuhan vegetatif.")

        if k_mean is not None and k_mean < 70:
            reasoning.append("Kalium zona belum kuat, sehingga ketahanan tanaman terhadap stres bisa lebih rendah.")
            monitoring_focus.append("Pantau vigor batang dan ketahanan tanaman pada fase pembentukan hasil.")

        if rainfall_mean is not None:
            if rainfall_mean < 5:
                reasoning.append("Curah hujan rata-rata rendah, sehingga strategi air perlu dijaga lebih ketat.")
                monitoring_focus.append("Pantau kelembapan tanah dan jadwal irigasi.")
            elif rainfall_mean > 12:
                risks.append("Curah hujan relatif tinggi dapat meningkatkan risiko pencucian unsur hara.")

        if temperature_mean is not None and temperature_mean > 30:
            risks.append("Suhu rata-rata tinggi dapat menaikkan stres tanaman dan kebutuhan air.")

        if not actions:
            actions.append(
                {
                    "title": "Pertahankan manajemen saat ini",
                    "rationale": "Profil zona relatif dekat dengan tanaman rekomendasi utama dan tidak ada sinyal defisiensi dominan.",
                    "timeframe": f"{min(time_horizon_days, 7)} hari ke depan",
                    "expected_impact": "Menjaga stabilitas kondisi zona sambil menunggu data sampling berikutnya.",
                }
            )
            urgency = "low"

        if not reasoning:
            reasoning.append("Model melihat kecocokan tertinggi pada profil unsur hara inti dan kondisi iklim zona saat ini.")

        if not monitoring_focus:
            monitoring_focus.append("Lanjutkan sampling berkala dan validasi respons tanaman terhadap intervensi.")

        current_crop_text = current_crop or "Belum ada tanaman aktif"
        summary = (
            f"Zona saat ini paling cocok untuk {recommended_label}. "
            f"Tanaman aktif: {current_crop_text}. "
            f"Fokus {time_horizon_days} hari ke depan adalah menjaga kestabilan hara inti dan mengurangi risiko utama yang terdeteksi."
        )

        return {
            "summary": summary,
            "urgency": urgency,
            "reasoning": list(dict.fromkeys(reasoning)),
            "recommended_actions": actions,
            "monitoring_focus": list(dict.fromkeys(monitoring_focus)),
            "risks": list(dict.fromkeys(risks)),
        }

    @staticmethod
    def _get_feature(aggregated_features: dict[str, Any], feature_name: str) -> float | None:
        value = aggregated_features.get(feature_name)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
