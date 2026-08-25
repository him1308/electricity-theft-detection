from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Alert, ConsumptionReading, Consumer, User
from app.schemas import ConsumerRead, ReadingRead


router = APIRouter()


def _consumer_row(db: Session, consumer: Consumer) -> ConsumerRead:
    avg = (
        db.query(func.avg(ConsumptionReading.energy_consumption))
        .filter(ConsumptionReading.consumer_id == consumer.consumer_id)
        .scalar()
        or 0
    )
    last = (
        db.query(func.max(ConsumptionReading.timestamp))
        .filter(ConsumptionReading.consumer_id == consumer.consumer_id)
        .scalar()
    )
    alert = (
        db.query(Alert)
        .filter(Alert.consumer_id == consumer.consumer_id, Alert.status != "Dismissed")
        .order_by(Alert.risk_score.desc())
        .first()
    )
    return ConsumerRead(
        consumer_id=consumer.consumer_id,
        name=consumer.name,
        location=consumer.location,
        meter_number=consumer.meter_number,
        account_status=consumer.account_status,
        average_consumption=round(float(avg), 2),
        risk_score=alert.risk_score if alert else 0,
        risk_level=alert.risk_level if alert else "Low",
        status="Suspicious" if alert and alert.risk_score >= 61 else "Normal",
        last_reading=last,
    )


@router.get("", response_model=list[ConsumerRead])
def list_consumers(
    search: str | None = None,
    risk: str | None = Query(default=None),
    location: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ConsumerRead]:
    query = db.query(Consumer)
    if search:
        query = query.filter(Consumer.consumer_id.contains(search) | Consumer.name.contains(search))
    if location:
        query = query.filter(Consumer.location == location)
    consumers = query.order_by(Consumer.consumer_id).offset(offset).limit(limit).all()
    rows = [_consumer_row(db, consumer) for consumer in consumers]
    if risk:
        rows = [row for row in rows if row.risk_level.lower() == risk.lower()]
    return rows


@router.get("/{consumer_id}", response_model=ConsumerRead)
def get_consumer(consumer_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ConsumerRead:
    consumer = db.query(Consumer).filter(Consumer.consumer_id == consumer_id).first()
    if not consumer:
        raise HTTPException(status_code=404, detail="Consumer not found")
    return _consumer_row(db, consumer)


@router.get("/{consumer_id}/consumption", response_model=list[ReadingRead])
def consumption(consumer_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[ReadingRead]:
    rows = (
        db.query(ConsumptionReading)
        .filter(ConsumptionReading.consumer_id == consumer_id)
        .order_by(ConsumptionReading.timestamp)
        .all()
    )
    return [
        ReadingRead(
            timestamp=row.timestamp,
            energy_consumption=row.energy_consumption,
            voltage=row.voltage,
            current=row.current,
            power_factor=row.power_factor,
        )
        for row in rows
    ]
