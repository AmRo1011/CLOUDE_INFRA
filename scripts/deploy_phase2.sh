#!/bin/bash
# =============================================================================
# Phase 2 Deployment Script
# =============================================================================
# Deploys Phase 2 microservices using Docker Compose
# Usage: ./scripts/deploy_phase2.sh [local|aws]
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_ROOT/deploy"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Determine deployment mode
MODE=${1:-local}

print_header "Cloud Learning Platform - Phase 2 Deployment"
echo "Mode: $MODE"

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose installed"
    
    # Check .env file
    if [ ! -f "$DEPLOY_DIR/.env" ]; then
        print_warning ".env file not found"
        echo "Creating from template..."
        cp "$DEPLOY_DIR/config.env.example" "$DEPLOY_DIR/.env"
        print_warning "Please edit $DEPLOY_DIR/.env with your configuration"
        exit 1
    fi
    print_success ".env file exists"
}

# Deploy locally
deploy_local() {
    print_header "Deploying Locally"
    
    cd "$DEPLOY_DIR"
    
    # Build images
    echo "Building Docker images..."
    docker-compose -f docker-compose.local.yml build
    
    # Start services
    echo "Starting services..."
    docker-compose -f docker-compose.local.yml up -d
    
    # Wait for services
    echo "Waiting for services to start..."
    sleep 15
    
    # Health check
    print_header "Health Check"
    
    services=("8001:User Management" "8000:Chat" "8002:Document" "8003:Quiz")
    
    for service in "${services[@]}"; do
        port="${service%%:*}"
        name="${service##*:}"
        
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            print_success "$name (port $port)"
        else
            print_error "$name (port $port) - Not responding"
        fi
    done
    
    # Check Nginx gateway
    if curl -s "http://localhost/health" > /dev/null 2>&1; then
        print_success "Nginx Gateway (port 80)"
    else
        print_warning "Nginx Gateway (port 80) - Not responding"
    fi
    
    print_header "Deployment Complete!"
    echo ""
    echo "Services available at:"
    echo "  API Gateway: http://localhost"
    echo "  User Mgmt:   http://localhost:8001"
    echo "  Chat:        http://localhost:8000"
    echo "  Document:    http://localhost:8002"
    echo "  Quiz:        http://localhost:8003"
    echo ""
    echo "Useful commands:"
    echo "  View logs:   docker-compose -f $DEPLOY_DIR/docker-compose.local.yml logs -f"
    echo "  Stop:        docker-compose -f $DEPLOY_DIR/docker-compose.local.yml down"
}

# Deploy to AWS
deploy_aws() {
    print_header "Deploying to AWS"
    
    # Source environment
    source "$DEPLOY_DIR/.env"
    
    # Check required variables
    if [ -z "$NGINX_PUBLIC_IP" ] || [ -z "$APP_NODE_1_PRIVATE_IP" ] || [ -z "$APP_NODE_2_PRIVATE_IP" ]; then
        print_error "Missing required environment variables"
        echo "Required: NGINX_PUBLIC_IP, APP_NODE_1_PRIVATE_IP, APP_NODE_2_PRIVATE_IP"
        echo ""
        echo "Get these from Terraform:"
        echo "  cd terraform && terraform output"
        exit 1
    fi
    
    # Check SSH key
    SSH_KEY="${SSH_KEY_PATH:-$HOME/.ssh/your-key.pem}"
    if [ ! -f "$SSH_KEY" ]; then
        print_error "SSH key not found: $SSH_KEY"
        echo "Set SSH_KEY_PATH environment variable"
        exit 1
    fi
    
    echo "Infrastructure:"
    echo "  Nginx IP:    $NGINX_PUBLIC_IP"
    echo "  App Node 1:  $APP_NODE_1_PRIVATE_IP"
    echo "  App Node 2:  $APP_NODE_2_PRIVATE_IP"
    
    # Update Nginx config
    echo ""
    echo "Updating Nginx configuration..."
    
    sed -e "s/APP_NODE_1_PRIVATE_IP/$APP_NODE_1_PRIVATE_IP/g" \
        -e "s/APP_NODE_2_PRIVATE_IP/$APP_NODE_2_PRIVATE_IP/g" \
        "$DEPLOY_DIR/nginx/nginx.conf" > "/tmp/nginx.conf"
    
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no \
        "/tmp/nginx.conf" \
        "ec2-user@$NGINX_PUBLIC_IP:/tmp/nginx.conf"
    
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "ec2-user@$NGINX_PUBLIC_IP" \
        "sudo cp /tmp/nginx.conf /etc/nginx/nginx.conf && sudo nginx -t && sudo systemctl reload nginx"
    
    print_success "Nginx configuration updated"
    
    print_header "AWS Deployment Complete!"
    echo ""
    echo "API Gateway: http://$NGINX_PUBLIC_IP"
    echo ""
    echo "Test with:"
    echo "  curl http://$NGINX_PUBLIC_IP/health"
}

# Main
check_prerequisites

case $MODE in
    local)
        deploy_local
        ;;
    aws)
        deploy_aws
        ;;
    *)
        echo "Usage: $0 [local|aws]"
        exit 1
        ;;
esac

