from functools import lru_cache
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings:
    app_name: str = "Electricity Theft Detection API"
    api_prefix: str = "/api"
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'electricity_theft.db'}"
    )
    secret_key: str = os.getenv("SECRET_KEY", "change-this-development-secret")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    algorithm: str = "HS256"
    model_path: str = os.getenv("MODEL_PATH", str(BASE_DIR / "ml" / "model.joblib"))
    default_cors_origins: str = ",".join(
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
    )
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", default_cors_origins).split(",")
        if origin.strip()
    ]
    uploads_dir: Path = BASE_DIR / "data" / "uploads"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.model_path).parent.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
    return settings
