#!/bin/bash
# =============================================================================
# Redeploy Script for AWS - After Fixing Configuration
# =============================================================================

echo "=================================="
echo "Redeploying Services on AWS"
echo "=================================="

# Stop containers
echo "Stopping containers..."
docker-compose -f deploy/docker-compose.aws-node2.yml down

# Pull latest images
echo "Pulling latest images..."
docker-compose -f deploy/docker-compose.aws-node2.yml pull

# Start with new config
echo "Starting services with updated configuration..."
docker-compose -f deploy/docker-compose.aws-node2.yml up -d

# Wait a bit for containers to start
sleep 5

# Check status
echo ""
echo "Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Waiting 10 seconds for health checks..."
sleep 10

# Show logs
echo ""
echo "Recent logs from Document service:"
docker logs platform-document --tail 20

echo ""
echo "Recent logs from Quiz service:"
docker logs platform-quiz --tail 20

echo ""
echo "=================================="
echo "Deployment Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Check container health: docker ps"
echo "2. Test endpoints:"
echo "   curl http://localhost:8002/health"
echo "   curl http://localhost:8003/health"
echo "3. View full logs: docker logs platform-document -f"
echo ""

