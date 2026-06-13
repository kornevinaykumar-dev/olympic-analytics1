"""Loads the trained Random Forest model and serves predictions."""
import os
import joblib
import numpy as np
from config import Config

_model = None
_encoders = None


def _load():
    global _model, _encoders
    if _model is None:
        _model = joblib.load(Config.ML_MODEL_PATH)
        _encoders = joblib.load(Config.ML_ENCODERS_PATH)
    return _model, _encoders


def predict_medal(data: dict) -> dict:
    model, enc = _load()
    le_country = enc["country"]
    le_sport = enc["sport"]
    le_target = enc["target"]

    country = data["country"]
    sport = data["sport"]
    if country not in le_country.classes_:
        country = le_country.classes_[0]
    if sport not in le_sport.classes_:
        sport = le_sport.classes_[0]

    feats = np.array([[
        le_country.transform([country])[0],
        le_sport.transform([sport])[0],
        float(data["athletes"]),
        float(data["prev_gold"]),
        float(data["prev_silver"]),
        float(data["prev_bronze"]),
        float(data["participation_count"]),
        float(data["prev_gold"]) + float(data["prev_silver"]) + float(data["prev_bronze"]),
    ]])

    probs = model.predict_proba(feats)[0]
    idx = int(np.argmax(probs))
    label = le_target.inverse_transform([idx])[0]
    classes = [le_target.inverse_transform([i])[0] for i in range(len(probs))]
    prob_map = {c: round(float(p), 4) for c, p in zip(classes, probs)}
    return {
        "predicted_medal": label,
        "probability": round(float(probs[idx]), 4),
        "confidence": round(float(probs[idx]) * 100, 2),
        "all_probabilities": prob_map,
    }
