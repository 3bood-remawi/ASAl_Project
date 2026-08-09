from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 - Alembic needs every model imported
from app.api.routes import contracts
from app.core.config import settings

app = FastAPI(
    title="Contract Intelligence Platform API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])


@app.get("/")
def root():
    return {"message": "Contract Intelligence Platform API is running"}