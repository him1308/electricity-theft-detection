from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ml.wide_format import is_wide_format


REQUIRED_COLUMNS = {"consumer_id", "timestamp", "energy_consumption"}
OPTIONAL_COLUMNS = ["voltage", "current", "power_factor", "meter_status", "location", "meter_number", "name"]


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    rows: int
    columns: list[str]


def validate_dataframe(df: pd.DataFrame) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if is_wide_format(df):
        return ValidationResult(True, errors, ["Detected wide smart-meter dataset; date columns will be normalized"], len(df), list(df.columns))
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        errors.append(f"Missing required columns: {', '.join(sorted(missing))}")
    for column in OPTIONAL_COLUMNS:
        if column not in df.columns:
            warnings.append(f"Optional column '{column}' not supplied")
    if "energy_consumption" in df.columns and pd.to_numeric(df["energy_consumption"], errors="coerce").isna().all():
        errors.append("energy_consumption must contain numeric values")
    return ValidationResult(not errors, errors, warnings, len(df), list(df.columns))


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [str(column).strip().lower() for column in cleaned.columns]
    validation = validate_dataframe(cleaned)
    if not validation.is_valid:
        raise ValueError("; ".join(validation.errors))

    cleaned["consumer_id"] = cleaned["consumer_id"].astype(str).str.strip()
    cleaned["timestamp"] = pd.to_datetime(cleaned["timestamp"], errors="coerce")
    cleaned["energy_consumption"] = pd.to_numeric(cleaned["energy_consumption"], errors="coerce")
    cleaned = cleaned.dropna(subset=["consumer_id", "timestamp", "energy_consumption"])
    cleaned = cleaned[cleaned["energy_consumption"] >= 0]

    for column in ["voltage", "current", "power_factor"]:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    for column in OPTIONAL_COLUMNS:
        if column not in cleaned.columns:
            cleaned[column] = None

    cleaned = cleaned.sort_values(["consumer_id", "timestamp"]).drop_duplicates(
        subset=["consumer_id", "timestamp"], keep="last"
    )
    return cleaned.reset_index(drop=True)
