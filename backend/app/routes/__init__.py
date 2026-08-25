from fastapi import APIRouter

from app.routes import admin, alerts, auth, consumers, dashboard, data, model, prediction

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(consumers.router, prefix="/consumers", tags=["consumers"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(model.router, prefix="/model", tags=["model"])
api_router.include_router(prediction.router, tags=["prediction"])
