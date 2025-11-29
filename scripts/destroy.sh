#!/bin/bash

# Cloud Learning Platform - Destroy Script
# This script safely destroys all infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}════════════════════════════════════════════════════════${NC}"
echo -e "${RED}   WARNING: Infrastructure Destruction                   ${NC}"
echo -e "${RED}════════════════════════════════════════════════════════${NC}"
echo ""

cd terraform

# Show what will be destroyed
echo -e "${YELLOW}The following resources will be DESTROYED:${NC}"
echo ""
terraform state list
echo ""

echo -e "${RED}⚠ This action will:${NC}"
echo "  • Delete all EC2 instances"
echo "  • Delete RDS database (all data lost)"
echo "  • Delete S3 buckets (all files lost)"
echo "  • Delete VPC and networking"
echo "  • Cannot be undone!"
echo ""

echo -e "${YELLOW}Backup recommendations:${NC}"
echo "  1. Export database: pg_dump"
echo "  2. Download S3 files: aws s3 sync"
echo "  3. Save Terraform state: cp terraform.tfstate backup/"
echo ""

read -p "Have you backed up your data? (yes/no): " BACKUP_CONFIRM
if [ "$BACKUP_CONFIRM" != "yes" ]; then
    echo -e "${RED}Please backup your data first!${NC}"
    exit 1
fi

read -p "Type 'destroy' to confirm destruction: " CONFIRM
if [ "$CONFIRM" != "destroy" ]; then
    echo -e "${GREEN}Operation cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${RED}Destroying infrastructure...${NC}"
terraform destroy -auto-approve

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Infrastructure Destroyed                             ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo "All AWS resources have been removed."
echo "Terraform state files remain for history."
echo ""

