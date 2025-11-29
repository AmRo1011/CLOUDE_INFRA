#!/bin/bash

# Cloud Learning Platform - Status Check Script
# This script shows the current status of all infrastructure

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Cloud Learning Platform - Infrastructure Status      ${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

cd terraform

# Check if infrastructure exists
if [ ! -f terraform.tfstate ] || [ ! -s terraform.tfstate ]; then
    echo -e "${YELLOW}No infrastructure deployed${NC}"
    echo "Run: ./scripts/deploy.sh to deploy"
    exit 0
fi

# EC2 Instances
echo -e "${BLUE}EC2 Instances:${NC}"
echo "─────────────────────────────────────────────────────"

PROJECT_NAME=$(terraform output -raw project_name 2>/dev/null || echo "cloud-learning-platform")
ENV=$(terraform output -raw environment 2>/dev/null || echo "dev")

aws ec2 describe-instances \
    --filters "Name=tag:Project,Values=$PROJECT_NAME" "Name=tag:Environment,Values=$ENV" \
    --query 'Reservations[].Instances[].[Tags[?Key==`Name`].Value|[0],InstanceType,State.Name,PrivateIpAddress,PublicIpAddress]' \
    --output table

echo ""

# RDS Status
echo -e "${BLUE}RDS Database:${NC}"
echo "─────────────────────────────────────────────────────"
RDS_ID=$(terraform output -json | jq -r '.rds_endpoint.value' | cut -d':' -f1 2>/dev/null || echo "")

if [ -n "$RDS_ID" ]; then
    aws rds describe-db-instances \
        --query "DBInstances[?contains(Endpoint.Address, '$RDS_ID')].[DBInstanceIdentifier,DBInstanceClass,DBInstanceStatus,AllocatedStorage]" \
        --output table
else
    echo "No RDS instance found"
fi

echo ""

# S3 Buckets
echo -e "${BLUE}S3 Buckets:${NC}"
echo "─────────────────────────────────────────────────────"
aws s3 ls | grep "$PROJECT_NAME" | awk '{print $3, "- Created:", $1, $2}'

echo ""

# Cost Estimate (current month)
echo -e "${BLUE}Cost Estimate (Current Month):${NC}"
echo "─────────────────────────────────────────────────────"
START_DATE=$(date +%Y-%m-01)
END_DATE=$(date +%Y-%m-%d)

aws ce get-cost-and-usage \
    --time-period Start=$START_DATE,End=$END_DATE \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --query 'ResultsByTime[0].Total.BlendedCost' \
    --output text | awk '{printf "Current month: $%.2f\n", $1}'

echo ""

# Terraform Outputs
echo -e "${BLUE}Connection Information:${NC}"
echo "─────────────────────────────────────────────────────"
echo -e "Nginx Public IP:    ${GREEN}$(terraform output -raw nginx_public_ip 2>/dev/null || echo 'N/A')${NC}"
echo -e "RDS Endpoint:       ${GREEN}$(terraform output -raw rds_address 2>/dev/null || echo 'N/A')${NC}"
echo -e "Kafka Private IP:   ${GREEN}$(terraform output -raw kafka_private_ip 2>/dev/null || echo 'N/A')${NC}"

echo ""
echo -e "${BLUE}Quick Access Commands:${NC}"
echo "─────────────────────────────────────────────────────"
NGINX_IP=$(terraform output -raw nginx_public_ip 2>/dev/null || echo "")
if [ -n "$NGINX_IP" ]; then
    echo "Test API:    curl http://$NGINX_IP/health"
    echo "SSH Nginx:   ssh -i your-key.pem ec2-user@$NGINX_IP"
fi

echo ""

