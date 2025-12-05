# Document Service

## Overview
Handles document upload, processing, and note generation for the learning platform.

## Port
- **8002**

## Database
- PostgreSQL Schema: `document`
- S3 Bucket: `document-service-storage`

## Responsibilities
- Document upload and storage
- PDF/text extraction
- Note generation from documents
- Document metadata management
- Document search and retrieval

## Kafka Topics
### Produces
- `document.uploaded` - When a new document is uploaded
- `document.processed` - After document text extraction
- `notes.generated` - When notes are created from a document

### Consumes
- (None - this is primarily a producer service)

## API Endpoints
See `docs/api_contracts_phase2.md` for full API specification.

## Environment Variables
```
DATABASE_URL=postgresql://document_svc:password@rds-endpoint:5432/platform_main?options=-csearch_path=document
S3_BUCKET=document-service-storage
AWS_REGION=us-east-1
KAFKA_BOOTSTRAP_SERVERS=kafka-node:9092
```

## Running Locally
```bash
cd services/document
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## Docker
```bash
docker build -t document-service .
docker run -p 8002:8002 --env-file .env document-service
```

