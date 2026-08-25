from __future__ import annotations

from collections import Counter

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Alert, ConsumptionReading, Consumer


RISK_LEVELS = ["Low", "Medium", "High", "Critical"]


def risk_distribution(db: Session) -> dict[str, int]:
    counts = Counter({level: 0 for level in RISK_LEVELS})
    for level, count in db.query(Alert.risk_level, func.count(Alert.id)).group_by(Alert.risk_level).all():
        counts[level] = count
    normal_consumers = db.query(Consumer).count() - db.query(Alert.consumer_id).distinct().count()
    counts["Low"] += max(normal_consumers, 0)
    return dict(counts)


def daily_consumption(db: Session) -> list[dict[str, object]]:
    rows = (
        db.query(func.date(ConsumptionReading.timestamp), func.sum(ConsumptionReading.energy_consumption))
        .group_by(func.date(ConsumptionReading.timestamp))
        .order_by(func.date(ConsumptionReading.timestamp))
        .limit(45)
        .all()
    )
    return [{"date": str(day), "consumption": round(total or 0, 2)} for day, total in rows]


def suspicious_over_time(db: Session) -> list[dict[str, object]]:
    rows = (
        db.query(func.date(Alert.created_at), func.count(Alert.id))
        .group_by(func.date(Alert.created_at))
        .order_by(func.date(Alert.created_at))
        .limit(45)
        .all()
    )
    return [{"date": str(day), "alerts": count} for day, count in rows]
