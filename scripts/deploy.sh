#!/bin/bash

# Cloud Learning Platform - Quick Deploy Script
# This script automates the deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Cloud Learning Platform - Infrastructure Deployment  ${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}✗ Terraform not found. Please install Terraform >= 1.5.0${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Terraform found: $(terraform version | head -1)${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗ AWS CLI not found. Please install AWS CLI${NC}"
    exit 1
fi
echo -e "${GREEN}✓ AWS CLI found: $(aws --version)${NC}"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}✗ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials configured${NC}"
echo ""

# Check if terraform.tfvars exists
cd terraform
if [ ! -f terraform.tfvars ]; then
    echo -e "${YELLOW}⚠ terraform.tfvars not found${NC}"
    echo -e "${YELLOW}Creating from template...${NC}"
    cp terraform.tfvars.example terraform.tfvars
    
    echo -e "${RED}Please edit terraform.tfvars with your values:${NC}"
    echo "  - ec2_key_name: Your EC2 key pair name"
    echo "  - db_password: Strong database password"
    echo ""
    echo -e "${YELLOW}Press Enter when ready to continue...${NC}"
    read
fi

# Initialize Terraform
echo -e "${BLUE}Initializing Terraform...${NC}"
terraform init

# Validate configuration
echo -e "${BLUE}Validating Terraform configuration...${NC}"
if ! terraform validate; then
    echo -e "${RED}✗ Terraform validation failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Configuration valid${NC}"
echo ""

# Show plan
echo -e "${BLUE}Generating deployment plan...${NC}"
terraform plan -out=tfplan

echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Review the plan above carefully.${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Estimated deployment time: 10-15 minutes${NC}"
echo -e "${YELLOW}Estimated monthly cost: ~$50-110/month${NC}"
echo ""
read -p "Do you want to proceed with deployment? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}Deployment cancelled${NC}"
    rm -f tfplan
    exit 0
fi

# Apply
echo ""
echo -e "${BLUE}Deploying infrastructure...${NC}"
terraform apply tfplan
rm -f tfplan

# Get outputs
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Deployment Complete!                                  ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""

NGINX_IP=$(terraform output -raw nginx_public_ip 2>/dev/null || echo "N/A")
RDS_ENDPOINT=$(terraform output -raw rds_address 2>/dev/null || echo "N/A")
KAFKA_IP=$(terraform output -raw kafka_private_ip 2>/dev/null || echo "N/A")

echo -e "${BLUE}Infrastructure Details:${NC}"
echo ""
echo -e "  ${GREEN}Nginx Gateway (Public):${NC} $NGINX_IP"
echo -e "  ${GREEN}RDS Database:${NC} $RDS_ENDPOINT"
echo -e "  ${GREEN}Kafka Broker:${NC} $KAFKA_IP"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "  1. Test health endpoint:"
echo "     ${GREEN}curl http://$NGINX_IP/health${NC}"
echo ""
echo "  2. SSH to Nginx gateway:"
echo "     ${GREEN}ssh -i your-key.pem ec2-user@$NGINX_IP${NC}"
echo ""
echo "  3. Setup database schemas:"
echo "     See: ${BLUE}docs/operations.md${NC}"
echo ""
echo "  4. Verify Kafka topics:"
echo "     See: ${BLUE}docs/operations.md${NC}"
echo ""

echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Important: Save your outputs for later reference${NC}"
echo ""
echo "Run: ${GREEN}terraform output${NC} to see all values"
echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"

