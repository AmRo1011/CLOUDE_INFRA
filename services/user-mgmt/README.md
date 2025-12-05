# User Management Service

## Overview
Handles authentication, authorization, RBAC, and user profile management.

## Port
- **8001**

## Database
- PostgreSQL Schema: `user_mgmt`
- S3 Bucket: `user-management-storage`

## Responsibilities
- User registration and login
- JWT token generation and validation
- Role-based access control (admin, instructor, student)
- Permission management
- User profile CRUD operations

## API Endpoints
See `docs/api_contracts_phase2.md` for full API specification.

## Environment Variables
```
DATABASE_URL=postgresql://user_mgmt_svc:password@rds-endpoint:5432/platform_main?options=-csearch_path=user_mgmt
JWT_SECRET=your-secret-key
JWT_EXPIRATION=3600
S3_BUCKET=user-management-storage
AWS_REGION=us-east-1
```

## Running Locally
```bash
cd services/user-mgmt
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Docker
```bash
docker build -t user-mgmt-service .
docker run -p 8001:8001 --env-file .env user-mgmt-service
```

