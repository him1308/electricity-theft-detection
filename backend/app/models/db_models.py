from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="Analyst")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Consumer(Base):
    __tablename__ = "consumers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consumer_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), default="Unknown Consumer")
    location: Mapped[str] = mapped_column(String(120), default="Unknown")
    meter_number: Mapped[str] = mapped_column(String(80), default="")
    account_status: Mapped[str] = mapped_column(String(40), default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    readings: Mapped[list["ConsumptionReading"]] = relationship(back_populates="consumer", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="consumer", cascade="all, delete-orphan")


class ConsumptionReading(Base):
    __tablename__ = "consumption_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consumer_id: Mapped[str] = mapped_column(String(80), ForeignKey("consumers.consumer_id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    energy_consumption: Mapped[float] = mapped_column(Float)
    voltage: Mapped[float | None] = mapped_column(Float, nullable=True)
    current: Mapped[float | None] = mapped_column(Float, nullable=True)
    power_factor: Mapped[float | None] = mapped_column(Float, nullable=True)
    meter_status: Mapped[str | None] = mapped_column(String(60), nullable=True)

    consumer: Mapped[Consumer] = relationship(back_populates="readings")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consumer_id: Mapped[str] = mapped_column(String(80), ForeignKey("consumers.consumer_id"), index=True)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="New")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    consumer: Mapped[Consumer] = relationship(back_populates="alerts")


class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_name: Mapped[str] = mapped_column(String(80))
    version: Mapped[str] = mapped_column(String(40), default="1.0.0")
    model_type: Mapped[str] = mapped_column(String(40), default="anomaly")
    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    recall: Mapped[float | None] = mapped_column(Float, nullable=True)
    f1_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    roc_auc: Mapped[float | None] = mapped_column(Float, nullable=True)
    samples: Mapped[int] = mapped_column(Integer, default=0)
    features: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
