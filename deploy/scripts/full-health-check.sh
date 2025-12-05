#!/bin/bash
# ==============================================================================
# Full System Health Check - Cloud Learning Platform Phase 2
# ==============================================================================

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║     Cloud Learning Platform - Full System Health Check            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NODE_1_IP="10.0.1.195"
APP_NODE_2_IP="10.0.2.179"
KAFKA_IP="10.0.10.231"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1️⃣  KAFKA HEALTH CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Kafka port
if nc -z $KAFKA_IP 9092 2>/dev/null; then
    echo -e "${GREEN}✅ Kafka Broker (${KAFKA_IP}:9092): REACHABLE${NC}"
else
    echo -e "${RED}❌ Kafka Broker (${KAFKA_IP}:9092): UNREACHABLE${NC}"
fi

# Check Zookeeper port
if nc -z $KAFKA_IP 2181 2>/dev/null; then
    echo -e "${GREEN}✅ Zookeeper (${KAFKA_IP}:2181): REACHABLE${NC}"
else
    echo -e "${RED}❌ Zookeeper (${KAFKA_IP}:2181): UNREACHABLE${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  2️⃣  APP NODE 1 - User Management & Chat"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# User Management Service
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://${APP_NODE_1_IP}:8001/health 2>/dev/null || echo "000")
if [ "$RESPONSE" = "200" ]; then
    HEALTH=$(curl -s http://${APP_NODE_1_IP}:8001/health 2>/dev/null)
    echo -e "${GREEN}✅ User Management (8001): ${HEALTH}${NC}"
else
    echo -e "${RED}❌ User Management (8001): HTTP ${RESPONSE}${NC}"
fi

# Chat Service
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://${APP_NODE_1_IP}:8000/health 2>/dev/null || echo "000")
if [ "$RESPONSE" = "200" ]; then
    HEALTH=$(curl -s http://${APP_NODE_1_IP}:8000/health 2>/dev/null)
    echo -e "${GREEN}✅ Chat Service (8000): ${HEALTH}${NC}"
else
    echo -e "${RED}❌ Chat Service (8000): HTTP ${RESPONSE}${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  3️⃣  APP NODE 2 - Document & Quiz"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Document Service
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://${APP_NODE_2_IP}:8002/health 2>/dev/null || echo "000")
if [ "$RESPONSE" = "200" ]; then
    HEALTH=$(curl -s http://${APP_NODE_2_IP}:8002/health 2>/dev/null)
    echo -e "${GREEN}✅ Document Service (8002): ${HEALTH}${NC}"
else
    echo -e "${RED}❌ Document Service (8002): HTTP ${RESPONSE}${NC}"
fi

# Quiz Service
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://${APP_NODE_2_IP}:8003/health 2>/dev/null || echo "000")
if [ "$RESPONSE" = "200" ]; then
    HEALTH=$(curl -s http://${APP_NODE_2_IP}:8003/health 2>/dev/null)
    echo -e "${GREEN}✅ Quiz Service (8003): ${HEALTH}${NC}"
else
    echo -e "${RED}❌ Quiz Service (8003): HTTP ${RESPONSE}${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  4️⃣  DATABASE CONNECTION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if services can connect to RDS
echo "Checking container logs for database connections..."

ssh -i ~/labsuser.pem ec2-user@${APP_NODE_1_IP} "docker logs platform-user-mgmt 2>&1 | grep -i 'database initialized' | tail -1" 2>/dev/null && \
    echo -e "${GREEN}✅ User Management: Database Connected${NC}" || \
    echo -e "${RED}❌ User Management: Database Issue${NC}"

ssh -i ~/labsuser.pem ec2-user@${APP_NODE_2_IP} "docker logs platform-document 2>&1 | grep -i 'database initialized' | tail -1" 2>/dev/null && \
    echo -e "${GREEN}✅ Document Service: Database Connected${NC}" || \
    echo -e "${RED}❌ Document Service: Database Issue${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  5️⃣  KAFKA INTEGRATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ssh -i ~/labsuser.pem ec2-user@${APP_NODE_1_IP} "docker logs platform-chat 2>&1 | grep -i 'kafka producer connected' | tail -1" 2>/dev/null && \
    echo -e "${GREEN}✅ Chat Service: Kafka Connected${NC}" || \
    echo -e "${YELLOW}⚠️  Chat Service: Kafka Not Connected${NC}"

ssh -i ~/labsuser.pem ec2-user@${APP_NODE_2_IP} "docker logs platform-document 2>&1 | grep -i 'kafka producer connected' | tail -1" 2>/dev/null && \
    echo -e "${GREEN}✅ Document Service: Kafka Connected${NC}" || \
    echo -e "${YELLOW}⚠️  Document Service: Kafka Not Connected${NC}"

ssh -i ~/labsuser.pem ec2-user@${APP_NODE_2_IP} "docker logs platform-quiz 2>&1 | grep -i 'kafka producer connected' | tail -1" 2>/dev/null && \
    echo -e "${GREEN}✅ Quiz Service: Kafka Connected${NC}" || \
    echo -e "${YELLOW}⚠️  Quiz Service: Kafka Not Connected${NC}"

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                    Health Check Complete                           ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

