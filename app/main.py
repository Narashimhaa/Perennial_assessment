from fastapi import FastAPI
from app.routers import search

app = FastAPI(title="Employee Search API")

app.include_router(search.router, prefix="/search", tags=["Search"])
