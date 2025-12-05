# Cloud-Based Learning Platform - Full Stack Deployment ✅

[![Terraform](https://img.shields.io/badge/Terraform-≥1.5.0-623CE4?logo=terraform)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-Infrastructure-FF9900?logo=amazon-aws)](https://aws.amazon.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-RDS-336791?logo=postgresql)](https://www.postgresql.org/)
[![Kafka](https://img.shields.io/badge/Kafka-3.9.0-231F20?logo=apache-kafka)](https://kafka.apache.org/)
[![Status](https://img.shields.io/badge/Status-Live%20&%20Healthy-success)]()

> **CSE363 Cloud Computing Project**  
> ✅ **Phase 1**: AWS Infrastructure (Completed)  
> ✅ **Phase 2**: Microservices Deployment (Completed)  
> 🎉 **Kafka Integration**: Event-driven architecture fully operational  
> 🚀 **Status**: All services running and healthy on AWS  
> 📅 **Deployment Date**: December 5, 2025

---

## 🎊 **Current System Status**

```
┌────────────────────────────────────────────────────────────────┐
│  🟢 ALL SYSTEMS OPERATIONAL (as of December 5, 2025)          │
├────────────────────────────────────────────────────────────────┤
│  ✅ 4 Microservices: Running with health checks passing       │
│  ✅ Kafka Cluster: 3.9.0 operational (6 topics, 18 partitions)│
│  ✅ PostgreSQL RDS: SSL-enabled with schema isolation         │
│  ✅ S3 Storage: 3 buckets configured and accessible           │
│  ✅ Event Integration: All services connected to Kafka        │
└────────────────────────────────────────────────────────────────┘
```

**📖 Quick Links:**
- 🚀 [Deployment Success Summary](DEPLOYMENT_SUCCESS.md)
- 🔍 [Health Check Scripts](#quick-health-check)
- 📚 [Complete API Reference](docs/ALL_APIS_REFERENCE.md)
- 🐳 [Docker Images on Docker Hub](https://hub.docker.com/u/amro1)

---

## 📋 Table of Contents

- [Overview](#overview)
- [🎉 Deployment Status](#-deployment-status)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Phase 1 + 2)](#quick-start-phase-1--2)
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

## 🎉 Deployment Status

### Live Services (AWS EC2)

All microservices are **deployed and operational** on AWS infrastructure:

| Service | Node | Status | Internal Endpoint | Port |
|---------|------|--------|------------------|------|
| **User Management** | App Node 1 | ✅ Healthy | `http://10.0.1.195:8001/health` | 8001 |
| **Chat Service** | App Node 1 | ✅ Healthy | `http://10.0.1.195:8000/health` | 8000 |
| **Document Service** | App Node 2 | ✅ Healthy | `http://10.0.2.179:8002/health` | 8002 |
| **Quiz Service** | App Node 2 | ✅ Healthy | `http://10.0.2.179:8003/health` | 8003 |

### Kafka Infrastructure

| Component | Status | Endpoint | Details |
|-----------|--------|----------|---------|
| **Kafka Broker** | ✅ Running | `10.0.10.231:9092` | v3.9.0, 6 topics active |
| **Zookeeper** | ✅ Running | `10.0.10.231:2181` | Coordination service |

### Infrastructure Status

- ✅ **AWS VPC** - Fully configured with public/private subnets
- ✅ **EC2 Instances** - 4 instances running (Nginx, 2x App Nodes, Kafka)
- ✅ **RDS PostgreSQL** - Running with SSL/TLS encryption
- ✅ **S3 Buckets** - 3 buckets created and accessible
- ✅ **Security Groups** - Configured with least-privilege access
- ✅ **Docker Containers** - All services containerized and running
- ✅ **Database Schemas** - Schema isolation implemented (user_mgmt, chat, document, quiz)
- ✅ **Kafka Cluster** - Kafka 3.9.0 running with 6 topics (3 partitions each)
- ✅ **Event Integration** - All services connected to Kafka for event-driven communication

### Quick Health Check

**Option 1: Automated Health Check Script**

```powershell
# Windows PowerShell
.\deploy\scripts\full-health-check.ps1
```

```bash
# Linux/Mac
bash deploy/scripts/full-health-check.sh
```

**Option 2: Manual Health Checks**

```bash
# From within VPC (SSH to Nginx node first)
curl http://10.0.1.195:8001/health  # User Management
curl http://10.0.1.195:8000/health  # Chat
curl http://10.0.2.179:8002/health  # Document
curl http://10.0.2.179:8003/health  # Quiz

# Test Kafka connectivity
nc -zv 10.0.10.231 9092  # Kafka broker
nc -zv 10.0.10.231 2181  # Zookeeper
```

**Option 3: PowerShell Direct Test**

```powershell
# From your local machine (if VPN/tunnel configured)
Invoke-RestMethod http://10.0.1.195:8001/health
Invoke-RestMethod http://10.0.1.195:8000/health
Invoke-RestMethod http://10.0.2.179:8002/health
Invoke-RestMethod http://10.0.2.179:8003/health
```

### Deployment Timeline

- ✅ **Phase 1 (Nov 2025)**: Infrastructure provisioning with Terraform
  - VPC, subnets, routing, and security groups
  - EC2 instances for Nginx, App Nodes, and Kafka
  - RDS PostgreSQL with multi-schema design
  - S3 buckets for object storage

- ✅ **Phase 2 (Dec 2025)**: Microservices containerization and deployment
  - Four microservices implemented (User-Mgmt, Chat, Document, Quiz)
  - Docker images built and pushed to Docker Hub
  - Services deployed to EC2 with docker-compose
  - Database connections established with SSL/TLS
  - Kafka 3.9.0 installed and configured
  - 6 event topics created (document.uploaded, document.processed, notes.generated, quiz.requested, quiz.generated, chat.message)
  - All services integrated with Kafka for event-driven architecture
  - Health checks verified and monitoring scripts created

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
│
├── terraform/                         # Phase 1: Infrastructure as Code
│   ├── main.tf                       # Root module - orchestrates all resources
│   ├── variables.tf                  # Variable definitions
│   ├── outputs.tf                    # Output values
│   ├── providers.tf                  # Provider configuration
│   ├── terraform.tfvars.example      # Example variables file
│   │
│   ├── modules/                      # Reusable Terraform modules
│   │   ├── vpc/                      # VPC, subnets, routing
│   │   ├── security/                 # Security groups
│   │   ├── ec2_instance/             # Generic EC2 instance
│   │   ├── rds_postgres/             # RDS PostgreSQL
│   │   └── s3_bucket/                # S3 bucket with policies
│   │
│   └── templates/                    # User data templates
│       ├── user_data_nginx.sh        # Nginx setup script
│       ├── user_data_app.sh          # Application node setup
│       └── user_data_kafka.sh        # Kafka/Zookeeper setup
│
├── services/                          # Phase 2: Microservices
│   ├── user-mgmt/                    # User Management Service
│   │   ├── app/                      # FastAPI application
│   │   │   ├── main.py               # Application entry point
│   │   │   ├── config.py             # Configuration management
│   │   │   ├── database.py           # Database connection with SSL
│   │   │   ├── models/               # SQLAlchemy models
│   │   │   ├── routers/              # API endpoints
│   │   │   ├── schemas/              # Pydantic schemas
│   │   │   └── services/             # Business logic
│   │   ├── Dockerfile                # Container definition
│   │   ├── requirements.txt          # Python dependencies
│   │   └── tests/                    # Unit tests
│   │
│   ├── chat/                         # Chat Service (same structure)
│   ├── document/                     # Document Service (same structure)
│   └── quiz/                         # Quiz Service (same structure)
│
├── deploy/                            # Deployment configurations
│   ├── docker-compose.local.yml      # Local development
│   ├── docker-compose.aws.yml        # AWS App Node 1 (User-Mgmt + Chat)
│   ├── docker-compose.aws-node2.yml  # AWS App Node 2 (Document + Quiz)
│   ├── nginx/
│   │   ├── nginx-local.conf          # Local Nginx config
│   │   └── nginx.conf                # AWS Nginx config
│   ├── env/                          # Environment files
│   │   ├── *.env.example             # Example env files
│   │   └── *.aws.env                 # AWS env files (git-ignored)
│   ├── init-db.sql                   # Database initialization
│   └── scripts/                      # Deployment scripts
│       ├── deploy-local.sh
│       ├── deploy-aws.sh
│       ├── health-check.sh
│       └── redeploy-aws.sh
│
├── .github/                           # CI/CD
│   └── workflows/
│       └── ci.yml                    # GitHub Actions workflow
│
└── docs/                             # Documentation
    ├── phase2_overview.md            # Phase 2 architecture
    ├── api_contracts_phase2.md       # API specifications
    ├── kafka_contracts_phase2.md     # Kafka message schemas
    ├── deployment_phase2.md          # Deployment guide
    ├── phase2_testing_checklist.md   # Testing procedures
    ├── ALL_APIS_REFERENCE.md         # Complete API reference
    ├── database_decision.md          # PostgreSQL analysis
    ├── cost_analysis.md              # Cost breakdown
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

## 🚀 Quick Start (Phase 1 + 2)

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

### 10. Deploy Phase 2 Microservices (Optional - Already Deployed)

**Phase 2 is already deployed and running!** But if you need to redeploy:

```bash
# SSH to App Node 1
ssh -i your-key.pem ec2-user@34.201.26.16

# Clone repository
cd ~
git clone https://github.com/AmRo1011/CLOUDE_INFRA.git cloud
cd cloud
git checkout phase-2

# Set environment variables
export USER_MGMT_DB_PASSWORD='YOUR_RDS_PASSWORD'
export CHAT_DB_PASSWORD='YOUR_RDS_PASSWORD'
export RDS_ENDPOINT="YOUR_RDS_ENDPOINT"
export RDS_PORT="5432"
export RDS_DATABASE="platform_main"
# ... (see deploy/env/*.aws.env for complete list)

# Deploy services
cd deploy
docker-compose -f docker-compose.aws.yml up -d

# Verify
curl http://localhost:8001/health  # User Management
curl http://localhost:8000/health  # Chat
```

**Repeat similar steps on App Node 2 for Document and Quiz services.**

See [docs/deployment_phase2.md](docs/deployment_phase2.md) for detailed instructions.

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
- ✅ Services communicate via Kafka events (fully integrated)
- ✅ No direct database or storage access between services
- ✅ Containerized with Docker for consistency and portability
- ✅ SSL/TLS encryption for RDS connections
- ✅ Event-driven architecture with 6 Kafka topics

### Kafka Topics

| Topic | Partitions | Producer | Consumer | Purpose |
|-------|-----------|----------|----------|---------|
| `document.uploaded` | 3 | Document Service | Quiz Service | Document upload notifications |
| `document.processed` | 3 | Document Service | Chat Service | Processing completion events |
| `notes.generated` | 3 | Document Service | Chat Service | AI-generated notes available |
| `quiz.requested` | 3 | Quiz Service | Document Service | Quiz generation requests |
| `quiz.generated` | 3 | Quiz Service | Chat Service | Quiz ready notifications |
| `chat.message` | 3 | Chat Service | Analytics (future) | Chat activity tracking |

### Docker Images

All services are containerized and available on Docker Hub:

- `amro1/user-mgmt:phase2ssl` - User Management Service
- `amro1/chat:phase2ssl` - Chat Service
- `amro1/document:phase2ssl` - Document Service
- `amro1/quiz:phase2ssl` - Quiz Service

**Key Features:**
- Multi-stage builds for optimized image size
- Non-root user for security
- Health checks included
- PostgreSQL async driver (asyncpg) with SSL support

### API Gateway (Nginx)

**Endpoints:**
- `/api/auth/*` → User Management Service (port 8001)
- `/api/users/*` → User Management Service (port 8001)
- `/api/chat/*` → Chat Service (port 8000)
- `/api/documents/*` → Document Service (port 8002)
- `/api/quiz/*` → Quiz Service (port 8003)

### API Documentation

For complete API reference with request/response examples, see:
- **[ALL_APIS_REFERENCE.md](docs/ALL_APIS_REFERENCE.md)** - Complete API documentation
- **[api_contracts_phase2.md](docs/api_contracts_phase2.md)** - Detailed API contracts

**Quick API Test:**
```bash
# Register a new user
curl -X POST http://34.201.26.16:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://34.201.26.16:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!"
  }'
```

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

#### 5. Verify Kafka Topics ✅ COMPLETED

```bash
# SSH to Kafka node (via Nginx jump host)
ssh -i your-key.pem -J ec2-user@<nginx-public-ip> ec2-user@10.0.10.231

# List topics
cd /opt/kafka
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Verify all topics created:
# ✅ chat.message
# ✅ document.processed
# ✅ document.uploaded
# ✅ notes.generated
# ✅ quiz.generated
# ✅ quiz.requested

# Check topic details
bin/kafka-topics.sh --describe --bootstrap-server localhost:9092

# Test producer/consumer
echo "Test message" | bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 --topic chat.message

bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic chat.message --from-beginning --max-messages 1
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

### Deployment Status
- ⭐ **[DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md)** - Complete deployment summary with all endpoints and status

### Phase 1 Documentation
- [Database Decision](docs/database_decision.md) - PostgreSQL vs MongoDB analysis
- [Cost Analysis](docs/cost_analysis.md) - Detailed cost breakdown and optimization
- [Operations Guide](docs/operations.md) - Day-to-day operational procedures

### Phase 2 Documentation
- [Phase 2 Overview](docs/phase2_overview.md) - Architecture and design decisions
- [API Contracts](docs/api_contracts_phase2.md) - Detailed API specifications
- [Complete API Reference](docs/ALL_APIS_REFERENCE.md) - All endpoints with examples
- [Kafka Contracts](docs/kafka_contracts_phase2.md) - Message schemas and topics
- [Deployment Guide](docs/deployment_phase2.md) - Step-by-step deployment instructions
- [Testing Checklist](docs/phase2_testing_checklist.md) - Comprehensive testing guide

### Operational Scripts
- `deploy/scripts/full-health-check.ps1` - Windows health check automation
- `deploy/scripts/full-health-check.sh` - Linux/Mac health check automation
- `deploy/scripts/redeploy-aws.sh` - Quick service redeployment

---

## 🎯 Project Milestones

- ✅ **Phase 1 (Nov 2025)**: Infrastructure as Code
  - VPC with public/private subnets
  - EC2 instances for Nginx, apps, and Kafka
  - RDS PostgreSQL with schema isolation
  - S3 buckets for object storage
  - Security groups and network policies
  
- ✅ **Phase 2 (Dec 5, 2025)**: Microservices Deployment - **COMPLETE**
  - ✅ 4 microservices implemented (User-Mgmt, Chat, Document, Quiz)
  - ✅ Docker containerization with multi-stage builds
  - ✅ Docker Hub image registry (amro1/* images)
  - ✅ Production deployment on AWS EC2
  - ✅ Database connections with SSL/TLS (asyncpg driver)
  - ✅ Kafka 3.9.0 cluster setup and configuration
  - ✅ 6 Kafka topics created (3 partitions each)
  - ✅ Event-driven integration across all services
  - ✅ Health checks and monitoring scripts
  - ✅ Complete API documentation with examples
  - ✅ Deployment automation scripts

### Current System Status (Dec 5, 2025)

🎉 **ALL SERVICES OPERATIONAL**

- **User Management**: ✅ Running, Kafka Connected, DB Connected
- **Chat Service**: ✅ Running, Kafka Connected, DB Connected
- **Document Service**: ✅ Running, Kafka Connected, DB Connected
- **Quiz Service**: ✅ Running, Kafka Connected, DB Connected
- **Kafka Broker**: ✅ Running (10.0.10.231:9092)
- **PostgreSQL RDS**: ✅ Running with SSL
- **S3 Buckets**: ✅ Accessible

📊 See **[DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md)** for complete status and testing instructions.

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

