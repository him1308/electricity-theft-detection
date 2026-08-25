from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth import require_analyst
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.services.data_service import ingest_dataframe, validate_csv
from app.services.model_service import model_exists, predict_and_alert


router = APIRouter()
settings = get_settings()


@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst),
) -> dict[str, object]:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    path = settings.uploads_dir / f"{uuid4().hex}_{Path(file.filename).name}"
    path.write_bytes(await file.read())
    validation = validate_csv(path)
    if not validation["is_valid"]:
        raise HTTPException(status_code=422, detail=validation)
    inserted = ingest_dataframe(db, pd.read_csv(path))
    predictions: list[dict[str, object]] = []
    if model_exists():
        predictions = predict_and_alert(db, pd.read_csv(path))
    return {"inserted_readings": inserted, "validation": validation, "predictions": predictions}
