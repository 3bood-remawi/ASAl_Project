from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import contracts
from app.core.config import settings
from app.core.cosmos import create_database_and_containers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup, not at import, so the app can be imported without Cosmos running
    create_database_and_containers()
    yield


app = FastAPI(
    title="Contract Intelligence Platform API",
    version="0.1.0",
    lifespan=lifespan,
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
