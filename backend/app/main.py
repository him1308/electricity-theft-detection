import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import seed_default_users
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.routes import api_router
from app.services.data_service import ensure_demo_data


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    with SessionLocal() as db:
        seed_default_users(db)
        ensure_demo_data(db)
    logger.info("API startup complete")
    yield


app = FastAPI(
    title=settings.app_name,
    description="Energy analytics platform for detecting suspicious smart meter consumption patterns.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)
