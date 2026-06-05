from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.core.config import Settings
from app.core.exceptions import PredictionError
from app.schemas import WeatherForecastRequest


class WeatherForecaster:
    """Monthly weather forecaster backed by the existing ARIMA artifacts."""

    MODEL_FILES = {
        "suhu_maksimum_c": "arima_suhu_maksimum_model.pkl",
        "suhu_rata_rata_c": "arima_suhu_rata-rata_model.pkl",
    }

    def __init__(self, settings: Settings):
        self.settings = settings
        self.forecast_dir = settings.weather_forecast_dir
        self._models: dict[str, Any] | None = None

    def forecast(self, payload: WeatherForecastRequest) -> dict[str, Any]:
        months = min(payload.months, self.settings.weather_forecast_max_months)
        models = self._load_models()
        month_index = pd.date_range(
            start=datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            periods=months,
            freq="MS",
        )

        forecast_columns: dict[str, list[float | None]] = {}
        for output_name, model in models.items():
            forecast_values = model.forecast(steps=months)
            values = forecast_values.values if hasattr(forecast_values, "values") else forecast_values
            forecast_columns[output_name] = [round(float(value), 2) for value in values]

        forecast_rows = []
        for idx, month in enumerate(month_index):
            forecast_rows.append(
                {
                    "month": month.strftime("%Y-%m"),
                    "suhu_maksimum_c": forecast_columns.get("suhu_maksimum_c", [None] * months)[idx],
                    "suhu_rata_rata_c": forecast_columns.get("suhu_rata_rata_c", [None] * months)[idx],
                }
            )

        warnings = [
            "Model forecasting saat ini berbasis deret waktu historis yang tersedia, bukan model spasial berbasis koordinat.",
            "Latitude dan longitude dicatat sebagai konteks zona, tetapi belum menjadi fitur input model ARIMA ini.",
        ]

        return {
            "status": "success",
            "zone_id": payload.zone_id,
            "location": {
                "latitude": payload.latitude,
                "longitude": payload.longitude,
            },
            "crop_name": payload.crop_name,
            "horizon_months": months,
            "forecast": forecast_rows,
            "model_info": {
                "model_type": "ARIMA",
                "artifact_dir": str(self.forecast_dir),
                "targets": list(self.MODEL_FILES.keys()),
                "frequency": "monthly",
            },
            "warnings": warnings,
        }

    def _load_models(self) -> dict[str, Any]:
        if self._models is not None:
            return self._models

        if not self.forecast_dir.exists():
            raise PredictionError(
                "Weather forecasting artifacts are not available.",
                details={"missing_dir": str(self.forecast_dir)},
            )

        models: dict[str, Any] = {}
        missing_files: list[str] = []

        for output_name, filename in self.MODEL_FILES.items():
            model_path = self.forecast_dir / filename
            if not model_path.exists():
                missing_files.append(str(model_path))
                continue
            models[output_name] = joblib.load(model_path)

        if missing_files:
            raise PredictionError(
                "Some weather forecasting artifacts are missing.",
                details={"missing_files": missing_files},
            )

        self._models = models
        return models
