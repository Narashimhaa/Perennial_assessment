import logging
import os
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import search
from app.rate_limiter import RateLimitMiddleware, limiter

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Employee Search API",
    description="A FastAPI-based employee search service with PostgreSQL backend, featuring rate limiting and configurable column visibility per organization.",
    version="1.0.0"
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, rate_limiter=limiter)

app.include_router(search.router, prefix="/employees", tags=["Search"])

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json():
    """Serve the OpenAPI JSON schema"""
    return JSONResponse(content=app.openapi())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Employee Search API"}

@app.on_event("startup")
async def startup_event():
    logger.info("Employee Search API starting up...")
    logger.info(f"Rate limiting: {os.getenv('RATE_LIMIT_REQUESTS', '5')} requests per {os.getenv('RATE_LIMIT_WINDOW', '60')} seconds")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Employee Search API shutting down...")
