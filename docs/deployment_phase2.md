# Phase 2 Deployment Guide

This guide covers deploying the Phase 2 microservices to both local development and AWS environments.

## Prerequisites

### Local Development
- Docker Desktop installed and running
- Git
- Text editor for editing `.env` files

### AWS Deployment
- Phase 1 infrastructure deployed (Terraform)
- SSH key for EC2 access
- AWS credentials configured
- Terraform outputs available

## Quick Start - Local Development

### 1. Setup Environment

```bash
cd deploy
cp config.env.example .env
```

Edit `.env` with these minimum values:
```
RDS_ENDPOINT=localhost
RDS_PORT=5432
RDS_DATABASE=platform_main
RDS_MASTER_USER=postgres
RDS_MASTER_PASSWORD=localdevpassword
JWT_SECRET=your-dev-secret-key
```

### 2. Start Services

```bash
./scripts/deploy-local.sh
# OR
docker-compose -f docker-compose.local.yml up -d
```

### 3. Verify Deployment

```bash
./scripts/health-check.sh
```

Or manually:
```bash
curl http://localhost:8001/health  # User Management
curl http://localhost:8000/health  # Chat
curl http://localhost:8002/health  # Document
curl http://localhost:8003/health  # Quiz
curl http://localhost/health       # Nginx Gateway
```

### 4. Access Services

| Service | Direct URL | Via Gateway |
|---------|-----------|-------------|
| User Mgmt | http://localhost:8001 | http://localhost/api/auth/ |
| Chat | http://localhost:8000 | http://localhost/api/chat/ |
| Document | http://localhost:8002 | http://localhost/api/documents/ |
| Quiz | http://localhost:8003 | http://localhost/api/quiz/ |

### 5. View Logs

```bash
docker-compose -f docker-compose.local.yml logs -f

# Specific service
docker-compose -f docker-compose.local.yml logs -f user-mgmt
```

### 6. Stop Services

```bash
docker-compose -f docker-compose.local.yml down

# Remove volumes too
docker-compose -f docker-compose.local.yml down -v
```

## AWS Deployment

### 1. Get Terraform Outputs

```bash
cd terraform
terraform output

# Save to file
terraform output > ../deploy/terraform-outputs.txt
```

Note these values:
- `nginx_public_ip`
- `app_node_1_private_ip`
- `app_node_2_private_ip`
- `rds_endpoint`
- `kafka_private_ip`

### 2. Configure Environment

```bash
cd deploy
cp config.env.example .env
```

Edit `.env` with Terraform outputs:
```
AWS_REGION=us-east-1
RDS_ENDPOINT=<your-rds-endpoint>
RDS_PORT=5432
RDS_DATABASE=platform_main
RDS_MASTER_PASSWORD=<your-secure-password>
KAFKA_BOOTSTRAP_SERVERS=<kafka-private-ip>:9092
JWT_SECRET=<your-production-secret>
NGINX_PUBLIC_IP=<nginx-public-ip>
APP_NODE_1_PRIVATE_IP=<app-node-1-private-ip>
APP_NODE_2_PRIVATE_IP=<app-node-2-private-ip>
```

### 3. Setup SSH Key

```bash
export SSH_KEY_PATH=/path/to/your-key.pem
```

### 4. Initialize Database Schemas

SSH to app node through Nginx bastion:
```bash
ssh -i $SSH_KEY_PATH -J ec2-user@<nginx-ip> ec2-user@<app-node-1-ip>
```

Connect to RDS and run init script:
```bash
psql -h <rds-endpoint> -U postgres -d platform_main < /path/to/init-db.sql
```

### 5. Deploy Services

```bash
./scripts/deploy-aws.sh
```

This script:
1. Updates Nginx configuration with correct IPs
2. Deploys containers to App Node 1 (Chat + User Mgmt)
3. Deploys containers to App Node 2 (Document + Quiz)

### 6. Verify Deployment

```bash
curl http://<nginx-public-ip>/health
curl http://<nginx-public-ip>/api/auth/health
curl http://<nginx-public-ip>/api/chat/health
curl http://<nginx-public-ip>/api/documents/health
curl http://<nginx-public-ip>/api/quiz/health
```

## Manual AWS Deployment (Alternative)

If the automated script doesn't work, deploy manually:

### Deploy to App Node 1

```bash
# SSH to App Node 1 through Nginx
ssh -i $SSH_KEY_PATH -J ec2-user@<nginx-ip> ec2-user@<app-node-1-ip>

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  user-mgmt:
    image: <your-ecr>/user-mgmt:latest
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://postgres:password@<rds-endpoint>:5432/platform_main
      - JWT_SECRET=your-secret
    restart: unless-stopped
  chat:
    image: <your-ecr>/chat:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@<rds-endpoint>:5432/platform_main
      - KAFKA_BOOTSTRAP_SERVERS=<kafka-ip>:9092
    restart: unless-stopped
EOF

# Pull and start
docker-compose pull
docker-compose up -d
```

### Deploy to App Node 2

Same process for Document and Quiz services on ports 8002 and 8003.

### Update Nginx Config

```bash
ssh -i $SSH_KEY_PATH ec2-user@<nginx-ip>

# Edit nginx config
sudo nano /etc/nginx/nginx.conf

# Update upstream IPs
# upstream user_mgmt_service {
#     server <app-node-1-ip>:8001;
# }
# etc...

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

## Troubleshooting

### Services Not Starting

Check Docker logs:
```bash
docker logs platform-user-mgmt
docker logs platform-chat
```

Common issues:
- Database connection failed: Check RDS security group allows traffic from app nodes
- Kafka connection failed: Check Kafka is running and accessible

### Cannot Access via Nginx

```bash
# Check Nginx is running
sudo systemctl status nginx

# Check Nginx config
sudo nginx -t

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Database Connection Issues

```bash
# Test connection from app node
psql -h <rds-endpoint> -U postgres -d platform_main

# Check security groups allow 5432 from app subnet
```

### Health Checks Failing

```bash
# Check if service is running
docker ps

# Check service logs
docker logs <container-name>

# Test locally on the instance
curl localhost:8001/health
```

## Rollback

### Local

```bash
docker-compose -f docker-compose.local.yml down
docker-compose -f docker-compose.local.yml up -d --build
```

### AWS

```bash
# SSH to instance
ssh -i $SSH_KEY_PATH -J ec2-user@<nginx-ip> ec2-user@<app-node-ip>

# Roll back to previous image
docker-compose pull <previous-tag>
docker-compose up -d
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs -f platform-user-mgmt
```

### Check Resources

```bash
docker stats
```

### Health Endpoints

Each service exposes:
- `/health` - Basic health check
- `/health/db` - Database connectivity (User Mgmt)
- `/health/kafka` - Kafka connectivity (Chat, Document, Quiz)

