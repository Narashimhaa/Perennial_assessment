.PHONY: help build up down logs test clean restart shell db-shell

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build the Docker images"
	@echo "  up        - Start the services in development mode"
	@echo "  up-prod   - Start the services in production mode"
	@echo "  down      - Stop and remove containers"
	@echo "  logs      - Show logs from all services"
	@echo "  logs-app  - Show logs from app service only"
	@echo "  logs-db   - Show logs from database service only"
	@echo "  test      - Run tests in container"
	@echo "  shell     - Open shell in app container"
	@echo "  db-shell  - Open PostgreSQL shell"
	@echo "  restart   - Restart all services"
	@echo "  clean     - Remove containers, networks, and volumes"
	@echo "  status    - Show status of all services"

# Build Docker images
build:
	docker-compose build

# Start services in development mode
up:
	docker-compose up -d
	@echo "Services started. API available at http://localhost:8000/docs"

# Start services in production mode
up-prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production services started. API available at http://localhost"

# Stop services
down:
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

logs-db:
	docker-compose logs -f db

# Run tests
test:
	docker-compose exec app python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	docker-compose exec app python -m pytest tests/ --cov=app --cov-report=html

# Open shell in app container
shell:
	docker-compose exec app /bin/bash

# Open PostgreSQL shell
db-shell:
	docker-compose exec db psql -U postgres -d assessment

# Restart services
restart:
	docker-compose restart

# Show service status
status:
	docker-compose ps

# Clean up everything
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Reset database (WARNING: This will delete all data)
reset-db:
	docker-compose down -v
	docker-compose up -d db
	@echo "Database reset. Waiting for initialization..."
	sleep 10
	docker-compose up -d app

# Check health of services
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/docs > /dev/null 2>&1 && echo "✅ API is healthy" || echo "❌ API is not responding"
	@docker-compose exec db pg_isready -U postgres > /dev/null 2>&1 && echo "✅ Database is healthy" || echo "❌ Database is not responding"
