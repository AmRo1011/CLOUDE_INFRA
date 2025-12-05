# Quiz Service

## Overview
Handles quiz generation, grading, and feedback for the learning platform.

## Port
- **8003**

## Database
- PostgreSQL Schema: `quiz`
- S3 Bucket: `quiz-service-storage`

## Responsibilities
- Quiz generation from documents
- Quiz question management
- Quiz taking and submission
- Automated grading
- Feedback generation
- Score tracking

## Kafka Topics
### Produces
- `quiz.generated` - When a quiz is created
- `quiz.graded` - When a quiz submission is graded

### Consumes
- `document.uploaded` - Trigger quiz generation from new documents
- `document.processed` - Use extracted text for quiz generation
- `quiz.requested` - Handle quiz generation requests

## API Endpoints
See `docs/api_contracts_phase2.md` for full API specification.

## Environment Variables
```
DATABASE_URL=postgresql://quiz_svc:password@rds-endpoint:5432/platform_main?options=-csearch_path=quiz
S3_BUCKET=quiz-service-storage
AWS_REGION=us-east-1
KAFKA_BOOTSTRAP_SERVERS=kafka-node:9092
OPENAI_API_KEY=your-openai-key
```

## Running Locally
```bash
cd services/quiz
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Docker
```bash
docker build -t quiz-service .
docker run -p 8003:8003 --env-file .env quiz-service
```

