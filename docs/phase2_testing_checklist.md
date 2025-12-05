# Phase 2 Testing Checklist

Use this checklist to verify all Phase 2 components are working correctly.

## Pre-Deployment Checks

- [ ] All services build successfully: `docker-compose build`
- [ ] No Terraform changes: `terraform plan` shows no changes
- [ ] Environment files configured correctly
- [ ] Database schemas created

## Service Health Checks

### User Management Service (Port 8001)

- [ ] Health check responds: `GET /health`
- [ ] Database connectivity: `GET /health/db`

### Chat Service (Port 8000)

- [ ] Health check responds: `GET /health`
- [ ] Kafka connectivity: `GET /health/kafka`

### Document Service (Port 8002)

- [ ] Health check responds: `GET /health`
- [ ] Kafka connectivity: `GET /health/kafka`

### Quiz Service (Port 8003)

- [ ] Health check responds: `GET /health`
- [ ] Kafka connectivity: `GET /health/kafka`

### Nginx Gateway (Port 80)

- [ ] Gateway health: `GET /health`
- [ ] Routes to User Mgmt: `GET /api/auth/health`
- [ ] Routes to Chat: `GET /api/chat/health`
- [ ] Routes to Document: `GET /api/documents/health`
- [ ] Routes to Quiz: `GET /api/quiz/health`

## Functional Tests

### Authentication Flow

```bash
# 1. Register user
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "role": "student"
  }'
```
- [ ] Returns 201 with user data

```bash
# 2. Login
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```
- [ ] Returns 200 with access_token
- [ ] Token contains correct claims (sub, email, role, permissions)

```bash
# 3. Get profile
curl http://localhost/api/users/me \
  -H "Authorization: Bearer <token>"
```
- [ ] Returns 200 with user profile

### Chat Flow

```bash
# 1. Create conversation
curl -X POST http://localhost/api/chat/conversations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Conversation"}'
```
- [ ] Returns 201 with conversation ID

```bash
# 2. Send message
curl -X POST http://localhost/api/chat/conversations/<conv_id>/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, can you help me study?"}'
```
- [ ] Returns 200 with user_message and assistant_message

```bash
# 3. List conversations
curl http://localhost/api/chat/conversations \
  -H "Authorization: Bearer <token>"
```
- [ ] Returns list of conversations

### Document Flow

```bash
# 1. Upload document
curl -X POST http://localhost/api/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@test.pdf" \
  -F "title=Test Document"
```
- [ ] Returns 201 with document ID
- [ ] Status shows "processing" or "processed"

```bash
# 2. Get document
curl http://localhost/api/documents/<doc_id> \
  -H "Authorization: Bearer <token>"
```
- [ ] Returns document details

```bash
# 3. Get content (after processing)
curl http://localhost/api/documents/<doc_id>/content \
  -H "Authorization: Bearer <token>"
```
- [ ] Returns extracted text content

```bash
# 4. Generate notes
curl -X POST http://localhost/api/documents/<doc_id>/generate-notes \
  -H "Authorization: Bearer <token>"
```
- [ ] Returns generated notes

### Quiz Flow

```bash
# 1. Generate quiz (instructor/admin)
curl -X POST http://localhost/api/quiz/generate \
  -H "Authorization: Bearer <instructor_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "<doc_id>",
    "title": "Test Quiz",
    "num_questions": 5,
    "time_limit_minutes": 15
  }'
```
- [ ] Returns 202 with quiz_id

```bash
# 2. Get quiz
curl http://localhost/api/quiz/<quiz_id> \
  -H "Authorization: Bearer <token>"
```
- [ ] Returns quiz with questions
- [ ] Students don't see correct answers

```bash
# 3. Start attempt (student)
curl -X POST http://localhost/api/quiz/<quiz_id>/start \
  -H "Authorization: Bearer <student_token>"
```
- [ ] Returns attempt_id with time remaining

```bash
# 4. Submit answer
curl -X POST http://localhost/api/quiz/<quiz_id>/attempts/<attempt_id>/answer \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{"question_id": "<q_id>", "selected_option_id": "<opt_id>"}'
```
- [ ] Returns success

```bash
# 5. Submit quiz
curl -X POST http://localhost/api/quiz/<quiz_id>/attempts/<attempt_id>/submit \
  -H "Authorization: Bearer <student_token>"
```
- [ ] Returns score and results

## End-to-End Flow Test

Test the complete flow:

1. [ ] Register as instructor
2. [ ] Upload a document
3. [ ] Wait for processing
4. [ ] Generate notes from document
5. [ ] Generate quiz from document
6. [ ] Register as student
7. [ ] Start chat conversation
8. [ ] Add document as context
9. [ ] Ask questions about document
10. [ ] Take the quiz
11. [ ] Submit and view results

## Kafka Event Tests

Verify events are published:

```bash
# Connect to Kafka container
docker exec -it platform-kafka bash

# List topics
kafka-topics --list --bootstrap-server localhost:9092

# Watch events
kafka-console-consumer --topic document.uploaded --bootstrap-server localhost:9092 --from-beginning
```

- [ ] `document.uploaded` events appear when uploading
- [ ] `document.processed` events appear after processing
- [ ] `quiz.generated` events appear when creating quiz
- [ ] `quiz.graded` events appear when submitting quiz
- [ ] `chat.message` events appear when chatting

## Error Handling Tests

- [ ] Invalid token returns 401
- [ ] Missing permissions return 403
- [ ] Non-existent resources return 404
- [ ] Invalid input returns 400/422 with clear error message

## Performance Checks

- [ ] API response times < 200ms for simple operations
- [ ] File upload works for 50MB files
- [ ] Quiz generation completes within 60 seconds

## Security Checks

- [ ] Passwords are hashed (not stored in plain text)
- [ ] JWT tokens expire correctly
- [ ] Users can only access their own resources
- [ ] CORS headers are set correctly

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| Service Health | | |
| Auth Flow | | |
| Chat Flow | | |
| Document Flow | | |
| Quiz Flow | | |
| E2E Flow | | |
| Kafka Events | | |
| Error Handling | | |
| Security | | |

**Tested By:** _______________  
**Date:** _______________  
**Environment:** _______________

## Issues Found

| # | Description | Severity | Status |
|---|-------------|----------|--------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

