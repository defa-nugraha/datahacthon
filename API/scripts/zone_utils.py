from __future__ import annotations

import re
from typing import Any

import pandas as pd


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return "unknown"
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def snake_case(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown"


def normalize_soil_color(value: Any) -> str:
    text = normalize_text(value).lower()
    text = text.replace(";", " ")
    text = text.replace("redish", "reddish")
    text = text.replace("reddis", "reddish")
    text = text.replace("broown", "brown")
    text = text.replace("lihgtish", "light")
    text = text.replace("darkbrown", "dark brown")
    text = text.replace("replacement of inaccessible target", "")
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text or text == "other":
        return "other"
    if "yellowish brown" in text:
        return "yellowish_brown"
    if "very dark brown" in text:
        return "very_dark_brown"
    if "very dark gray" in text:
        return "very_dark_gray"
    if "dark grayish brown" in text:
        return "dark_grayish_brown"
    if "grayish brown" in text:
        return "grayish_brown"
    if "dark reddish brown" in text or "reddish brown" in text or ("red" in text and "brown" in text):
        return "reddish_brown"
    if "dark brown" in text:
        return "dark_brown"
    if "brown" in text:
        return "brown"
    if "yellowish" in text:
        return "yellowish"
    if "black" in text or "vertisol" in text:
        return "black"
    if "dark gray" in text or "dark grey" in text:
        return "dark_gray"
    if "gray" in text or "grey" in text:
        return "gray"
    if "red" in text or "reddish" in text or "luvisol" in text:
        return "red"
    return snake_case(text)


def normalize_target_label(value: Any) -> str:
    text = normalize_text(value)
    text = text.replace("seed", "Seed")
    text = text.replace("pepper", "Pepper")
    text = text.title()
    text = text.replace("Niger Seed", "Niger Seed")
    return text
