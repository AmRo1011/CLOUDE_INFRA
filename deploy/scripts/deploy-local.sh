#!/bin/bash
# =============================================================================
# Local Development Deployment Script
# =============================================================================
# Starts all services locally using Docker Compose
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$DEPLOY_DIR")"

echo "=========================================="
echo "Cloud Learning Platform - Local Deployment"
echo "=========================================="

# Check if .env file exists
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    echo "Error: .env file not found in deploy directory"
    echo "Please copy config.env.example to .env and fill in values:"
    echo "  cp $DEPLOY_DIR/config.env.example $DEPLOY_DIR/.env"
    exit 1
fi

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build services
echo ""
echo "Building Docker images..."
echo ""

cd "$PROJECT_ROOT"

docker-compose -f "$DEPLOY_DIR/docker-compose.local.yml" build

# Start services
echo ""
echo "Starting services..."
echo ""

docker-compose -f "$DEPLOY_DIR/docker-compose.local.yml" up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
echo ""

sleep 10

# Check service health
echo ""
echo "Checking service health..."
echo ""

services=("user-mgmt:8001" "chat:8000" "document:8002" "quiz:8003")

for service in "${services[@]}"; do
    name="${service%%:*}"
    port="${service##*:}"
    
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✓ $name service is healthy (port $port)"
    else
        echo "✗ $name service is not responding (port $port)"
    fi
done

echo ""
echo "=========================================="
echo "Local deployment complete!"
echo ""
echo "Services available at:"
echo "  - User Management: http://localhost:8001"
echo "  - Chat:            http://localhost:8000"
echo "  - Document:        http://localhost:8002"
echo "  - Quiz:            http://localhost:8003"
echo ""
echo "To view logs:"
echo "  docker-compose -f $DEPLOY_DIR/docker-compose.local.yml logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f $DEPLOY_DIR/docker-compose.local.yml down"
echo "=========================================="

