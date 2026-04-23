from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.core.config import settings
from app.core.logging import logger
from app.db import base  # noqa: F401  (registra modelos no Base.metadata)
from app.db.base_class import Base
from app.db.seed import seed_initial_user
from app.db.session import SessionLocal, engine

app = FastAPI(title="APP_FC_26 — FastAPI JWT + Users")

origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_user(db)
    finally:
        db.close()
    logger.info("Database tables created and application startup complete")


app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
