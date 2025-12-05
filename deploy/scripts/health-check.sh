#!/bin/bash
# =============================================================================
# Health Check Script
# =============================================================================
# Verifies all services are running and healthy
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Cloud Learning Platform - Health Check"
echo "=========================================="
echo ""

# Load environment if available
if [ -f "$DEPLOY_DIR/.env" ]; then
    source "$DEPLOY_DIR/.env"
fi

# Default to localhost for local development
BASE_URL="${NGINX_PUBLIC_IP:-localhost}"

# If we have a public IP, use it; otherwise assume local
if [ "$BASE_URL" != "localhost" ]; then
    BASE_URL="http://$BASE_URL"
else
    BASE_URL="http://localhost"
fi

echo "Checking services at: $BASE_URL"
echo ""

# Function to check a service
check_service() {
    local name=$1
    local url=$2
    local timeout=${3:-5}
    
    printf "%-25s" "$name:"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    elif [ "$response" = "000" ]; then
        echo -e "${RED}✗ Not reachable${NC}"
        return 1
    else
        echo -e "${YELLOW}⚠ HTTP $response${NC}"
        return 1
    fi
}

# Track failures
failures=0

# Check Nginx Gateway
echo "API Gateway:"
echo "------------"
check_service "Nginx Gateway" "$BASE_URL/health" || ((failures++))
echo ""

# Check Microservices
echo "Microservices:"
echo "--------------"

# Local ports for local development
if [ "$BASE_URL" = "http://localhost" ]; then
    check_service "User Management" "http://localhost:8001/health" || ((failures++))
    check_service "Chat Service" "http://localhost:8000/health" || ((failures++))
    check_service "Document Service" "http://localhost:8002/health" || ((failures++))
    check_service "Quiz Service" "http://localhost:8003/health" || ((failures++))
else
    # Via API Gateway
    check_service "User Management" "$BASE_URL/api/auth/health" || ((failures++))
    check_service "Chat Service" "$BASE_URL/api/chat/health" || ((failures++))
    check_service "Document Service" "$BASE_URL/api/documents/health" || ((failures++))
    check_service "Quiz Service" "$BASE_URL/api/quiz/health" || ((failures++))
fi

echo ""

# Check Database connectivity (if we can reach a service)
echo "Database Connectivity:"
echo "----------------------"
db_check=$(curl -s --max-time 5 "http://localhost:8001/health/db" 2>/dev/null || echo '{"status":"unknown"}')
if echo "$db_check" | grep -q '"status":"healthy"'; then
    echo -e "PostgreSQL:               ${GREEN}✓ Connected${NC}"
else
    echo -e "PostgreSQL:               ${YELLOW}⚠ Unable to verify${NC}"
fi

# Check Kafka connectivity (if we can reach a service)
kafka_check=$(curl -s --max-time 5 "http://localhost:8000/health/kafka" 2>/dev/null || echo '{"status":"unknown"}')
if echo "$kafka_check" | grep -q '"status":"healthy"'; then
    echo -e "Kafka:                    ${GREEN}✓ Connected${NC}"
else
    echo -e "Kafka:                    ${YELLOW}⚠ Unable to verify${NC}"
fi

echo ""
echo "=========================================="

# Summary
if [ $failures -eq 0 ]; then
    echo -e "${GREEN}All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}$failures service(s) are not healthy${NC}"
    exit 1
fi

