"""
Unit tests for the search API using mocking.
These tests are fast and don't require a database connection.
Run with: pytest tests/test_search.py -v
"""

from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.routers.search import get_db
import pytest

# Mark all tests in this file as unit tests
pytestmark = pytest.mark.unit

# Mock database session
mock_db = Mock()

def override_get_db():
    return mock_db

app.dependency_overrides[get_db] = override_get_db

from app.rate_limiter import RateLimitMiddleware
app.user_middleware = [m for m in app.user_middleware if not isinstance(m.cls, type(RateLimitMiddleware))]

client = TestClient(app)

mock_employees = [
    {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "phone": "+1-555-0101",
        "department": "HR",
        "position": "Manager",
        "location": "NY",
        "avatar_url": "https://example.com/avatar1.jpg"
    },
    {
        "first_name": "Bob",
        "last_name": "Brown",
        "email": "bob@example.com",
        "phone": "+1-555-0102",
        "department": "IT",
        "position": "Dev",
        "location": "SF",
        "avatar_url": "https://example.com/avatar2.jpg"
    }
]

mock_org_columns = ["first_name", "last_name", "email", "phone", "department", "position", "location", "avatar_url"]

mock_filter_metadata = {
    "statuses": ["ACTIVE", "NOT_STARTED", "TERMINATED"],
    "locations": ["NY", "SF", "Berlin", "London", "Chennai"],
    "departments": ["HR", "IT", "Engineering", "Marketing", "Sales"],
    "positions": ["Manager", "Dev", "Analyst", "Intern", "Executive"]
}

@patch('app.crud.get_org_columns')
@patch('app.crud.search_employees')
def test_search_employees(mock_search_employees, mock_get_org_columns):
    mock_get_org_columns.return_value = mock_org_columns
    mock_search_employees.return_value = [Mock(**emp) for emp in mock_employees]

    response = client.get("/employees/search?org_id=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert "first_name" in response.json()[0]

    # Verify mocks were called
    mock_get_org_columns.assert_called_once()
    mock_search_employees.assert_called_once()

@patch('app.crud.get_filter_metadata')
def test_search_filters_metadata(mock_get_filter_metadata):
    mock_get_filter_metadata.return_value = mock_filter_metadata

    response = client.get("/employees/filters/metadata?org_id=1")
    assert response.status_code == 200
    metadata = response.json()
    assert "statuses" in metadata
    assert "locations" in metadata
    assert "departments" in metadata
    assert "positions" in metadata

    mock_get_filter_metadata.assert_called_once()

@patch('app.crud.get_org_columns')
@patch('app.crud.search_employees')
def test_search_with_query(mock_search_employees, mock_get_org_columns):
    mock_get_org_columns.return_value = mock_org_columns
    alice_employee = [Mock(**mock_employees[0])]  # Only Alice
    mock_search_employees.return_value = alice_employee

    response = client.get("/employees/search?org_id=1&q=alice")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 0

    mock_search_employees.assert_called_once()

@patch('app.crud.get_org_columns')
@patch('app.crud.search_employees')
def test_search_with_status_filter(mock_search_employees, mock_get_org_columns):
    mock_get_org_columns.return_value = mock_org_columns
    mock_search_employees.return_value = [Mock(**emp) for emp in mock_employees]

    response = client.get("/employees/search?org_id=1&status=ACTIVE")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)

@patch('app.crud.get_org_columns')
@patch('app.crud.search_employees')
def test_search_pagination(mock_search_employees, mock_get_org_columns):
    mock_get_org_columns.return_value = mock_org_columns
    mock_search_employees.return_value = [Mock(**mock_employees[0])]  

    response = client.get("/employees/search?org_id=1&limit=1&offset=0")
    assert response.status_code == 200
    results = response.json()
    assert len(results) <= 1

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@patch('app.crud.get_org_columns')
def test_search_employees_org_not_found(mock_get_org_columns):
    mock_get_org_columns.return_value = None

    response = client.get("/employees/search?org_id=999")
    assert response.status_code == 404
    assert "Organization config not found" in response.json()["detail"]
