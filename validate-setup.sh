#!/bin/bash

# Validation script for Docker containerization setup
set -e

echo "🐳 Validating Docker Containerization Setup"
echo "==========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi
echo "✅ Docker Compose is installed"

# Check if required files exist
required_files=(
    "Dockerfile"
    "docker-compose.yml"
    "docker-compose.prod.yml"
    "nginx.conf"
    "init.sql"
    ".dockerignore"
    ".env.example"
    "requirements.txt"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done
echo "✅ All required files present"

# Validate Dockerfile syntax
if docker build -t perennial-test . > /dev/null 2>&1; then
    echo "✅ Dockerfile builds successfully"
    docker rmi perennial-test > /dev/null 2>&1
else
    echo "❌ Dockerfile build failed"
    exit 1
fi

# Validate docker-compose.yml syntax
if docker-compose config > /dev/null 2>&1; then
    echo "✅ docker-compose.yml is valid"
else
    echo "❌ docker-compose.yml has syntax errors"
    exit 1
fi

# Validate production compose file
if docker-compose -f docker-compose.yml -f docker-compose.prod.yml config > /dev/null 2>&1; then
    echo "✅ Production docker-compose configuration is valid"
else
    echo "❌ Production docker-compose configuration has errors"
    exit 1
fi

# Check if ports are available
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

check_port 8000
check_port 5432

echo ""
echo "🎉 Containerization setup validation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure as needed"
echo "2. Run 'make up' or 'docker-compose up -d' to start services"
echo "3. Access API documentation at http://localhost:8000/docs"
echo ""
echo "For production deployment:"
echo "1. Configure SSL certificates in ./ssl/ directory"
echo "2. Update .env with production values"
echo "3. Run 'make up-prod' to deploy with production configuration"
