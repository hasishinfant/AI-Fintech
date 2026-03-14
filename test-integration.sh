#!/bin/bash

# Intelli-Credit Backend-Frontend Integration Test Script
# This script tests all API endpoints to verify integration is working

echo "=========================================="
echo "Intelli-Credit Integration Test"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api"
TEST_APP_ID="550e8400-e29b-41d4-a716-446655440000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    
    response=$(curl -s -w "\n%{http_code}" "$url")
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $status_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $status_code, expected $expected_status)"
        echo "Response: $body"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Function to test CORS
test_cors() {
    echo -n "Testing CORS... "
    
    response=$(curl -s -I -X OPTIONS "$API_URL/applications" \
        -H "Origin: http://localhost:5173" \
        -H "Access-Control-Request-Method: GET")
    
    if echo "$response" | grep -q "access-control-allow-origin"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Response: $response"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "1. Core Endpoints"
echo "===================="
test_endpoint "Health Check" "$BASE_URL/health"
test_endpoint "Root Endpoint" "$BASE_URL/"
echo ""

echo "2. Application Endpoints"
echo "========================="
test_endpoint "List Applications" "$API_URL/applications"
test_endpoint "Get Application Detail" "$API_URL/applications/$TEST_APP_ID"
test_endpoint "Get Application Status" "$API_URL/applications/$TEST_APP_ID/status"
echo ""

echo "3. Processing Endpoints"
echo "========================"
test_endpoint "Get Credit Assessment" "$API_URL/applications/$TEST_APP_ID/credit-assessment"
test_endpoint "Get Loan Recommendation" "$API_URL/applications/$TEST_APP_ID/recommendation"
test_endpoint "Get Research Data" "$API_URL/applications/$TEST_APP_ID/research"
echo ""

echo "4. CAM Endpoints"
echo "================="
test_endpoint "Get CAM Document" "$API_URL/applications/$TEST_APP_ID/cam"
echo ""

echo "5. CORS Configuration"
echo "======================"
test_cors
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start frontend: cd frontend && npm run dev"
    echo "2. Open http://localhost:5173 in browser"
    echo "3. Navigate to Applications page"
    echo "4. Verify data loads correctly"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
    exit 1
fi
