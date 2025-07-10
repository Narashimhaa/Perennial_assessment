from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, Employee, OrgConfig
from app.db import SessionLocal
from app.routers.search import get_db
import pytest

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/assessment"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db 

from app.rate_limiter import RateLimitMiddleware
app.user_middleware = [m for m in app.user_middleware if not isinstance(m.cls, type(RateLimitMiddleware))]

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(OrgConfig(org_id=1, visible_columns=["first_name", "last_name", "email", "phone", "department", "position", "location", "avatar_url"]))
    db.add_all([
        Employee(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            phone="+1-555-0101",
            org_id=1,
            status="ACTIVE",
            department="HR",
            position="Manager",
            location="NY",
            avatar_url="https://example.com/avatar1.jpg"
        ),
        Employee(
            first_name="Bob",
            last_name="Brown",
            email="bob@example.com",
            phone="+1-555-0102",
            org_id=1,
            status="NOT_STARTED",
            department="IT",
            position="Dev",
            location="SF",
            avatar_url="https://example.com/avatar2.jpg"
        )
    ])
    db.commit()
    db.close()

def test_search_employees():
    response = client.get("/employees/search?org_id=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert "first_name" in response.json()[0]

def test_search_filters_metadata():
    response = client.get("/employees/filters/metadata?org_id=1")
    assert response.status_code == 200
    metadata = response.json()
    assert "statuses" in metadata
    assert "locations" in metadata
    assert "departments" in metadata
    assert "positions" in metadata

def test_search_with_query():
    response = client.get("/employees/search?org_id=1&q=alice")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 0 

def test_search_with_status_filter():
    response = client.get("/employees/search?org_id=1&status=ACTIVE")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)

def test_search_pagination():
    response = client.get("/employees/search?org_id=1&limit=1&offset=0")
    assert response.status_code == 200
    results = response.json()
    assert len(results) <= 1

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
