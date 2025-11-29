# Cloud-Based Learning Platform - Infrastructure (Phase 1)

[![Terraform](https://img.shields.io/badge/Terraform-≥1.5.0-623CE4?logo=terraform)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-Infrastructure-FF9900?logo=amazon-aws)](https://aws.amazon.com/)

> **CSE363 Cloud Computing Project** - Phase 1: AWS Infrastructure Layer  
> **Deadline**: Thursday, 20/11/2025

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Cost Analysis](#cost-analysis)
- [Services Overview](#services-overview)
- [Database Strategy](#database-strategy)
- [Security & RBAC](#security--rbac)
- [Deployment Guide](#deployment-guide)
- [Operations](#operations)
- [Scaling to Production](#scaling-to-production)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project implements a **cost-optimized, production-ready AWS infrastructure** for a cloud-based learning platform using **Infrastructure as Code (Terraform)**. The platform supports AI-powered educational services including chat, document processing, quiz generation, and user management.

### Key Features

✅ **Microservices Architecture** - Isolated services with clear boundaries  
✅ **Event-Driven Design** - Apache Kafka for asynchronous communication  
✅ **Container-Ready** - EC2 instances configured for Docker/Docker Compose  
✅ **Secure by Default** - Network isolation, encryption, security groups  
✅ **Cost-Optimized** - Dev configuration under $50/month (see [Cost Analysis](docs/cost_analysis.md))  
✅ **Scalable** - Designed to scale from dev to production  
✅ **Well-Documented** - Comprehensive documentation and inline comments  

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────┐
│   Internet  │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│                      VPC (10.0.0.0/16)                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │          Public Subnet (10.0.1.0/24)               │    │
│  │                                                      │    │
│  │   ┌──────────────────┐                             │    │
│  │   │  Nginx Gateway   │ (Load Balancer)             │    │
│  │   │   (t3.micro)     │                             │    │
│  │   └────────┬─────────┘                             │    │
│  │            │                                        │    │
│  └────────────┼────────────────────────────────────────┘    │
│               │                                              │
│  ┌────────────▼────────────────────────────────────────┐    │
│  │      Private App Subnet (10.0.10.0/24)             │    │
│  │                                                      │    │
│  │   ┌──────────────┐       ┌──────────────┐          │    │
│  │   │  App Node 1  │       │  App Node 2  │          │    │
│  │   │  (t3.small)  │       │  (t3.small)  │          │    │
│  │   │              │       │              │          │    │
│  │   │ - Chat Svc   │       │ - Doc Svc    │          │    │
│  │   │ - User Mgmt  │       │ - Quiz Svc   │          │    │
│  │   └──────┬───────┘       └──────┬───────┘          │    │
│  │          │                      │                   │    │
│  │          └──────────┬───────────┘                   │    │
│  │                     │                               │    │
│  │          ┌──────────▼──────────┐                    │    │
│  │          │   Kafka + ZK Node   │                    │    │
│  │          │     (t3.small)      │                    │    │
│  │          └─────────────────────┘                    │    │
│  │                                                      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │        DB Subnet (10.0.20.0/24)                      │    │
│  │                                                      │    │
│  │          ┌─────────────────────┐                     │    │
│  │          │   RDS PostgreSQL    │                     │    │
│  │          │   (db.t3.micro)     │                     │    │
│  │          │                     │                     │    │
│  │          │ Schemas:            │                     │    │
│  │          │ - user_mgmt         │                     │    │
│  │          │ - chat              │                     │    │
│  │          │ - document          │                     │    │
│  │          │ - quiz              │                     │    │
│  │          └─────────────────────┘                     │    │
│  │                                                      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                       AWS S3 (Object Storage)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  User Mgmt   │  │  Document    │  │    Quiz      │      │
│  │   Bucket     │  │   Bucket     │  │   Bucket     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

### Network Architecture

- **VPC**: `10.0.0.0/16`
- **Public Subnets**: `10.0.1.0/24`, `10.0.2.0/24` (2 AZs)
- **Private App Subnets**: `10.0.10.0/24`, `10.0.11.0/24` (2 AZs)
- **DB Subnets**: `10.0.20.0/24`, `10.0.21.0/24` (2 AZs)
- **Internet Gateway**: Public internet access
- **NAT Gateway**: Single NAT for private subnet internet access (cost optimization)

### Security Groups

| SG Name | Purpose | Inbound Rules |
|---------|---------|---------------|
| `nginx-sg` | Nginx gateway | HTTP (80), HTTPS (443) from 0.0.0.0/0, SSH (22) |
| `app-sg` | Application nodes | HTTP (8000-8100) from nginx-sg, inter-app communication |
| `kafka-sg` | Kafka cluster | Kafka (9092), Zookeeper (2181) from app-sg |
| `db-sg` | RDS PostgreSQL | PostgreSQL (5432) from app-sg |

---

## 📁 Project Structure

```
.
├── README.md                          # This file
├── terraform/                         # Terraform infrastructure code
│   ├── main.tf                       # Root module - orchestrates all resources
│   ├── variables.tf                  # Variable definitions
│   ├── outputs.tf                    # Output values
│   ├── providers.tf                  # Provider configuration
│   ├── terraform.tfvars.example      # Example variables file
│   ├── .gitignore                    # Terraform gitignore
│   │
│   ├── modules/                      # Reusable Terraform modules
│   │   ├── vpc/                      # VPC, subnets, routing
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── security/                 # Security groups
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── ec2_instance/             # Generic EC2 instance
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── rds_postgres/             # RDS PostgreSQL
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   └── s3_bucket/                # S3 bucket with policies
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   │
│   └── templates/                    # User data templates
│       ├── user_data_nginx.sh        # Nginx setup script
│       ├── user_data_app.sh          # Application node setup
│       └── user_data_kafka.sh        # Kafka/Zookeeper setup
│
└── docs/                             # Documentation
    ├── database_decision.md          # PostgreSQL vs MongoDB analysis
    ├── cost_analysis.md              # Detailed cost breakdown
    └── operations.md                 # Operational procedures
```

---

## 📋 Prerequisites

### Required Software

1. **Terraform** >= 1.5.0
   ```bash
   # Download from https://www.terraform.io/downloads
   terraform --version
   ```

2. **AWS CLI** >= 2.0
   ```bash
   aws --version
   aws configure
   ```

3. **Git**
   ```bash
   git --version
   ```

### AWS Requirements

1. **AWS Account** with sufficient permissions
2. **AWS Access Keys** configured
3. **EC2 Key Pair** for SSH access (create in AWS Console)
4. **Learner Lab** credentials (if using AWS Academy)

### Permissions Required

- EC2 (full)
- VPC (full)
- RDS (full)
- S3 (full)
- IAM (limited - for instance profiles, if available)

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd CLOUDE_INFRA
```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# OR set environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 3. Create SSH Key Pair

```bash
# In AWS Console: EC2 -> Key Pairs -> Create Key Pair
# Download the .pem file and save it securely
chmod 400 your-key.pem
```

### 4. Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars
```

**Required changes in `terraform.tfvars`:**
```hcl
ec2_key_name = "your-key-pair-name"  # The key pair you created
db_password  = "your-secure-password" # Strong password!
```

### 5. Initialize Terraform

```bash
terraform init
```

### 6. Plan Infrastructure

```bash
terraform plan
```

Review the plan carefully. Terraform will show:
- Resources to be created
- Estimated costs (if using Infracost)

### 7. Deploy Infrastructure

```bash
terraform apply

# Type 'yes' when prompted
```

**Deployment takes ~10-15 minutes**

### 8. Get Outputs

```bash
terraform output

# Get specific output
terraform output nginx_public_ip
```

### 9. Test Connection

```bash
# Get the public IP
NGINX_IP=$(terraform output -raw nginx_public_ip)

# Test health endpoint
curl http://$NGINX_IP/health

# SSH to Nginx gateway
ssh -i your-key.pem ec2-user@$NGINX_IP
```

---

## 💰 Cost Analysis

### Development Configuration (Current)

| Resource | Monthly Cost |
|----------|--------------|
| EC2 Instances (4x) | $52.50 |
| EBS Volumes | $8.80 |
| RDS PostgreSQL | $12.50 |
| S3 Storage | $0.17 |
| NAT Gateway | $33.30 |
| Data Transfer | $0.50 |
| **Total** | **~$108/month** |

### Cost Optimization to $50/month

See detailed analysis in [docs/cost_analysis.md](docs/cost_analysis.md)

**Recommended optimizations:**
1. Use t4g (ARM) instances (-20%)
2. Remove NAT Gateway or use only when needed (-$33)
3. Stop instances when not in use (50% savings)
4. Leverage AWS Free Tier (first 12 months)

**Optimized configuration achieves ~$45-50/month**

---

## 🔧 Services Overview

### Microservices Architecture

| Service | Purpose | Storage | Port |
|---------|---------|---------|------|
| **User Management** | Authentication, RBAC, user profiles | PostgreSQL + S3 | 8001 |
| **Chat Service** | Conversational AI, STT, TTS | PostgreSQL only | 8000 |
| **Document Service** | Upload, processing, note generation | PostgreSQL + S3 | 8002 |
| **Quiz Service** | Quiz generation, grading, feedback | PostgreSQL + S3 | 8003 |

### Service Isolation

- ✅ Each service has dedicated S3 bucket (where needed)
- ✅ Each service has dedicated PostgreSQL schema
- ✅ Services communicate via Kafka events only
- ✅ No direct database or storage access between services

### API Gateway (Nginx)

**Endpoints:**
- `/api/auth/*` → User Management Service
- `/api/users/*` → User Management Service
- `/api/chat/*` → Chat Service
- `/api/documents/*` → Document Service
- `/api/quiz/*` → Quiz Service

---

## 🗄️ Database Strategy

### PostgreSQL on RDS (Selected)

**Why PostgreSQL?**
- ✅ ACID compliance for critical data (users, grades, scores)
- ✅ Strong relational support (joins, foreign keys)
- ✅ JSON/JSONB for semi-structured data
- ✅ AWS RDS managed service (backups, updates, monitoring)
- ✅ Aligns with project requirements

**Why not MongoDB?**
- ❌ No managed service in Learner Lab
- ❌ Requires manual setup and maintenance
- ❌ Less suitable for transactional workloads

### Schema Isolation Strategy

**Single RDS instance with multiple schemas:**

```sql
-- User Management Schema
CREATE SCHEMA user_mgmt;
-- Tables: users, roles, permissions, sessions

-- Chat Schema
CREATE SCHEMA chat;
-- Tables: conversations, messages, context

-- Document Schema
CREATE SCHEMA document;
-- Tables: documents, notes, metadata

-- Quiz Schema
CREATE SCHEMA quiz;
-- Tables: quizzes, questions, responses, scores
```

**Benefits:**
- Cost-effective ($12/month vs $48/month for 4 instances)
- Logical isolation maintained
- Easy to separate later if needed
- All services share connection pool efficiently

**Connection string pattern:**
```
postgresql://user:password@rds-endpoint:5432/platform_main?options=-csearch_path=user_mgmt
```

See full analysis: [docs/database_decision.md](docs/database_decision.md)

---

## 🔒 Security & RBAC

### Network Security

- ✅ All services in private subnets (except Nginx)
- ✅ Security groups with least-privilege rules
- ✅ No direct internet access for app/DB instances
- ✅ Encrypted EBS volumes
- ✅ Encrypted RDS storage
- ✅ S3 server-side encryption

### Application-Level RBAC

Since AWS Learner Lab restricts IAM usage, we implement **custom RBAC service**:

```
┌──────────────────────────────────────────────────────┐
│              User Management Service                 │
│                                                      │
│  ┌────────────────────────────────────────────┐     │
│  │           RBAC Service                     │     │
│  │                                            │     │
│  │  Roles:                                    │     │
│  │  - admin (full access)                     │     │
│  │  - instructor (create/grade quizzes)       │     │
│  │  - student (take quizzes, use services)    │     │
│  │                                            │     │
│  │  Permissions:                              │     │
│  │  - document.upload                         │     │
│  │  - quiz.create                             │     │
│  │  - chat.use                                │     │
│  │  - user.manage                             │     │
│  │                                            │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  JWT Token: { user_id, role, permissions[] }        │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Flow:**
1. User logs in → receives JWT with role
2. Each request includes JWT in Authorization header
3. Service validates JWT and checks permissions
4. Allow or deny based on role/permission

---

## 📖 Deployment Guide

### Step-by-Step Deployment

#### 1. Pre-Deployment Checklist

- [ ] AWS credentials configured
- [ ] EC2 key pair created
- [ ] Terraform installed
- [ ] `terraform.tfvars` configured
- [ ] Budget alerts set up

#### 2. Deploy Infrastructure

```bash
cd terraform

# Initialize
terraform init

# Validate configuration
terraform validate

# Plan (review carefully)
terraform plan -out=tfplan

# Apply
terraform apply tfplan
```

#### 3. Verify Deployment

```bash
# Get outputs
terraform output

# Test Nginx health
curl http://$(terraform output -raw nginx_public_ip)/health

# SSH to Nginx
ssh -i your-key.pem ec2-user@$(terraform output -raw nginx_public_ip)
```

#### 4. Configure Database Schemas

```bash
# SSH to app node
ssh -i your-key.pem ec2-user@<nginx-ip>
# Then SSH tunnel to app node

# Connect to RDS
psql -h <rds-endpoint> -U postgres -d platform_main

# Create schemas
CREATE SCHEMA user_mgmt;
CREATE SCHEMA chat;
CREATE SCHEMA document;
CREATE SCHEMA quiz;

# Create service users
CREATE USER user_mgmt_svc WITH PASSWORD 'password';
GRANT ALL ON SCHEMA user_mgmt TO user_mgmt_svc;

CREATE USER chat_svc WITH PASSWORD 'password';
GRANT ALL ON SCHEMA chat TO chat_svc;

-- Repeat for other services
```

#### 5. Verify Kafka Topics

```bash
# SSH to Kafka node (through bastion)
ssh -i your-key.pem ec2-user@<kafka-private-ip>

# List topics
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Should see:
# - document.uploaded
# - document.processed
# - notes.generated
# - quiz.requested
# - quiz.generated
# - chat.message
# (and others)
```

---

## 🔧 Operations

### Daily Operations

#### Start Infrastructure

```bash
cd terraform
terraform apply -auto-approve
```

#### Stop Infrastructure (Save Costs)

```bash
# Stop EC2 instances (keeps data)
aws ec2 stop-instances --instance-ids \
  $(terraform output -raw nginx_instance_id) \
  $(terraform output -raw app1_instance_id) \
  $(terraform output -raw app2_instance_id) \
  $(terraform output -raw kafka_instance_id)

# Note: RDS and S3 still incur charges
```

#### Destroy Everything

```bash
terraform destroy

# WARNING: This deletes all data!
# Make sure to backup first
```

### Monitoring

#### Check Instance Status

```bash
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=cloud-learning-platform" \
  --query 'Reservations[].Instances[].[InstanceId,State.Name,PrivateIpAddress,PublicIpAddress]' \
  --output table
```

#### Check Costs

```bash
aws ce get-cost-and-usage \
  --time-period Start=2024-12-01,End=2024-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

#### SSH Access

```bash
# Nginx (public)
ssh -i your-key.pem ec2-user@<nginx-public-ip>

# App nodes (through Nginx as bastion)
ssh -i your-key.pem -J ec2-user@<nginx-public-ip> ec2-user@<app-private-ip>
```

### Logs

```bash
# User data logs
ssh ec2-user@<instance-ip>
cat /var/log/user-data-complete.log
cat /var/log/cloud-init-output.log

# Docker logs (after Phase 2)
docker ps
docker logs <container-id>

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Kafka logs
tail -f /opt/kafka/logs/server.log
```

---

## 📈 Scaling to Production

### From Dev-Slim to Production

Current Terraform is designed with variables for easy scaling:

#### 1. Increase Instance Counts

```hcl
# In terraform.tfvars

# Multi-node Kafka cluster
kafka_broker_count = 3

# Multi-node app tier
app_node_count = 3

# Separate RDS per service
enable_separate_rds_per_service = true
```

#### 2. Enable High Availability

```hcl
# Multi-AZ RDS
rds_multi_az = true

# Multiple NAT Gateways
single_nat_gateway = false

# Auto Scaling Groups (Phase 2)
enable_auto_scaling = true
min_instances = 2
max_instances = 10
```

#### 3. Add Application Load Balancer

```hcl
# Replace Nginx EC2 with ALB
use_alb = true
alb_certificate_arn = "arn:aws:acm:..."
```

#### 4. Production-Grade Database

```hcl
db_instance_class = "db.r6g.large"
db_allocated_storage = 100
enable_read_replicas = true
read_replica_count = 2
backup_retention_period = 30
```

#### 5. Enhanced Monitoring

```hcl
enable_cloudwatch_detailed_monitoring = true
enable_vpc_flow_logs = true
enable_rds_performance_insights = true
```

### Estimated Production Costs

| Resource | Monthly Cost |
|----------|--------------|
| EC2 Instances (10x m5.large) | $700 |
| Application Load Balancer | $16 |
| RDS (4x db.m5.large, Multi-AZ) | $800 |
| S3 + Data Transfer | $50 |
| NAT Gateways (2x) | $64 |
| CloudWatch + Monitoring | $50 |
| **Total** | **~$1,680/month** |

---

## ❓ Troubleshooting

### Common Issues

#### 1. Terraform Apply Fails

**Error**: `InvalidKeyPair.NotFound`

**Solution**:
```bash
# Create key pair in AWS Console first
# Or use AWS CLI:
aws ec2 create-key-pair --key-name my-key --query 'KeyMaterial' --output text > my-key.pem
chmod 400 my-key.pem
```

#### 2. Cannot SSH to Instances

**Error**: `Connection timed out`

**Solution**:
```bash
# Check security group allows your IP
aws ec2 describe-security-groups --group-ids <sg-id>

# Update allowed_ssh_cidr_blocks in terraform.tfvars
allowed_ssh_cidr_blocks = ["YOUR_IP/32"]

terraform apply
```

#### 3. RDS Connection Failed

**Error**: `could not connect to server`

**Solution**:
```bash
# RDS is in private subnet
# Must connect from app node or through bastion

# Test from app node:
ssh -i key.pem ec2-user@<app-ip>
psql -h <rds-endpoint> -U postgres -d platform_main
```

#### 4. High Costs

**Solution**:
```bash
# Stop instances when not in use
aws ec2 stop-instances --instance-ids $(terraform output -json | jq -r '.*.value | select(.!=null)')

# Or destroy and recreate
terraform destroy
terraform apply  # When needed again
```

#### 5. User Data Scripts Not Running

**Check logs**:
```bash
ssh ec2-user@<instance-ip>
sudo cat /var/log/cloud-init-output.log
sudo cat /var/log/user-data-complete.log
```

---

## 📚 Additional Documentation

- [Database Decision](docs/database_decision.md) - PostgreSQL vs MongoDB analysis
- [Cost Analysis](docs/cost_analysis.md) - Detailed cost breakdown and optimization
- [Operations Guide](docs/operations.md) - Day-to-day operational procedures

---

## 🤝 Contributing

This is a student project for CSE363. Team members:
- [Your Team Member Names]

---

## 📄 License

Educational project for CSE363 Cloud Computing Course.

---

## 📞 Support

For questions or issues:
1. Check [Troubleshooting](#troubleshooting)
2. Review [AWS Documentation](https://docs.aws.amazon.com/)
3. Ask course instructor or TA

---

**Built with ❤️ for CSE363 Cloud Computing**

