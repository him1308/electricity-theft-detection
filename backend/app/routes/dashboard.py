from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin, require_analyst
from app.config import get_settings
from app.database import get_db
from app.models import Alert, ConsumptionReading, Consumer, ModelMetadata, User
from app.routes.consumers import _consumer_row
from app.schemas import AdminDashboardRead, AnalystDashboardRead, SummaryRead
from app.services.reporting_service import daily_consumption, risk_distribution, suspicious_over_time


router = APIRouter()
settings = get_settings()


def _latest_upload_time(upload_dir: Path):
    uploads = [path for path in upload_dir.glob("*.csv") if path.is_file()]
    if not uploads:
        return None
    return max(path.stat().st_mtime for path in uploads)


def _latest_upload_datetime(upload_dir: Path):
    timestamp = _latest_upload_time(upload_dir)
    if timestamp is None:
        return None
    from datetime import datetime

    return datetime.fromtimestamp(timestamp)


def _open_alert_query(db: Session):
    return db.query(Alert).filter(Alert.status != "Dismissed")


def _risk_consumer_count(db: Session, *levels: str) -> int:
    return (
        db.query(Alert.consumer_id)
        .filter(Alert.status != "Dismissed", Alert.risk_level.in_(levels))
        .distinct()
        .count()
    )


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


@router.get("/dashboard/admin", response_model=AdminDashboardRead)
def admin_dashboard(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> AdminDashboardRead:
    metadata = db.query(ModelMetadata).order_by(ModelMetadata.trained_at.desc()).first()
    model_performance = None
    if metadata:
        model_performance = metadata.f1_score or metadata.accuracy or metadata.roc_auc

    return AdminDashboardRead(
        total_consumers=db.query(Consumer).count(),
        high_risk_consumers=_risk_consumer_count(db, "High", "Critical"),
        active_alerts=_open_alert_query(db).count(),
        total_analysts=db.query(User).filter(func.lower(User.role) == "analyst").count(),
        total_users=db.query(User).count(),
        data_records=db.query(ConsumptionReading).count(),
        model_performance=round(float(model_performance), 4) if model_performance is not None else None,
        latest_data_upload=_latest_upload_datetime(settings.uploads_dir),
    )


@router.get("/dashboard/analyst", response_model=AnalystDashboardRead)
def analyst_dashboard(db: Session = Depends(get_db), _: User = Depends(require_analyst)) -> AnalystDashboardRead:
    suspicious_ids = [
        row[0]
        for row in (
            _open_alert_query(db)
            .filter(Alert.risk_level.in_(["High", "Critical"]))
            .order_by(Alert.risk_score.desc(), Alert.created_at.desc())
            .with_entities(Alert.consumer_id)
            .distinct()
            .limit(8)
            .all()
        )
    ]
    consumers = db.query(Consumer).filter(Consumer.consumer_id.in_(suspicious_ids)).all() if suspicious_ids else []
    consumer_map = {consumer.consumer_id: consumer for consumer in consumers}

    return AnalystDashboardRead(
        consumers_analyzed=db.query(ConsumptionReading.consumer_id).distinct().count(),
        high_risk_consumers=_risk_consumer_count(db, "High", "Critical"),
        medium_risk_consumers=_risk_consumer_count(db, "Medium"),
        pending_investigations=db.query(Alert)
        .filter(Alert.status.in_(["New", "Under Investigation"]))
        .count(),
        active_alerts=_open_alert_query(db).count(),
        recent_suspicious_consumers=[
            _consumer_row(db, consumer_map[consumer_id])
            for consumer_id in suspicious_ids
            if consumer_id in consumer_map
        ],
    )
