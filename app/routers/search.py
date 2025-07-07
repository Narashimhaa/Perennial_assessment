from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db import SessionLocal
from app import crud, utils, rate_limiter
from app.schemas import FilterMetadata

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def search_employees(
    request: Request,
    org_id: int,
    q: Optional[str] = None,
    status: Optional[List[str]] = Query(None),
    locations: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None),
    positions: Optional[List[str]] = Query(None),
    offset: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    ip = request.client.host
    if not rate_limiter.limiter.is_allowed(ip):
        raise HTTPException(status_code=429, detail="Too many requests")

    columns = crud.get_org_columns(db, org_id)
    if not columns:
        raise HTTPException(status_code=404, detail="Organization config not found")

    employees = crud.search_employees(db, org_id, q, offset, limit, status, locations, departments, positions)
    return [utils.serialize_employee(emp, columns) for emp in employees]

@router.get("/filters/metadata", response_model=FilterMetadata)
def get_filter_metadata(org_id: int, db: Session = Depends(get_db)):
    return crud.get_filter_metadata(db, org_id)