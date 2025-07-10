"""
Integration tests that use a real database connection.
These tests are slower but verify end-to-end functionality.
Run with: pytest tests/test_integration.py -v
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, Employee, OrgConfig
from app.routers.search import get_db
import pytest
import os

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/assessment_test")

engine = create_engine(TEST_DATABASE_URL)
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
def setup_test_db():
    """Setup test database with sample data"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        db.add(OrgConfig(
            org_id=1, 
            visible_columns=["first_name", "last_name", "email", "phone", "department", "position", "location", "avatar_url"]
        ))
        
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
    finally:
        db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

def test_integration_search_employees():
    """Integration test for employee search with real database"""
    response = client.get("/employees/search?org_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert "first_name" in data[0]

def test_integration_search_with_filters():
    """Integration test for search with filters"""
    response = client.get("/employees/search?org_id=1&status=ACTIVE")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_integration_filter_metadata():
    """Integration test for filter metadata endpoint"""
    response = client.get("/employees/filters/metadata?org_id=1")
    assert response.status_code == 200
    metadata = response.json()
    assert "statuses" in metadata
    assert "locations" in metadata
    assert "departments" in metadata
    assert "positions" in metadata

def test_integration_org_not_found():
    """Integration test for non-existent organization"""
    response = client.get("/employees/search?org_id=999")
    assert response.status_code == 404
    assert "Organization config not found" in response.json()["detail"]
