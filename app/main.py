import logging
from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import health, extraction, clean

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="REST API for parsing and clean HTML content and extracting main text.",
    version="0.1.0",
)

# Register routers
app.include_router(health.router)
app.include_router(extraction.router)
app.include_router(clean.router)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "health_check_url": "/health",
    }
