from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Alert, ModelMetadata
from app.services.data_service import readings_to_dataframe
from ml.predict import predict_dataframe
from ml.train import train_model


settings = get_settings()


def train_from_database(db: Session) -> ModelMetadata:
    df = readings_to_dataframe(db)
    if df.empty:
        raise ValueError("No consumption readings available for training")
    result = train_model(df, settings.model_path)
    metrics = result["metrics"]
    metadata = ModelMetadata(
        model_name=result["model_name"],
        version=result["version"],
        model_type=result["model_type"],
        trained_at=datetime.utcnow(),
        accuracy=metrics.get("accuracy"),
        precision=metrics.get("precision"),
        recall=metrics.get("recall"),
        f1_score=metrics.get("f1_score"),
        roc_auc=metrics.get("roc_auc"),
        samples=result["samples"],
        features=result["features"],
        notes=result["notes"],
    )
    db.add(metadata)
    db.commit()
    db.refresh(metadata)
    return metadata


def latest_metadata(db: Session) -> ModelMetadata | None:
    return db.query(ModelMetadata).order_by(ModelMetadata.trained_at.desc()).first()


def predict_and_alert(db: Session, df: pd.DataFrame) -> list[dict[str, object]]:
    results = predict_dataframe(df, settings.model_path)
    for result in results:
        if int(result["risk_score"]) < 61:
            continue
        existing = (
            db.query(Alert)
            .filter(Alert.consumer_id == result["consumer_id"], Alert.status.in_(["New", "Under Investigation"]))
            .first()
        )
        reason = "; ".join(result["reasons"])
        if existing:
            existing.risk_score = int(result["risk_score"])
            existing.risk_level = str(result["risk_level"])
            existing.reason = reason
        else:
            db.add(
                Alert(
                    consumer_id=str(result["consumer_id"]),
                    risk_score=int(result["risk_score"]),
                    risk_level=str(result["risk_level"]),
                    reason=reason,
                )
            )
    db.commit()
    return results


def model_exists() -> bool:
    return Path(settings.model_path).exists()
