from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas import ModelMetricsRead, ModelStatus
from app.services.data_service import ensure_demo_data, readings_to_dataframe
from app.services.model_service import latest_metadata, model_exists, predict_and_alert, train_from_database


router = APIRouter()
settings = get_settings()


@router.post("/train", response_model=ModelMetricsRead)
def train(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> ModelMetricsRead:
    ensure_demo_data(db)
    try:
        metadata = train_from_database(db)
        predict_and_alert(db, readings_to_dataframe(db))
        return metadata
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/metrics", response_model=ModelMetricsRead)
def metrics(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ModelMetricsRead:
    metadata = latest_metadata(db)
    if not metadata:
        raise HTTPException(status_code=404, detail="Model has not been trained yet")
    return metadata


@router.get("/status", response_model=ModelStatus)
def status(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ModelStatus:
    metadata = latest_metadata(db)
    return ModelStatus(
        is_trained=model_exists(),
        model_path=settings.model_path,
        model_name=metadata.model_name if metadata else None,
        version=metadata.version if metadata else None,
        trained_at=metadata.trained_at if metadata else None,
        samples=metadata.samples if metadata else 0,
        features=metadata.features if metadata else 0,
    )
