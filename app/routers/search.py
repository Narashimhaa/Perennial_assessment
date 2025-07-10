import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db import SessionLocal
from app import crud, utils
from app.schemas import FilterMetadata, EmployeeSearchRequest, EmployeeOut, EmployeeStatus

logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/search")
def search_employees(
    request: Request,
    org_id: int = Query(..., gt=0, description="Organization ID must be positive"),
    search_query: Optional[str] = Query(None, alias="q", max_length=100, description="Search query for employee names and email"),
    status: Optional[List[EmployeeStatus]] = Query(None, description="Filter by employee status"),
    locations: Optional[List[str]] = Query(None, description="Filter by locations"),
    departments: Optional[List[str]] = Query(None, description="Filter by departments"),
    positions: Optional[List[str]] = Query(None, description="Filter by positions"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return (max 100)"),
    db: Session = Depends(get_db)
):
    logger.info(f"Search request for org_id={org_id}, search_query='{search_query}', filters={{status={status}, locations={locations}, departments={departments}, positions={positions}}}")

    columns = crud.get_org_columns(db, org_id)
    if not columns:
        raise HTTPException(status_code=404, detail="Organization config not found")

    employees = crud.search_employees(db, org_id, search_query, offset, limit, status, locations, departments, positions)
    return [utils.serialize_employee(emp, columns) for emp in employees]

@router.get("/filters/metadata", response_model=FilterMetadata)
def get_filter_metadata(org_id: int, db: Session = Depends(get_db)):
    return crud.get_filter_metadata(db, org_id)