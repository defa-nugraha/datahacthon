from __future__ import annotations

import argparse
import json
from typing import Any

import sys
from pathlib import Path

import joblib
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.common import BEST_MODEL_PATH, FINAL_METADATA_PATH, PROJECT_ROOT


def load_artifacts() -> tuple[Any, dict[str, Any]]:
    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {BEST_MODEL_PATH}. Run `python scripts/train_model.py` first."
        )
    if not FINAL_METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset metadata not found at {FINAL_METADATA_PATH}. Run `python scripts/data_preparation.py` first."
        )
    model = joblib.load(BEST_MODEL_PATH)
    metadata = json.loads(FINAL_METADATA_PATH.read_text(encoding="utf-8"))
    return model, metadata


def predict_from_payload(payload: dict[str, Any], top_k: int = 3) -> dict[str, Any]:
    model, metadata = load_artifacts()
    feature_columns = [
        column
        for column in metadata["final_dataset_versions"]["final_dataset"]["columns"]
        if column not in {"record_id", "source_dataset", metadata["target_column"]}
    ]

    row = {column: payload.get(column) for column in feature_columns}
    frame = pd.DataFrame([row], columns=feature_columns)
    probabilities = model.predict_proba(frame)[0]
    classes = model.classes_
    ranked_indices = probabilities.argsort()[::-1][:top_k]
    ranked_predictions = [
        {"target_crop": classes[index], "probability": float(probabilities[index])}
        for index in ranked_indices
    ]
    return {
        "input": row,
        "top_predictions": ranked_predictions,
        "predicted_target": ranked_predictions[0]["target_crop"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run inference for the vegetation recommendation model.")
    parser.add_argument(
        "--input-json",
        required=True,
        help="JSON object containing feature values for the final_dataset schema.",
    )
    parser.add_argument("--top-k", type=int, default=3, help="Number of ranked predictions to return.")
    args = parser.parse_args()

    payload = json.loads(args.input_json)
    result = predict_from_payload(payload, top_k=args.top_k)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
