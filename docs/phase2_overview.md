# Phase 2 Overview - Microservices & Containers

## Summary

Phase 2 implements the containerized microservices layer on top of the Phase 1 AWS infrastructure. This phase delivers four fully functional services that power the Cloud Learning Platform.

## What Was Built

### Microservices Implemented

| Service | Port | Description |
|---------|------|-------------|
| **User Management** | 8001 | Authentication, RBAC, user profiles |
| **Chat** | 8000 | Conversational AI, STT/TTS |
| **Document** | 8002 | Document upload, processing, notes |
| **Quiz** | 8003 | Quiz generation, taking, grading |

### Technology Stack

- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (via SQLAlchemy async)
- **Message Queue**: Apache Kafka (aiokafka)
- **Storage**: AWS S3 (boto3)
- **Authentication**: JWT (python-jose)
- **Containerization**: Docker
- **Orchestration**: Docker Compose

## Architecture

```
                    ┌─────────────────────────┐
                    │    Nginx API Gateway    │
                    │       (Port 80)         │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  User Mgmt    │    │   App Node 1     │    │   App Node 2     │
│   Service     │    │                  │    │                  │
│  (Port 8001)  │    │ ┌──────────────┐ │    │ ┌──────────────┐ │
└───────┬───────┘    │ │ Chat Service │ │    │ │ Document Svc │ │
        │            │ │  (Port 8000) │ │    │ │  (Port 8002) │ │
        │            │ └──────────────┘ │    │ └──────────────┘ │
        │            │ ┌──────────────┐ │    │ ┌──────────────┐ │
        │            │ │ User Mgmt    │ │    │ │  Quiz Svc    │ │
        │            │ │  (Port 8001) │ │    │ │  (Port 8003) │ │
        │            │ └──────────────┘ │    │ └──────────────┘ │
        │            └────────┬─────────┘    └────────┬─────────┘
        │                     │                       │
        └─────────────────────┼───────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Kafka Broker    │
                    │   (Port 9092)     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  RDS PostgreSQL   │
                    │   (Port 5432)     │
                    └───────────────────┘
```

## Service Details

### User Management Service

**Responsibilities:**
- User registration and authentication
- JWT token generation and validation
- Role-based access control (admin, instructor, student)
- User profile management

**Key Endpoints:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Authenticate and get token
- `GET /api/users/me` - Get current user profile
- `GET /api/users/` - List all users (admin only)

### Chat Service

**Responsibilities:**
- Manage conversations and messages
- AI-powered responses (OpenAI integration)
- Document context for conversations
- Speech-to-text and text-to-speech (via Kafka events)

**Key Endpoints:**
- `POST /api/chat/conversations` - Create conversation
- `POST /api/chat/conversations/{id}/messages` - Send message, get AI response
- `POST /api/chat/conversations/{id}/context` - Add document context

**Kafka Topics:**
- Produces: `chat.message`, `audio.transcription.requested`
- Consumes: `document.processed`, `audio.transcription.completed`

### Document Service

**Responsibilities:**
- Document upload to S3
- Text extraction (PDF, DOCX, TXT, MD)
- AI-powered note generation
- Document metadata management

**Key Endpoints:**
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/{id}` - Get document details
- `GET /api/documents/{id}/content` - Get extracted text
- `POST /api/documents/{id}/generate-notes` - AI notes

**Kafka Topics:**
- Produces: `document.uploaded`, `document.processed`, `notes.generated`

### Quiz Service

**Responsibilities:**
- Quiz generation from document content
- Quiz question management
- Quiz attempt tracking
- Automated grading

**Key Endpoints:**
- `POST /api/quiz/generate` - Generate quiz from document
- `GET /api/quiz/{id}` - Get quiz with questions
- `POST /api/quiz/{id}/start` - Start quiz attempt
- `POST /api/quiz/{id}/attempts/{attempt_id}/submit` - Submit for grading

**Kafka Topics:**
- Produces: `quiz.generated`, `quiz.graded`
- Consumes: `document.processed`

## Deployment

### Local Development

```bash
cd deploy
cp config.env.example .env
# Edit .env with your values

./scripts/deploy-local.sh
# OR
docker-compose -f docker-compose.local.yml up
```

### AWS Deployment

```bash
cd deploy
./scripts/deploy-aws.sh
```

## Project Structure

```
services/
├── user-mgmt/           # User Management Service
│   ├── app/
│   │   ├── main.py      # FastAPI application
│   │   ├── config.py    # Settings
│   │   ├── database.py  # DB connection
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── routers/     # API routes
│   │   ├── services/    # Business logic
│   │   └── utils/       # Helpers
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── chat/                # Chat Service (same structure)
├── document/            # Document Service (same structure)
└── quiz/                # Quiz Service (same structure)

deploy/
├── docker-compose.local.yml  # Local development
├── docker-compose.aws.yml    # AWS deployment
├── nginx/
│   └── nginx.conf           # API Gateway config
├── env/                     # Service env templates
├── scripts/
│   ├── deploy-local.sh
│   ├── deploy-aws.sh
│   └── health-check.sh
└── init-db.sql             # Database schema

.github/
└── workflows/
    └── ci.yml              # CI/CD pipeline
```

## Environment Variables

All services require these environment variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Secret for JWT signing |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address |
| `AWS_REGION` | AWS region |

Service-specific variables are documented in `deploy/env/*.env.example`.

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **On PR to phase-2**: Run tests, validate Docker build
2. **On merge to phase-2**: Build and push images to ECR

## Integration with Phase 1

Phase 2 uses Phase 1 infrastructure without modifications:

- **VPC/Networking**: Same subnets, security groups
- **EC2 Instances**: Docker pre-installed
- **RDS PostgreSQL**: Uses schemas created in Phase 1
- **S3 Buckets**: Uses buckets created in Phase 1
- **Kafka**: Uses broker deployed in Phase 1

## Next Steps (Phase 3)

- Enhanced monitoring (CloudWatch, Prometheus)
- Auto-scaling configuration
- Production CI/CD with blue-green deployment
- Performance optimization

