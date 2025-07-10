# Employee Search API

A FastAPI-based employee search service with PostgreSQL backend, featuring rate limiting and configurable column visibility per organization.

## Features

- **Employee Search**: Full-text search across employee records
- **Filtering**: Filter by status, location, department, and position
- **Rate Limiting**: Configurable rate limiting with middleware (default: 5 requests per minute per IP)
- **Organization Configuration**: Configurable visible columns per organization
- **Pagination**: Offset-based pagination support with validation
- **Health Checks**: Built-in health monitoring
- **Database Migrations**: Alembic integration for schema management
- **Input Validation**: Comprehensive Pydantic model validation
- **Logging**: Configurable logging with structured output
- **OpenAPI Integration**: Full OpenAPI 3.0 specification support

## Docker Containerization

### Quick Start with Docker Compose

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd Perennial_assessment
   cp .env.example .env
   ```

2. **Configure environment (optional)**:
   ```bash
   # Edit .env file to customize settings
   nano .env

   # Key settings:
   # RATE_LIMIT_REQUESTS=5        # Requests per minute
   # RATE_LIMIT_WINDOW=60         # Rate limit window in seconds
   # LOG_LEVEL=INFO               # Logging level
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d --build
   ```

4. **Verify setup**:
   ```bash
   # Check if services are running and healthy
   docker-compose ps

   # Test the health endpoint
   curl http://localhost:8000/health

   # Test the search API
   curl "http://localhost:8000/employees/search?org_id=1&limit=5"
   ```

5. **Access the API**:
   - Health Check: http://localhost:8000/health
   - API Documentation: http://localhost:8000/docs
   - OpenAPI JSON: http://localhost:8000/openapi.json
   - API Base URL: http://localhost:8000
   - Database: localhost:5433 (mapped from container port 5432)

### Testing Docker Setup

```bash
# Run comprehensive Docker tests (uses test configuration with stricter rate limits)
./docker-test.sh

# This script will:
# - Build and start all services with test configuration
# - Test health endpoints
# - Verify API functionality
# - Test rate limiting with aggressive settings (3 requests/minute)
# - Validate OpenAPI integration
# - Show detailed rate limiting behavior
```

### Testing Rate Limiting Specifically

```bash
# Test rate limiter logic (unit test)
python test_rate_limiter_unit.py

# Test rate limiting against running API
./test-rate-limiting.sh

# Manual rate limiting test
for i in {1..10}; do
  echo "Request $i: $(curl -s -w "%{http_code}" "http://localhost:8000/employees/search?org_id=1" -o /dev/null)"
  sleep 0.1  # Small delay between requests
done
```

### Development Setup

```bash
# Start with live reload for development
docker-compose up --build

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Reset everything (including volumes)
docker-compose down -v --remove-orphans
```



## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   FastAPI App   │    │   PostgreSQL    │
│  (Reverse Proxy)│────│   (Python)      │────│   (Database)    │
│     Port 80     │    │   Port 8000     │    │   Port 5432     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
├── app/                    # Application code
│   ├── main.py            # FastAPI application entry point
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── crud.py            # Database operations
│   ├── db.py              # Database configuration
│   ├── rate_limiter.py    # Rate limiting implementation
│   ├── utils.py           # Utility functions
│   └── routers/           # API route handlers
├── tests/                 # Test files
├── Dockerfile             # Container definition
├── docker-compose.yml     # Service orchestration
├── nginx.conf             # Nginx configuration
├── init.sql               # Database initialization
└── requirements.txt       # Python dependencies
```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API Endpoints

### 1. Search Employees

**Endpoint:** `GET /employees/search`

**Description:** Search and filter employees within an organization with full-text search capabilities.

**Request Signature:**
```http
GET /employees/search?org_id={int}&q={string}&status={array}&locations={array}&departments={array}&positions={array}&limit={int}&offset={int}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `org_id` | `int` | ✅ Yes | - | Organization ID (1, 2, or 3) |
| `q` | `string` | ❌ No | - | Search query (searches across first_name, last_name, email, phone) |
| `status` | `array[string]` | ❌ No | - | Filter by employee status |
| `locations` | `array[string]` | ❌ No | - | Filter by office locations |
| `departments` | `array[string]` | ❌ No | - | Filter by departments |
| `positions` | `array[string]` | ❌ No | - | Filter by job positions |
| `limit` | `int` | ❌ No | `50` | Number of results per page (max: 100) |
| `offset` | `int` | ❌ No | `0` | Pagination offset |

**Response Schema:**
```json
[
  {
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "phone": "string",
    "department": "string",
    "position": "string",
    "location": "string",
    "avatar_url": "string"
  }
]
```

**Example Requests:**

```bash
# Basic search for organization 1
curl "http://localhost:8000/employees/search?org_id=1"

# Search with text query
curl "http://localhost:8000/employees/search?org_id=1&q=alice"

# Filter by status
curl "http://localhost:8000/employees/search?org_id=1&status=ACTIVE&status=NOT_STARTED"

# Multiple filters with pagination
curl "http://localhost:8000/employees/search?org_id=1&departments=Engineering&locations=New%20York&limit=10&offset=0"

# Complex search
curl "http://localhost:8000/employees/search?org_id=2&q=john&status=ACTIVE&departments=Engineering&departments=Marketing&limit=25"
```

**Example Response:**
```json
[
  {
    "first_name": "Alice",
    "last_name": "Smith",
    "email": "alice.smith@example.com",
    "department": "Engineering",
    "position": "Manager"
  },
  {
    "first_name": "Bob",
    "last_name": "Johnson",
    "email": "bob.johnson@example.com",
    "department": "Engineering",
    "position": "Developer"
  }
]
```

---

### 2. Get Filter Metadata

**Endpoint:** `GET /search/filters/metadata`

**Description:** Retrieve all available filter options for an organization.

**Request Signature:**
```http
GET /search/filters/metadata?org_id={int}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `org_id` | `int` | ✅ Yes | Organization ID |

**Response Schema:**
```json
{
  "statuses": ["string"],
  "locations": ["string"],
  "departments": ["string"],
  "positions": ["string"]
}
```

**Example Request:**
```bash
curl "http://localhost:8000/employees/filters/metadata?org_id=1"
```

**Example Response:**
```json
{
  "statuses": ["ACTIVE", "NOT_STARTED", "TERMINATED"],
  "locations": ["New York", "San Francisco", "Berlin", "London", "Chennai"],
  "departments": ["Engineering", "Marketing", "Sales", "HR", "Support"],
  "positions": ["Manager", "Developer", "Analyst", "Intern", "Executive"]
}
```

---

## Developer Usage Guide

### Quick Start for Developers

1. **Clone and Start:**
   ```bash
   git clone <repository-url>
   cd Perennial_assessment
   docker compose up -d
   ```

2. **Verify Setup:**
   ```bash
   # Check services are running
   docker compose ps

   # Test API health
   curl http://localhost:8000/docs
   ```

3. **Explore the Data:**
   ```bash
   # Get all employees for org 1
   curl "http://localhost:8000/search/?org_id=1" | jq '.[0:3]'

   # Check available filters
   curl "http://localhost:8000/search/filters/metadata?org_id=1" | jq
   ```

### Rate Limiting

The API implements configurable rate limiting to prevent abuse:
- **Default Limit**: 5 requests per minute per IP address
- **Configurable**: Set via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW` environment variables
- **Response**: HTTP 429 when limit exceeded with `Retry-After` header
- **Scope**: Applied per IP address (supports proxy headers)

**Configuration:**
```bash
# In .env or docker-compose.yml
RATE_LIMIT_REQUESTS=5    # Number of requests allowed
RATE_LIMIT_WINDOW=60     # Time window in seconds
```

**Testing Rate Limiting:**
```bash
# Quick test with default settings (may need 6+ rapid requests)
for i in {1..10}; do
  echo "Request $i: $(curl -s -w "%{http_code}" "http://localhost:8000/employees/search?org_id=1" -o /dev/null)"
done

# Comprehensive rate limiting test
./test-rate-limiting.sh

# Unit test for rate limiter logic
python test_rate_limiter_unit.py
```

**Rate Limiting Features:**
- ✅ Memory leak prevention with automatic cleanup
- ✅ Failed requests count towards limit
- ✅ Proxy-aware IP detection (X-Forwarded-For, X-Real-IP)
- ✅ Configurable via environment variables
- ✅ Proper HTTP 429 responses with structured JSON and retry headers
- ✅ No internal server errors - always returns meaningful responses

**Rate Limit Response Format:**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "detail": "Rate limit: 5 requests per 60 seconds",
  "retry_after": 60
}
```

**Testing Rate Limit Responses:**
```bash
# Test that rate limiting returns proper JSON (not 500 errors)
python test_rate_limit_response.py
```

### Organization Data Structure

The system supports multiple organizations with configurable column visibility:

| Org ID | Visible Columns |
|--------|----------------|
| 1 | `first_name`, `last_name`, `department`, `position` |
| 2 | `first_name`, `email`, `phone`, `location` |
| 3 | `first_name`, `last_name`, `department`, `location`, `position` |

### Search Behavior

**Text Search (`q` parameter):**
- Case-insensitive partial matching
- Searches across: `first_name`, `last_name`, `email`, `phone`
- Uses PostgreSQL `LIKE` with wildcards

**Filter Behavior:**
- Multiple values for same filter = OR logic
- Different filters = AND logic
- Example: `departments=Engineering&departments=Sales&status=ACTIVE`
  - Returns: (Engineering OR Sales) AND ACTIVE

### Error Handling

**Common HTTP Status Codes:**

| Code | Description | Example |
|------|-------------|---------|
| `200` | Success | Valid request with results |
| `404` | Not Found | Invalid `org_id` |
| `422` | Validation Error | Invalid parameter types |
| `429` | Rate Limited | Too many requests |
| `500` | Server Error | Database connection issues |

**Error Response Format:**
```json
{
  "detail": "Organization config not found"
}
```

### Performance Considerations

**Pagination:**
- Use `limit` and `offset` for large result sets
- Maximum `limit`: 100 records
- Default `limit`: 50 records

**Indexing:**
- Database includes indexes on commonly filtered fields
- Text search is optimized with lowercase indexes
- Org-based queries are highly optimized

**Caching Recommendations:**
- Cache filter metadata responses (changes infrequently)
- Implement client-side caching for repeated searches
- Consider Redis for enhanced performance

---

## Testing & Integration

### API Testing Examples

**Using cURL:**
```bash
# Test basic functionality
curl -X GET "http://localhost:8000/search/?org_id=1&limit=5" \
  -H "accept: application/json"

# Test with complex filters
curl -X GET "http://localhost:8000/search/" \
  -G \
  -d "org_id=1" \
  -d "q=alice" \
  -d "status=ACTIVE" \
  -d "departments=Engineering" \
  -d "limit=10" \
  -H "accept: application/json"
```

**Using Python requests:**
```python
import requests

# Basic search
response = requests.get(
    "http://localhost:8000/search/",
    params={"org_id": 1, "limit": 5}
)
employees = response.json()

# Advanced search with filters
response = requests.get(
    "http://localhost:8000/search/",
    params={
        "org_id": 1,
        "q": "alice",
        "status": ["ACTIVE", "NOT_STARTED"],
        "departments": ["Engineering", "Marketing"],
        "limit": 20
    }
)
```

**Using JavaScript/Node.js:**
```javascript
// Using fetch API
const searchEmployees = async (orgId, filters = {}) => {
  const params = new URLSearchParams({
    org_id: orgId,
    ...filters
  });

  const response = await fetch(`http://localhost:8000/search/?${params}`);
  return response.json();
};

// Usage
const employees = await searchEmployees(1, {
  q: "john",
  status: "ACTIVE",
  limit: 10
});
```

### Integration Patterns

**Frontend Integration:**
```javascript
// React/Vue component example
const useEmployeeSearch = (orgId) => {
  const [employees, setEmployees] = useState([]);
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(false);

  const searchEmployees = async (searchParams) => {
    setLoading(true);
    try {
      const response = await fetch(`/search/?org_id=${orgId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchParams)
      });
      const data = await response.json();
      setEmployees(data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return { employees, searchEmployees, loading };
};
```

**Backend Integration:**
```python
# FastAPI client example
from httpx import AsyncClient

class EmployeeSearchClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def search_employees(self, org_id: int, **filters):
        async with AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search/",
                params={"org_id": org_id, **filters}
            )
            return response.json()

    async def get_filter_metadata(self, org_id: int):
        async with AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search/filters/metadata",
                params={"org_id": org_id}
            )
            return response.json()
```

---

## Database Schema

### Tables

**employees**
```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    department VARCHAR(100),
    position VARCHAR(100),
    location VARCHAR(255),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    org_id INTEGER
);
```

**org_column_config**
```sql
CREATE TABLE org_column_config (
    org_id SERIAL PRIMARY KEY,
    visible_columns TEXT[]
);
```

### Sample Data

The database is pre-populated with:
- **500+ employees** across 3 organizations
- **Realistic data distribution** across departments, locations, and positions
- **Test records** with known values for easier testing

### Direct Database Access

```bash
# Connect to PostgreSQL
docker compose exec db psql -U postgres -d assessment

# Useful queries
SELECT COUNT(*) FROM employees;
SELECT DISTINCT department FROM employees;
SELECT org_id, COUNT(*) FROM employees GROUP BY org_id;
```

---



## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/assessment` |
| `POSTGRES_DB` | Database name | `assessment` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `RATE_LIMIT_REQUESTS` | Number of requests allowed per window | `5` |
| `RATE_LIMIT_WINDOW` | Rate limit window in seconds | `60` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

### Rate Limiting

The API implements rate limiting (5 requests per minute per IP). This can be configured in `app/rate_limiter.py`.

## 🧪 Testing

### Run Tests with Docker

```bash
# Run tests in container
docker-compose exec app python -m pytest tests/ -v

# Run tests with coverage
docker-compose exec app python -m pytest tests/ --cov=app --cov-report=html
```

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## 🔒 Security Features

- **Rate Limiting**: Prevents API abuse
- **Non-root User**: Container runs as non-privileged user
- **Security Headers**: Nginx adds security headers
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 📊 Monitoring & Health Checks

### Health Check Endpoint
```http
GET /docs
```

### Docker Health Checks
The container includes built-in health checks that monitor application availability.

### Logs
```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f db

# View nginx logs
docker compose logs -f nginx
```



## 🔧 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check database status
docker compose ps db

# Check database logs
docker compose logs db

# Test database connectivity
docker compose exec db pg_isready -U postgres

# Restart database
docker compose restart db
```

**Application Won't Start**
```bash
# Check application logs
docker compose logs app

# Check for Python errors
docker compose exec app python -c "import app.main; print('Import successful')"

# Rebuild container
docker compose build --no-cache app
docker compose up -d app
```

**API Returns Empty Results**
```bash
# Verify data exists
docker compose exec db psql -U postgres -d assessment -c "SELECT COUNT(*) FROM employees;"

# Check organization configuration
curl "http://localhost:8000/search/filters/metadata?org_id=1"

# Test with known data
curl "http://localhost:8000/search/?org_id=1&q=alice"
```

**Rate Limiting Issues**
```bash
# Check rate limiter status
docker compose logs app | grep "Too many requests"

# Reset rate limiter (restart app)
docker compose restart app

# Test rate limits
for i in {1..6}; do curl -w "%{http_code}\n" "http://localhost:8000/search/?org_id=1"; done
```

**Port Conflicts**
```bash
# Check what's using ports
lsof -i :8000
lsof -i :5432

# Stop conflicting services
brew services stop postgresql  # macOS
sudo systemctl stop postgresql  # Linux

# Or use different ports in docker-compose.yml
ports:
  - "8001:8000"  # API on port 8001
  - "5433:5432"  # Database on port 5433
```

### Performance Tuning

**Database Optimization**
- Increase `shared_buffers` in PostgreSQL
- Add database connection pooling
- Monitor query performance

**Application Scaling**
```bash
# Scale application instances
docker-compose up -d --scale app=3
```

## 📝 Development Guide

### Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd Perennial_assessment

# Start development environment
docker compose up --build

# Make changes to code (auto-reload enabled)
# Access API at http://localhost:8000/docs
```

### Development Workflow

1. **Make Code Changes**: Edit files in `app/` directory
2. **Auto-Reload**: FastAPI automatically reloads on file changes
3. **Test Changes**: Use Swagger UI at http://localhost:8000/docs
4. **Run Tests**: `docker compose exec app python -m pytest`
5. **Check Logs**: `docker compose logs -f app`

### Adding New Features

1. **Update Models**: Modify `app/models.py` for database schema changes
2. **Database Migrations**: Add migration scripts for schema updates
3. **API Endpoints**: Create new routes in `app/routers/`
4. **Validation**: Update `app/schemas.py` for request/response validation
5. **Tests**: Add comprehensive tests in `tests/`
6. **Documentation**: Update this README and API docs

### Code Structure Best Practices

```
app/
├── main.py           # FastAPI app initialization
├── models.py         # SQLAlchemy database models
├── schemas.py        # Pydantic request/response models
├── crud.py           # Database operations
├── db.py             # Database connection setup
├── rate_limiter.py   # Rate limiting logic
├── utils.py          # Helper functions
└── routers/          # API route handlers
    └── search.py     # Search endpoint implementation
```

### API Design Principles

- **RESTful**: Follow REST conventions for endpoint design
- **Consistent**: Use consistent naming and response formats
- **Validated**: All inputs validated with Pydantic schemas
- **Documented**: Comprehensive OpenAPI documentation
- **Secure**: Rate limiting and input sanitization
- **Performant**: Database indexing and query optimization

### Testing Strategy

The project includes both unit tests (with mocking) and integration tests (with real database).

**Unit Tests (Fast, Mocked):**
```bash
# Run unit tests with mocking (no database required)
pytest tests/test_search.py -v

# These tests use mocking and are fast:
# - Mock database responses
# - Test API logic without database dependencies
# - Ideal for CI/CD pipelines
```

**Integration Tests (Slower, Real Database):**
```bash
# Run integration tests with real database
pytest tests/test_integration.py -v

# These tests require a running database:
# - Test end-to-end functionality
# - Verify database interactions
# - Use for comprehensive testing
```

**Run All Tests:**
```bash
# Run all tests (unit + integration)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run tests in Docker container
docker compose exec app python -m pytest tests/ -v

# Run with coverage
docker compose exec app python -m pytest tests/ --cov=app --cov-report=html

# Run specific test
docker compose exec app python -m pytest tests/test_search.py::test_search_employees -v

# Load testing
ab -n 100 -c 10 "http://localhost:8000/search/?org_id=1"
```

### Performance Monitoring

```bash
# Monitor container resources
docker stats

# Database performance
docker compose exec db psql -U postgres -d assessment -c "
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  ORDER BY total_time DESC LIMIT 10;"

# API response times
curl -w "@curl-format.txt" "http://localhost:8000/search/?org_id=1"
```
