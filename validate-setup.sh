#!/bin/bash

# Validation script for Docker containerization setup
set -e

echo "🐳 Validating Docker Containerization Setup"
echo "==========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo " Docker is not installed"
    exit 1
fi
echo " Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo " Docker Compose is not installed"
    exit 1
fi
echo " Docker Compose is installed"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo " Python 3 is not installed"
    exit 1
fi
echo " Python 3 is installed"

# Check if required files exist
required_files=(
    "Dockerfile"
    "docker-compose.yml"
    ".dockerignore"
    ".env.example"
    "requirements.txt"
    "app/main.py"
    "app/models.py"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo " Required file missing: $file"
        exit 1
    fi
done
echo " All required files present"

# Check if app directory structure is correct
required_dirs=(
    "app"
    "tests"
    "alembic"
)

for dir in "${required_dirs[@]}"; do
    if [[ ! -d "$dir" ]]; then
        echo " Required directory missing: $dir"
        exit 1
    fi
done
echo " All required directories present"

# Validate Dockerfile syntax
if docker build -t perennial-test . > /dev/null 2>&1; then
    echo " Dockerfile builds successfully"
    docker rmi perennial-test > /dev/null 2>&1
else
    echo " Dockerfile build failed"
    exit 1
fi

# Validate docker-compose.yml syntax
if docker compose config > /dev/null 2>&1; then
    echo " docker-compose.yml is valid"
else
    echo " docker-compose.yml has syntax errors"
    exit 1
fi


# Check if ports are available
check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        if lsof -i :$port > /dev/null 2>&1; then
            echo "  Port $port is already in use"
            return 1
        else
            echo " Port $port is available"
            return 0
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -ln | grep ":$port " > /dev/null 2>&1; then
            echo "  Port $port is already in use"
            return 1
        else
            echo " Port $port is available"
            return 0
        fi
    else
        echo " Cannot check port $port (lsof/netstat not available)"
        return 0
    fi
}

check_port 8000
check_port 5433

echo ""
echo " Containerization setup validation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure as needed"
echo "2. Run 'docker compose up -d' to start services"
echo "3. Access API documentation at http://localhost:8000/docs"
echo "4. Test the setup with './docker-test.sh'"
echo ""
echo "Available endpoints:"
echo "- Health check: http://localhost:8000/health"
echo "- API docs: http://localhost:8000/docs"
echo "- Employee search: http://localhost:8000/employees/search?org_id=1"
echo "- OpenAPI JSON: http://localhost:8000/openapi.json"
