from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    username: str
    role: str


class AdminUserRead(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime


class UserRoleUpdate(BaseModel):
    role: str = Field(pattern="^(Admin|Analyst|admin|analyst)$")


class ConsumerRead(BaseModel):
    consumer_id: str
    name: str
    location: str
    meter_number: str
    account_status: str
    average_consumption: float = 0
    risk_score: int = 0
    risk_level: str = "Low"
    status: str = "Normal"
    last_reading: datetime | None = None


class ReadingRead(BaseModel):
    timestamp: datetime
    energy_consumption: float
    voltage: float | None = None
    current: float | None = None
    power_factor: float | None = None


class AlertRead(BaseModel):
    id: int
    consumer_id: str
    risk_score: int
    risk_level: str
    reason: str
    status: str
    created_at: datetime


class AlertStatusUpdate(BaseModel):
    status: str = Field(pattern="^(New|Under Investigation|Verified|Dismissed)$")


class SummaryRead(BaseModel):
    total_consumers: int
    total_readings: int
    suspicious_consumers: int
    critical_alerts: int
    average_consumption: float
    average_risk_score: float
    risk_distribution: dict[str, int]
    daily_consumption: list[dict[str, Any]]
    suspicious_over_time: list[dict[str, Any]]


class AdminDashboardRead(BaseModel):
    total_consumers: int
    high_risk_consumers: int
    active_alerts: int
    total_analysts: int
    total_users: int
    data_records: int
    model_performance: float | None = None
    latest_data_upload: datetime | None = None


class AnalystDashboardRead(BaseModel):
    consumers_analyzed: int
    high_risk_consumers: int
    medium_risk_consumers: int
    pending_investigations: int
    active_alerts: int
    recent_suspicious_consumers: list[ConsumerRead]


class UploadedDatasetRead(BaseModel):
    filename: str
    size_bytes: int
    uploaded_at: datetime
    records: int | None = None
    status: str


class DataManagementRead(BaseModel):
    total_consumers: int
    total_readings: int
    uploaded_datasets: list[UploadedDatasetRead]


class SystemSettingsRead(BaseModel):
    app_name: str
    api_prefix: str
    access_token_expire_minutes: int
    cors_origins: list[str]
    model_path: str
    database_backend: str
    uploads_directory: str
    configuration_source: str


class PredictionReading(BaseModel):
    consumer_id: str
    timestamp: datetime
    energy_consumption: float
    voltage: float | None = None
    current: float | None = None
    power_factor: float | None = None
    meter_status: str | None = None


class PredictRequest(BaseModel):
    readings: list[PredictionReading]


class PredictionResult(BaseModel):
    consumer_id: str
    risk_score: int
    risk_level: str
    anomaly_status: str
    reasons: list[str]
    anomaly_score: float


class ModelStatus(BaseModel):
    is_trained: bool
    model_path: str
    model_name: str | None = None
    version: str | None = None
    trained_at: datetime | None = None
    samples: int = 0
    features: int = 0


class ModelMetricsRead(BaseModel):
    model_name: str
    version: str
    model_type: str
    trained_at: datetime
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1_score: float | None = None
    roc_auc: float | None = None
    samples: int
    features: int
    notes: str
