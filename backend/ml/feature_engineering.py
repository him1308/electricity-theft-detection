from __future__ import annotations

import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "mean_consumption",
    "median_consumption",
    "std_consumption",
    "min_consumption",
    "max_consumption",
    "total_consumption",
    "peak_consumption",
    "off_peak_consumption",
    "consumption_variance",
    "mean_change_pct",
    "sudden_drop_pct",
    "sudden_increase_pct",
    "abnormal_reading_count",
    "rolling_mean_avg",
    "rolling_std_avg",
    "weekend_weekday_ratio",
    "day_night_ratio",
    "avg_voltage",
    "voltage_variance",
    "avg_current",
    "current_variance",
    "avg_power_factor",
]


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0 or np.isnan(denominator):
        return 0.0
    return float(numerator / denominator)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    working["timestamp"] = pd.to_datetime(working["timestamp"])
    working["hour"] = working["timestamp"].dt.hour
    working["is_weekend"] = working["timestamp"].dt.dayofweek >= 5
    working["is_day"] = working["hour"].between(6, 21)
    working["change_pct"] = working.groupby("consumer_id")["energy_consumption"].pct_change().replace([np.inf, -np.inf], np.nan)
    working["rolling_mean"] = working.groupby("consumer_id")["energy_consumption"].transform(
        lambda series: series.rolling(7, min_periods=2).mean()
    )
    working["rolling_std"] = working.groupby("consumer_id")["energy_consumption"].transform(
        lambda series: series.rolling(7, min_periods=2).std()
    )

    rows: list[dict[str, float | str]] = []
    global_mean = working["energy_consumption"].mean()
    global_std = working["energy_consumption"].std() or 1

    for consumer_id, group in working.groupby("consumer_id"):
        readings = group["energy_consumption"]
        day_avg = group.loc[group["is_day"], "energy_consumption"].mean()
        night_avg = group.loc[~group["is_day"], "energy_consumption"].mean()
        weekend_avg = group.loc[group["is_weekend"], "energy_consumption"].mean()
        weekday_avg = group.loc[~group["is_weekend"], "energy_consumption"].mean()
        abnormal_count = int(((readings - global_mean).abs() > 2.5 * global_std).sum())
        drops = group["change_pct"].dropna()

        row = {
            "consumer_id": consumer_id,
            "mean_consumption": float(readings.mean()),
            "median_consumption": float(readings.median()),
            "std_consumption": float(readings.std() or 0),
            "min_consumption": float(readings.min()),
            "max_consumption": float(readings.max()),
            "total_consumption": float(readings.sum()),
            "peak_consumption": float(group.loc[group["hour"].between(18, 22), "energy_consumption"].mean() or 0),
            "off_peak_consumption": float(group.loc[group["hour"].between(0, 5), "energy_consumption"].mean() or 0),
            "consumption_variance": float(readings.var() or 0),
            "mean_change_pct": float(drops.abs().mean() if not drops.empty else 0),
            "sudden_drop_pct": float(abs(drops.min()) if not drops.empty and drops.min() < 0 else 0),
            "sudden_increase_pct": float(drops.max() if not drops.empty and drops.max() > 0 else 0),
            "abnormal_reading_count": abnormal_count,
            "rolling_mean_avg": float(group["rolling_mean"].mean() or readings.mean()),
            "rolling_std_avg": float(group["rolling_std"].mean() or 0),
            "weekend_weekday_ratio": _safe_ratio(float(weekend_avg or 0), float(weekday_avg or 0)),
            "day_night_ratio": _safe_ratio(float(day_avg or 0), float(night_avg or 0)),
            "avg_voltage": float(group["voltage"].mean() if "voltage" in group else 0),
            "voltage_variance": float(group["voltage"].var() if "voltage" in group else 0),
            "avg_current": float(group["current"].mean() if "current" in group else 0),
            "current_variance": float(group["current"].var() if "current" in group else 0),
            "avg_power_factor": float(group["power_factor"].mean() if "power_factor" in group else 0),
        }
        rows.append(row)

    features = pd.DataFrame(rows)
    for column in FEATURE_COLUMNS:
        if column not in features:
            features[column] = 0.0
    features[FEATURE_COLUMNS] = features[FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return features[["consumer_id", *FEATURE_COLUMNS]]


def build_explanations(row: pd.Series, risk_score: int) -> list[str]:
    reasons: list[str] = []
    if row.get("sudden_drop_pct", 0) > 0.35:
        reasons.append(f"{row['sudden_drop_pct']:.0%} sudden consumption reduction")
    if row.get("std_consumption", 0) > row.get("mean_consumption", 0) * 0.65:
        reasons.append("High deviation from historical average")
    if row.get("day_night_ratio", 1) < 0.75:
        reasons.append("Unusual night-time consumption pattern")
    if row.get("weekend_weekday_ratio", 1) > 1.7:
        reasons.append("Weekend consumption is unusually higher than weekday use")
    if row.get("avg_power_factor", 1) and row.get("avg_power_factor", 1) < 0.72:
        reasons.append("Low average power factor detected")
    if row.get("abnormal_reading_count", 0) >= 3:
        reasons.append("Repeated abnormal meter readings")
    if not reasons:
        reasons.append("Model score is elevated compared with peer consumers" if risk_score >= 61 else "No major suspicious indicators")
    return reasons[:4]
