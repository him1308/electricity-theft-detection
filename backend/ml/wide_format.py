from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from ml.feature_engineering import FEATURE_COLUMNS


CONSUMER_COLUMNS = ["CONS_NO", "consumer_id", "Consumer_ID", "consumer"]
LABEL_COLUMNS = ["FLAG", "is_theft", "theft_label", "fraud_label", "label"]


def _first_present(columns: pd.Index, candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


@lru_cache(maxsize=16)
def _parse_date_column(column: str) -> pd.Timestamp | None:
    parsed = pd.to_datetime(column, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed


def date_columns(df: pd.DataFrame) -> list[str]:
    dated = [(column, _parse_date_column(str(column))) for column in df.columns]
    valid = [(column, parsed) for column, parsed in dated if parsed is not None]
    return [column for column, _ in sorted(valid, key=lambda item: item[1])]


def is_wide_format(df: pd.DataFrame) -> bool:
    consumer_col = _first_present(df.columns, CONSUMER_COLUMNS)
    return consumer_col is not None and len(date_columns(df)) >= 7


def wide_label_column(df: pd.DataFrame) -> str | None:
    return _first_present(df.columns, LABEL_COLUMNS)


def wide_consumer_column(df: pd.DataFrame) -> str:
    consumer_col = _first_present(df.columns, CONSUMER_COLUMNS)
    if not consumer_col:
        raise ValueError("Wide dataset must contain CONS_NO or consumer_id")
    return consumer_col


def engineer_wide_features(df: pd.DataFrame) -> pd.DataFrame:
    if not is_wide_format(df):
        raise ValueError("Dataset is not in supported wide smart-meter format")

    consumer_col = wide_consumer_column(df)
    dates = date_columns(df)
    matrix = df[dates].apply(pd.to_numeric, errors="coerce").clip(lower=0)
    matrix = matrix.interpolate(axis=1, limit_direction="both").fillna(0.0)
    values = matrix.to_numpy(dtype=float)

    with np.errstate(divide="ignore", invalid="ignore"):
        previous = values[:, :-1]
        current = values[:, 1:]
        changes = np.where(previous > 0, (current - previous) / previous, 0.0)

    timestamps = pd.to_datetime(dates)
    weekend_mask = np.array([timestamp.weekday() >= 5 for timestamp in timestamps])
    weekday_mask = ~weekend_mask
    global_mean = float(np.mean(values))
    global_std = float(np.std(values)) or 1.0

    features = pd.DataFrame(
        {
            "consumer_id": df[consumer_col].astype(str),
            "mean_consumption": np.mean(values, axis=1),
            "median_consumption": np.median(values, axis=1),
            "std_consumption": np.std(values, axis=1),
            "min_consumption": np.min(values, axis=1),
            "max_consumption": np.max(values, axis=1),
            "total_consumption": np.sum(values, axis=1),
            "peak_consumption": np.percentile(values, 95, axis=1),
            "off_peak_consumption": np.percentile(values, 10, axis=1),
            "consumption_variance": np.var(values, axis=1),
            "mean_change_pct": np.mean(np.abs(changes), axis=1),
            "sudden_drop_pct": np.abs(np.minimum(np.min(changes, axis=1), 0)),
            "sudden_increase_pct": np.maximum(np.max(changes, axis=1), 0),
            "abnormal_reading_count": np.sum(np.abs(values - global_mean) > 2.5 * global_std, axis=1),
            "rolling_mean_avg": np.mean(values, axis=1),
            "rolling_std_avg": np.std(values, axis=1),
            "weekend_weekday_ratio": _safe_axis_ratio(values[:, weekend_mask].mean(axis=1), values[:, weekday_mask].mean(axis=1)),
            "day_night_ratio": np.ones(values.shape[0]),
            "avg_voltage": np.zeros(values.shape[0]),
            "voltage_variance": np.zeros(values.shape[0]),
            "avg_current": np.zeros(values.shape[0]),
            "current_variance": np.zeros(values.shape[0]),
            "avg_power_factor": np.zeros(values.shape[0]),
        }
    )

    for column in FEATURE_COLUMNS:
        if column not in features:
            features[column] = 0.0
    features[FEATURE_COLUMNS] = features[FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return features[["consumer_id", *FEATURE_COLUMNS]]


def labels_from_wide(df: pd.DataFrame, features: pd.DataFrame) -> np.ndarray | None:
    label_col = wide_label_column(df)
    if not label_col:
        return None
    consumer_col = wide_consumer_column(df)
    labels = (
        df.assign(_consumer_id=df[consumer_col].astype(str))
        .groupby("_consumer_id")[label_col]
        .max()
        .reindex(features["consumer_id"])
        .fillna(0)
        .astype(int)
    )
    return labels.to_numpy()


def wide_to_long_recent(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    if not is_wide_format(df):
        raise ValueError("Dataset is not in supported wide smart-meter format")
    consumer_col = wide_consumer_column(df)
    dates = date_columns(df)[-days:]
    keep = [consumer_col, *dates]
    long = df[keep].melt(id_vars=[consumer_col], var_name="timestamp", value_name="energy_consumption")
    long = long.rename(columns={consumer_col: "consumer_id"})
    long["timestamp"] = pd.to_datetime(long["timestamp"], errors="coerce")
    long["energy_consumption"] = pd.to_numeric(long["energy_consumption"], errors="coerce").fillna(0).clip(lower=0)
    long["meter_status"] = "Uploaded wide dataset sample"
    return long


def _safe_axis_ratio(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    return np.divide(numerator, denominator, out=np.zeros_like(numerator, dtype=float), where=denominator != 0)
