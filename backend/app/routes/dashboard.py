from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Alert, ConsumptionReading, Consumer, User
from app.schemas import SummaryRead
from app.services.reporting_service import daily_consumption, risk_distribution, suspicious_over_time


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "electricity-theft-detection"}


@router.get("/dashboard/summary", response_model=SummaryRead)
def summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> SummaryRead:
    total_consumers = db.query(Consumer).count()
    total_readings = db.query(ConsumptionReading).count()
    suspicious_consumers = db.query(Alert.consumer_id).filter(Alert.status != "Dismissed").distinct().count()
    critical_alerts = db.query(Alert).filter(Alert.risk_level == "Critical", Alert.status != "Dismissed").count()
    average_consumption = db.query(func.avg(ConsumptionReading.energy_consumption)).scalar() or 0
    average_risk_score = db.query(func.avg(Alert.risk_score)).scalar() or 0
    return SummaryRead(
        total_consumers=total_consumers,
        total_readings=total_readings,
        suspicious_consumers=suspicious_consumers,
        critical_alerts=critical_alerts,
        average_consumption=round(float(average_consumption), 2),
        average_risk_score=round(float(average_risk_score), 2),
        risk_distribution=risk_distribution(db),
        daily_consumption=daily_consumption(db),
        suspicious_over_time=suspicious_over_time(db),
    )
