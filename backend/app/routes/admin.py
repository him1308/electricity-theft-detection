from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import normalize_role, require_admin
from app.config import get_settings
from app.database import get_db
from app.models import ConsumptionReading, Consumer, User
from app.schemas import AdminUserRead, DataManagementRead, SystemSettingsRead, UploadedDatasetRead, UserRoleUpdate


router = APIRouter()
settings = get_settings()


def _canonical_role(role: str) -> str:
    return "Admin" if role.lower() == "admin" else "Analyst"


def _csv_record_count(path) -> int | None:
    try:
        return int(pd.read_csv(path, usecols=[0]).shape[0])
    except Exception:
        return None


@router.get("/users", response_model=list[AdminUserRead])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[User]:
    return db.query(User).order_by(User.created_at.desc(), User.username).all()


@router.patch("/users/{user_id}/role", response_model=AdminUserRead)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    next_role = _canonical_role(payload.role)
    if normalize_role(user.role) == "admin" and next_role != "Admin":
        admin_count = db.query(User).filter(func.lower(User.role) == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one admin user is required")

    user.role = next_role
    db.commit()
    db.refresh(user)
    return user


@router.get("/data", response_model=DataManagementRead)
def data_management(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> DataManagementRead:
    uploaded_datasets = [
        UploadedDatasetRead(
            filename=path.name,
            size_bytes=path.stat().st_size,
            uploaded_at=datetime.fromtimestamp(path.stat().st_mtime),
            records=_csv_record_count(path),
            status="Stored",
        )
        for path in sorted(settings.uploads_dir.glob("*.csv"), key=lambda item: item.stat().st_mtime, reverse=True)
        if path.is_file()
    ]
    return DataManagementRead(
        total_consumers=db.query(Consumer).count(),
        total_readings=db.query(ConsumptionReading).count(),
        uploaded_datasets=uploaded_datasets,
    )


@router.get("/settings", response_model=SystemSettingsRead)
def system_settings(_: User = Depends(require_admin)) -> SystemSettingsRead:
    database_backend = settings.database_url.split(":", 1)[0]
    return SystemSettingsRead(
        app_name=settings.app_name,
        api_prefix=settings.api_prefix,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        cors_origins=settings.cors_origins,
        model_path=settings.model_path,
        database_backend=database_backend,
        uploads_directory=str(settings.uploads_dir),
        configuration_source="Environment variables and backend application configuration",
    )
