from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, Employee, OrgConfig
from app.db import SessionLocal
import pytest

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/assessment"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

# ✅ Proper dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[SessionLocal] = override_get_db  # <-- FIXED

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(OrgConfig(org_id=1, visible_columns=["first_name", "last_name", "email"]))
    db.add_all([
        Employee(first_name="Alice", last_name="Smith", email="alice@example.com", org_id=1, status="ACTIVE", department="HR", position="Manager", location="NY"),
        Employee(first_name="Bob", last_name="Brown", email="bob@example.com", org_id=1, status="NOT_STARTED", department="IT", position="Dev", location="SF")
    ])
    db.commit()
    db.close()

def test_search_employees():
    response = client.get("/search/?org_id=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert "first_name" in response.json()[0]

def test_search_filters_metadata():
    response = client.get("/search/filters/metadata?org_id=1")
    assert response.status_code == 200
    metadata = response.json()
    assert "statuses" in metadata
    assert "locations" in metadata
    assert "departments" in metadata
    assert "positions" in metadata
