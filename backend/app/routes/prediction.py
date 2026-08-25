from io import StringIO

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.config import get_settings
from app.models import User
from app.schemas import PredictRequest, PredictionResult
from app.services.model_service import model_exists
from ml.predict import predict_dataframe


router = APIRouter()
settings = get_settings()


@router.post("/predict", response_model=list[PredictionResult])
def predict(payload: PredictRequest, _: User = Depends(get_current_user)) -> list[dict[str, object]]:
    if not model_exists():
        raise HTTPException(status_code=400, detail="Train the model before requesting predictions")
    df = pd.DataFrame([item.model_dump() for item in payload.readings])
    return predict_dataframe(df, settings.model_path)


@router.post("/predict/batch")
async def predict_batch(
    file: UploadFile = File(...),
    download: bool = False,
    _: User = Depends(get_current_user),
):
    if not model_exists():
        raise HTTPException(status_code=400, detail="Train the model before requesting predictions")
    df = pd.read_csv(file.file)
    results = predict_dataframe(df, settings.model_path)
    if not download:
        return results
    output = StringIO()
    pd.DataFrame(results).assign(reasons=lambda data: data["reasons"].apply("; ".join)).to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=prediction_results.csv"},
    )
