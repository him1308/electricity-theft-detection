from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from ml.feature_engineering import FEATURE_COLUMNS, build_explanations, engineer_features
from ml.preprocessing import clean_dataframe
from ml.wide_format import engineer_wide_features, is_wide_format


def risk_level(score: int) -> str:
    if score <= 30:
        return "Low"
    if score <= 60:
        return "Medium"
    if score <= 80:
        return "High"
    return "Critical"


def _scale(values: np.ndarray) -> np.ndarray:
    if len(values) == 0:
        return values
    low, high = np.percentile(values, 5), np.percentile(values, 95)
    if high - low <= 1e-9:
        return np.full_like(values, 50.0, dtype=float)
    return np.clip((values - low) / (high - low) * 100, 0, 100)


def load_model(model_path: str) -> dict[str, Any]:
    if not Path(model_path).exists():
        raise FileNotFoundError("Model has not been trained yet")
    return joblib.load(model_path)


def predict_dataframe(raw_df: pd.DataFrame, model_path: str) -> list[dict[str, Any]]:
    bundle = load_model(model_path)
    features = engineer_wide_features(raw_df) if is_wide_format(raw_df) else engineer_features(clean_dataframe(raw_df))
    pipeline = bundle["pipeline"]
    X = features[FEATURE_COLUMNS].to_numpy()

    if bundle["model_type"] == "supervised":
        probabilities = pipeline.predict_proba(X)[:, 1]
        model_scores = probabilities * 100
    else:
        scaler = pipeline.named_steps["scaler"]
        model = pipeline.named_steps["model"]
        normality = model.score_samples(scaler.transform(X))
        model_scores = 100 - _scale(normality)

    results: list[dict[str, Any]] = []
    for index, row in features.iterrows():
        rule_score = min(
            100,
            row["sudden_drop_pct"] * 80
            + row["mean_change_pct"] * 20
            + min(row["abnormal_reading_count"], 8) * 5
            + (15 if row["day_night_ratio"] < 0.75 else 0)
            + (10 if row["avg_power_factor"] and row["avg_power_factor"] < 0.72 else 0),
        )
        risk_score = int(np.clip(0.72 * model_scores[index] + 0.28 * rule_score, 0, 100))
        level = risk_level(risk_score)
        results.append(
            {
                "consumer_id": row["consumer_id"],
                "risk_score": risk_score,
                "risk_level": level,
                "anomaly_status": "Suspicious" if risk_score >= 61 else "Normal",
                "reasons": build_explanations(row, risk_score),
                "anomaly_score": round(float(model_scores[index]) / 100, 4),
            }
        )
    return results
