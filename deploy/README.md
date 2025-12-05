# Deployment Configuration

This directory contains all deployment-related files for Phase 2 microservices.

## Structure

```
deploy/
├── README.md                    # This file
├── config.env.example          # Environment variables template
├── docker-compose.local.yml    # Local development setup
├── docker-compose.aws.yml      # AWS EC2 deployment setup
├── nginx/
│   └── nginx.conf              # Nginx API gateway configuration
├── env/
│   ├── user-mgmt.env.example   # User Management service env
│   ├── chat.env.example        # Chat service env
│   ├── document.env.example    # Document service env
│   └── quiz.env.example        # Quiz service env
└── scripts/
    ├── deploy-aws.sh           # Deploy to AWS EC2 nodes
    ├── deploy-local.sh         # Start local development
    └── health-check.sh         # Verify all services are running
```

## Quick Start

### Local Development
```bash
# Copy environment template
cp config.env.example .env

# Edit .env with your values
nano .env

# Start all services locally
./scripts/deploy-local.sh

# Or using docker-compose directly
docker-compose -f docker-compose.local.yml up
```

### AWS Deployment
```bash
# Ensure Terraform outputs are available
cd ../terraform && terraform output > ../deploy/terraform-outputs.txt

# Deploy to AWS
./scripts/deploy-aws.sh
```

## Port Assignments
| Service | Port |
|---------|------|
| Chat | 8000 |
| User Management | 8001 |
| Document | 8002 |
| Quiz | 8003 |

## Network Architecture
- Nginx runs on the public EC2 instance and routes traffic to services
- Services run on private EC2 app nodes
- All services communicate through Docker network or direct IP
- Kafka and RDS are accessed via private network addresses

