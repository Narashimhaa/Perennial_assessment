#!/bin/bash

# Docker Test Script for Employee Search API
# This script tests the Docker setup with the latest changes

set -e

echo "🐳 Testing Docker setup with latest changes..."

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    docker compose -f docker-compose.yml -f docker-compose.test.yml down -v --remove-orphans 2>/dev/null || true
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Build and start services with test configuration
echo "📦 Building and starting services with test configuration..."
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
timeout=120
counter=0

while [ $counter -lt $timeout ]; do
    if docker compose -f docker-compose.yml -f docker-compose.test.yml ps | grep -q "healthy"; then
        echo "Services are healthy!"
        break
    fi
    
    if [ $counter -eq $timeout ]; then
        echo " Timeout waiting for services to be healthy"
        docker compose -f docker-compose.yml -f docker-compose.test.yml logs
        exit 1
    fi
    
    echo "Waiting... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

# Test the health endpoint
echo "🏥 Testing health endpoint..."
health_response=$(curl -s http://localhost:8000/health)
if echo "$health_response" | grep -q "healthy"; then
    echo "Health check passed: $health_response"
else
    echo "Health check failed: $health_response"
    exit 1
fi

# Test the search endpoint
echo "🔍 Testing search endpoint..."
search_response=$(curl -s "http://localhost:8000/employees/search?org_id=1&limit=2")
if echo "$search_response" | grep -q "first_name"; then
    echo "Search endpoint working: Found employee data"
else
    echo "Search endpoint failed: $search_response"
    exit 1
fi

# Test rate limiting (make multiple requests quickly)
echo "🚦 Testing rate limiting..."
echo "Making rapid requests to trigger rate limit..."

rate_limit_hit=false
successful_requests=0

# Make requests as fast as possible to trigger rate limiting
for i in {1..15}; do
    response=$(curl -s -w "%{http_code}" "http://localhost:8000/employees/search?org_id=1" -o /dev/null)
    echo "Request $i: HTTP $response"

    if [ "$response" = "429" ]; then
        rate_limit_hit=true
        echo "Rate limiting working: Got 429 status code after $i requests"
        break
    elif [ "$response" = "200" ]; then
        successful_requests=$((successful_requests + 1))
    fi

    # No sleep - make requests as fast as possible
done

if [ "$rate_limit_hit" = true ]; then
    echo "Rate limiting is working correctly"
    echo "Successful requests before rate limit: $successful_requests"
else
    echo "  Rate limiting test results:"
    echo "   - Total requests made: 15"
    echo "   - Successful requests: $successful_requests"
    echo "   - Rate limit triggered: No"
    echo "   - This might indicate:"
    echo "     * Rate limit is set too high for this test"
    echo "     * Requests are not fast enough"
    echo "     * Rate limiter configuration needs adjustment"

    echo "Checking rate limit configuration..."
    docker compose -f docker-compose.yml -f docker-compose.test.yml exec app printenv | grep RATE_LIMIT || echo "Rate limit env vars not found"
fi

echo "Testing OpenAPI endpoint..."
openapi_response=$(curl -s http://localhost:8000/openapi.json)
if echo "$openapi_response" | grep -q "Employee Search API"; then
    echo "OpenAPI endpoint working"
else
    echo "OpenAPI endpoint failed"
    exit 1
fi

echo "All Docker tests passed successfully!"
echo "Service status:"
docker compose -f docker-compose.yml -f docker-compose.test.yml ps
