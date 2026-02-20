"""
TalentIQ — AI-Powered Career Intelligence Platform
Main FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core import vector_store
from app.routers import upload, analyze

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    logger.info("🚀 Starting %s v%s …", settings.APP_NAME, settings.APP_VERSION)
    vector_store.initialise()
    logger.info("✅ Vector store ready — %d roles indexed", len(vector_store.get_roles()))
    yield
    logger.info("👋 Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Career Intelligence Platform — Smarter Careers Start Here.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS — allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "TalentIQ backend running"}

# --- Routers ---
app.include_router(upload.router)
app.include_router(analyze.router)
