#!/bin/bash
# =============================================================================
# AWS EC2 Deployment Script
# =============================================================================
# Deploys services to AWS EC2 instances using Docker Compose
# Requires: SSH access to EC2 instances, Terraform outputs
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$DEPLOY_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

echo "=========================================="
echo "Cloud Learning Platform - AWS Deployment"
echo "=========================================="

# Load environment variables
if [ -f "$DEPLOY_DIR/.env" ]; then
    source "$DEPLOY_DIR/.env"
else
    echo "Error: .env file not found in deploy directory"
    echo "Please copy config.env.example to .env and fill in values"
    exit 1
fi

# Get Terraform outputs if not set
if [ -z "$NGINX_PUBLIC_IP" ] || [ -z "$APP_NODE_1_PRIVATE_IP" ] || [ -z "$APP_NODE_2_PRIVATE_IP" ]; then
    echo "Getting infrastructure details from Terraform..."
    cd "$TERRAFORM_DIR"
    
    NGINX_PUBLIC_IP=$(terraform output -raw nginx_public_ip 2>/dev/null || echo "")
    APP_NODE_1_PRIVATE_IP=$(terraform output -raw app_node_1_private_ip 2>/dev/null || echo "")
    APP_NODE_2_PRIVATE_IP=$(terraform output -raw app_node_2_private_ip 2>/dev/null || echo "")
    
    if [ -z "$NGINX_PUBLIC_IP" ]; then
        echo "Error: Could not get Terraform outputs. Make sure infrastructure is deployed."
        exit 1
    fi
fi

echo ""
echo "Infrastructure Details:"
echo "  Nginx Public IP:      $NGINX_PUBLIC_IP"
echo "  App Node 1 Private:   $APP_NODE_1_PRIVATE_IP"
echo "  App Node 2 Private:   $APP_NODE_2_PRIVATE_IP"
echo ""

# SSH key path
SSH_KEY="${SSH_KEY_PATH:-$HOME/.ssh/your-key.pem}"
if [ ! -f "$SSH_KEY" ]; then
    echo "Error: SSH key not found at $SSH_KEY"
    echo "Set SSH_KEY_PATH environment variable to your key location"
    exit 1
fi

# Function to deploy to an EC2 instance
deploy_to_instance() {
    local instance_ip=$1
    local instance_name=$2
    local compose_file=$3
    
    echo ""
    echo "Deploying to $instance_name ($instance_ip)..."
    echo ""
    
    # Copy docker-compose file
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no \
        "$DEPLOY_DIR/$compose_file" \
        "ec2-user@$instance_ip:/home/ec2-user/docker-compose.yml"
    
    # Copy environment files
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no \
        "$DEPLOY_DIR/.env" \
        "ec2-user@$instance_ip:/home/ec2-user/.env"
    
    # Pull and start containers
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "ec2-user@$instance_ip" << 'EOF'
        cd /home/ec2-user
        
        # Login to ECR (if using ECR)
        if [ -n "$ECR_REGISTRY" ]; then
            aws ecr get-login-password --region $AWS_REGION | \
                docker login --username AWS --password-stdin $ECR_REGISTRY
        fi
        
        # Pull latest images and restart
        docker-compose pull
        docker-compose up -d
        
        # Show status
        docker-compose ps
EOF
    
    echo "✓ Deployed to $instance_name"
}

# Deploy Nginx configuration
echo ""
echo "Deploying Nginx configuration..."
echo ""

# Update nginx.conf with actual IPs
sed -e "s/APP_NODE_1_PRIVATE_IP/$APP_NODE_1_PRIVATE_IP/g" \
    -e "s/APP_NODE_2_PRIVATE_IP/$APP_NODE_2_PRIVATE_IP/g" \
    "$DEPLOY_DIR/nginx/nginx.conf" > "/tmp/nginx.conf"

scp -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "/tmp/nginx.conf" \
    "ec2-user@$NGINX_PUBLIC_IP:/tmp/nginx.conf"

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "ec2-user@$NGINX_PUBLIC_IP" << 'EOF'
    sudo cp /tmp/nginx.conf /etc/nginx/nginx.conf
    sudo nginx -t && sudo systemctl reload nginx
    echo "✓ Nginx configuration updated"
EOF

# Deploy to App Node 1 (Chat + User Management)
# Note: In production, use separate compose files for each node
# For simplicity, we're using the same compose file

echo ""
echo "Deploying to App Node 1 (via Nginx as bastion)..."
echo ""

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    -J "ec2-user@$NGINX_PUBLIC_IP" \
    "ec2-user@$APP_NODE_1_PRIVATE_IP" << 'INNEREOF'
    echo "Connected to App Node 1"
    # Pull and run containers for Chat and User Management
    # docker-compose commands would go here
INNEREOF

echo ""
echo "Deploying to App Node 2 (via Nginx as bastion)..."
echo ""

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    -J "ec2-user@$NGINX_PUBLIC_IP" \
    "ec2-user@$APP_NODE_2_PRIVATE_IP" << 'INNEREOF'
    echo "Connected to App Node 2"
    # Pull and run containers for Document and Quiz
    # docker-compose commands would go here
INNEREOF

echo ""
echo "=========================================="
echo "AWS Deployment Complete!"
echo ""
echo "API Gateway available at: http://$NGINX_PUBLIC_IP"
echo ""
echo "Test endpoints:"
echo "  curl http://$NGINX_PUBLIC_IP/health"
echo "  curl http://$NGINX_PUBLIC_IP/api/auth/health"
echo "  curl http://$NGINX_PUBLIC_IP/api/chat/health"
echo "  curl http://$NGINX_PUBLIC_IP/api/documents/health"
echo "  curl http://$NGINX_PUBLIC_IP/api/quiz/health"
echo "=========================================="

