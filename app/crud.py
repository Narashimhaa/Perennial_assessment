from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models import Employee, OrgConfig
from typing import Optional, List

def search_employees(db: Session, org_id: int, q: Optional[str], offset: int, limit: int,
                     status: Optional[List[str]], locations: Optional[List[str]],
                     departments: Optional[List[str]], positions: Optional[List[str]]):
    query = db.query(Employee).filter(Employee.org_id == org_id)

    if status:
        query = query.filter(Employee.status.in_(status))
    if locations:
        query = query.filter(Employee.location.in_(locations))
    if departments:
        query = query.filter(Employee.department.in_(departments))
    if positions:
        query = query.filter(Employee.position.in_(positions))
    if q:
        pattern = f"%{q.lower()}%"
        query = query.filter(or_(
            func.lower(Employee.first_name).like(pattern),
            func.lower(Employee.last_name).like(pattern),
            func.lower(Employee.email).like(pattern),
            func.lower(Employee.phone).like(pattern)
        ))

    return query.offset(offset).limit(limit).all()

def get_org_columns(db: Session, org_id: int) -> List[str]:
    config = db.query(OrgConfig).filter_by(org_id=org_id).first()
    if config and config.visible_columns:
        return config.visible_columns
    return []

def get_filter_metadata(db: Session, org_id: int):
    query = db.query(Employee).filter(Employee.org_id == org_id)
    return {
        "statuses": [r[0] for r in query.with_entities(Employee.status).distinct().all()],
        "locations": [r[0] for r in query.with_entities(Employee.location).distinct().all()],
        "departments": [r[0] for r in query.with_entities(Employee.department).distinct().all()],
        "positions": [r[0] for r in query.with_entities(Employee.position).distinct().all()],
    }