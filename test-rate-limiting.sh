#!/bin/bash

# Standalone Rate Limiting Test Script
# Tests the rate limiting functionality of the Employee Search API

set -e

API_URL="http://localhost:8000"
ENDPOINT="/employees/search?org_id=1"

echo " Testing Rate Limiting for Employee Search API"
echo "================================================"

echo "🔍 Checking if API is accessible..."
if ! curl -s "$API_URL/health" > /dev/null; then
    echo " API is not accessible at $API_URL"
    echo "Please make sure the API is running with: docker compose up -d"
    exit 1
fi

echo " API is accessible"

echo "📡 Testing normal request..."
response=$(curl -s -w "%{http_code}" "$API_URL$ENDPOINT" -o /dev/null)
if [ "$response" = "200" ]; then
    echo " Normal request successful (HTTP $response)"
else
    echo " Normal request failed (HTTP $response)"
    exit 1
fi

# Wait a moment to ensure clean state
echo " Waiting 2 seconds for clean state..."
sleep 2

# Test rate limiting with rapid requests
echo " Testing rate limiting with rapid requests..."
echo "Making requests as fast as possible..."

rate_limit_hit=false
successful_requests=0
failed_requests=0
first_429_at=0

for i in {1..20}; do
    start_time=$(date +%s.%N)
    response=$(curl -s -w "%{http_code}" "$API_URL$ENDPOINT" -o /dev/null 2>/dev/null)
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    printf "Request %2d: HTTP %s (%.3fs)\n" "$i" "$response" "$duration"
    
    if [ "$response" = "429" ]; then
        if [ "$rate_limit_hit" = false ]; then
            first_429_at=$i
            rate_limit_hit=true
            echo " First rate limit hit at request $i"
        fi
        failed_requests=$((failed_requests + 1))
    elif [ "$response" = "200" ]; then
        successful_requests=$((successful_requests + 1))
    fi
done

echo ""
echo " Rate Limiting Test Results:"
echo "================================"
echo "Total requests made: 20"
echo "Successful requests: $successful_requests"
echo "Rate limited requests: $failed_requests"

if [ "$rate_limit_hit" = true ]; then
    echo " Rate limiting is WORKING"
    echo " First rate limit triggered at request: $first_429_at"
    echo " Rate limit effectiveness: $(echo "scale=1; $failed_requests * 100 / 20" | bc -l)% of requests blocked"
else
    echo "  Rate limiting test INCONCLUSIVE"
    echo "Possible reasons:"
    echo "  • Rate limit is set too high (current default: 5 requests/minute)"
    echo "  • Requests are not fast enough to trigger limit"
    echo "  • Rate limiter is not properly configured"
    echo ""
    echo " Troubleshooting suggestions:"
    echo "  1. Check rate limit configuration:"
    echo "     docker compose exec app printenv | grep RATE_LIMIT"
    echo "  2. Check application logs:"
    echo "     docker compose logs app | grep -i rate"
    echo "  3. Try with lower rate limits in docker-compose.yml:"
    echo "     RATE_LIMIT_REQUESTS: 2"
    echo "     RATE_LIMIT_WINDOW: 60"
fi

echo ""
echo " Additional Information:"
echo "API Endpoint: $API_URL$ENDPOINT"
echo "Test completed at: $(date)"
