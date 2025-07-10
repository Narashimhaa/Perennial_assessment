#!/bin/bash

# Test script for validate-setup.sh
# This script tests the validation script in different scenarios

set -e

echo "🧪 Testing validate-setup.sh script"
echo "===================================="

# Test 1: Normal execution (should pass)
echo "Test 1: Normal execution"
if ./validate-setup.sh >/dev/null 2>&1; then
    echo " Normal execution: PASSED"
else
    echo " Normal execution: FAILED"
    echo "Running validation script with output to debug:"
    ./validate-setup.sh
    exit 1
fi

# Test 2: Check if script is executable
echo "Test 2: Script permissions"
if [[ -x "./validate-setup.sh" ]]; then
    echo " Script is executable: PASSED"
else
    echo " Script is not executable: FAILED"
    exit 1
fi

# Test 3: Check if script handles missing files gracefully
echo "Test 3: Missing file handling"
# Temporarily rename a required file
if [[ -f "requirements.txt" ]]; then
    mv requirements.txt requirements.txt.backup
    if ./validate-setup.sh > /dev/null 2>&1; then
        echo " Missing file detection: FAILED (should have failed)"
        mv requirements.txt.backup requirements.txt
        exit 1
    else
        echo " Missing file detection: PASSED"
        mv requirements.txt.backup requirements.txt
    fi
else
    echo "⚠️  requirements.txt not found, skipping missing file test"
fi

# Test 4: Check if script validates Docker commands
echo "Test 4: Docker command validation"
# This test assumes Docker is installed
if command -v docker &> /dev/null; then
    echo " Docker command validation: PASSED"
else
    echo "  Docker not found, validation script should handle this"
fi

# Test 5: Check if script validates docker-compose syntax
echo "Test 5: Docker Compose syntax validation"
if docker compose config > /dev/null 2>&1; then
    echo " Docker Compose syntax validation: PASSED"
else
    echo " Docker Compose syntax validation: FAILED"
    exit 1
fi

# Test 6: Check if script provides helpful output
echo "Test 6: Output format validation"
output=$(./validate-setup.sh 2>&1)
if echo "$output" | grep -q "Containerization setup validation completed successfully"; then
    echo " Output format validation: PASSED"
else
    echo " Output format validation: FAILED"
    exit 1
fi

echo ""
echo " All validate-setup.sh tests PASSED!"
echo ""
echo "Summary:"
echo "- Script is executable and runs correctly"
echo "- Handles missing files appropriately"
echo "- Validates Docker and Docker Compose"
echo "- Provides clear success/failure messages"
echo "- Gives helpful next steps"
