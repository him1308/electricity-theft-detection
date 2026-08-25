from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.models import ConsumptionReading, Consumer
from ml.preprocessing import clean_dataframe, validate_dataframe
from ml.synthetic import generate_synthetic_readings
from ml.wide_format import is_wide_format, wide_consumer_column, wide_to_long_recent


def validate_csv(path: Path) -> dict[str, object]:
    df = pd.read_csv(path)
    result = validate_dataframe(df)
    return {
        "is_valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
        "rows": result.rows,
        "columns": result.columns,
        "preview": df.head(10).to_dict(orient="records"),
    }


def ingest_dataframe(db: Session, df: pd.DataFrame) -> int:
    if is_wide_format(df):
        return ingest_wide_dataframe(db, df)
    cleaned = clean_dataframe(df)
    known = {consumer.consumer_id for consumer in db.query(Consumer.consumer_id).all()}
    consumers: list[Consumer] = []
    for consumer_id, group in cleaned.groupby("consumer_id"):
        if consumer_id in known:
            continue
        first = group.iloc[0]
        consumers.append(
            Consumer(
                consumer_id=consumer_id,
                name=str(first.get("name") or f"Consumer {consumer_id}"),
                location=str(first.get("location") or "Unknown"),
                meter_number=str(first.get("meter_number") or f"SM-{consumer_id}"),
            )
        )
        known.add(consumer_id)
    if consumers:
        db.add_all(consumers)
        db.flush()

    existing_keys = {
        (reading.consumer_id, reading.timestamp)
        for reading in db.query(ConsumptionReading.consumer_id, ConsumptionReading.timestamp).all()
    }
    readings: list[ConsumptionReading] = []
    for record in cleaned.to_dict(orient="records"):
        timestamp = record["timestamp"].to_pydatetime() if hasattr(record["timestamp"], "to_pydatetime") else record["timestamp"]
        key = (record["consumer_id"], timestamp)
        if key in existing_keys:
            continue
        readings.append(
            ConsumptionReading(
                consumer_id=record["consumer_id"],
                timestamp=timestamp,
                energy_consumption=float(record["energy_consumption"]),
                voltage=None if pd.isna(record.get("voltage")) else float(record.get("voltage")),
                current=None if pd.isna(record.get("current")) else float(record.get("current")),
                power_factor=None if pd.isna(record.get("power_factor")) else float(record.get("power_factor")),
                meter_status=None if pd.isna(record.get("meter_status")) else str(record.get("meter_status")),
            )
        )
        existing_keys.add(key)
    if readings:
        db.add_all(readings)
    db.commit()
    return len(readings)


def ingest_wide_dataframe(db: Session, df: pd.DataFrame, sample_days: int = 30) -> int:
    consumer_col = wide_consumer_column(df)
    known = {consumer.consumer_id for consumer in db.query(Consumer.consumer_id).all()}
    consumers: list[Consumer] = []
    for consumer_id in df[consumer_col].astype(str).unique():
        if consumer_id in known:
            continue
        consumers.append(
            Consumer(
                consumer_id=consumer_id,
                name=f"Consumer {consumer_id[:8]}",
                location="Uploaded Dataset",
                meter_number=f"SM-{consumer_id[:12]}",
            )
        )
        known.add(consumer_id)
    if consumers:
        db.add_all(consumers)
        db.flush()

    recent = wide_to_long_recent(df, days=sample_days)
    existing_keys: set[tuple[str, object]] = set()
    consumer_ids = recent["consumer_id"].unique().tolist()
    if db.query(ConsumptionReading.id).first():
        for start in range(0, len(consumer_ids), 800):
            chunk = consumer_ids[start : start + 800]
            existing_keys.update(
                (reading.consumer_id, reading.timestamp)
                for reading in db.query(ConsumptionReading.consumer_id, ConsumptionReading.timestamp)
                .filter(ConsumptionReading.consumer_id.in_(chunk))
                .all()
            )
    readings: list[ConsumptionReading] = []
    batch_size = 25_000
    inserted = 0
    for record in recent.to_dict(orient="records"):
        timestamp = record["timestamp"].to_pydatetime() if hasattr(record["timestamp"], "to_pydatetime") else record["timestamp"]
        key = (record["consumer_id"], timestamp)
        if key in existing_keys:
            continue
        readings.append(
            ConsumptionReading(
                consumer_id=record["consumer_id"],
                timestamp=timestamp,
                energy_consumption=float(record["energy_consumption"]),
                meter_status=record.get("meter_status"),
            )
        )
        existing_keys.add(key)
        if len(readings) >= batch_size:
            db.add_all(readings)
            db.commit()
            inserted += len(readings)
            readings.clear()
    if readings:
        db.add_all(readings)
        db.commit()
        inserted += len(readings)
    else:
        db.commit()
    return inserted


def ensure_demo_data(db: Session) -> None:
    if db.query(ConsumptionReading).count() > 0:
        return
    ingest_dataframe(db, generate_synthetic_readings())


def readings_to_dataframe(db: Session, consumer_id: str | None = None) -> pd.DataFrame:
    query = db.query(ConsumptionReading)
    if consumer_id:
        query = query.filter(ConsumptionReading.consumer_id == consumer_id)
    rows = query.order_by(ConsumptionReading.consumer_id, ConsumptionReading.timestamp).all()
    return pd.DataFrame(
        [
            {
                "consumer_id": row.consumer_id,
                "timestamp": row.timestamp,
                "energy_consumption": row.energy_consumption,
                "voltage": row.voltage,
                "current": row.current,
                "power_factor": row.power_factor,
                "meter_status": row.meter_status,
            }
            for row in rows
        ]
    )
