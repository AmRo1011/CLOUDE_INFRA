# API Contracts - Phase 2

This document defines the REST API contracts for all microservices in Phase 2.

## Table of Contents

1. [General Information](#general-information)
2. [Authentication](#authentication)
3. [User Management Service API](#user-management-service-api)
4. [Chat Service API](#chat-service-api)
5. [Document Service API](#document-service-api)
6. [Quiz Service API](#quiz-service-api)

---

## General Information

### Base URLs

| Environment | Base URL |
|------------|----------|
| Local Development | `http://localhost` |
| AWS (via Nginx) | `http://<nginx-public-ip>` |

### Common Headers

```
Content-Type: application/json
Authorization: Bearer <jwt-token>  # Required for protected endpoints
```

### Common Response Format

**Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": { ... }
  }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |

---

## Authentication

### JWT Token Structure

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "student",
  "permissions": ["chat.use", "quiz.take", "document.view"],
  "iat": 1699900000,
  "exp": 1699986400
}
```

### Roles and Permissions

| Role | Permissions |
|------|------------|
| admin | All permissions |
| instructor | document.upload, document.view, document.delete, quiz.create, quiz.grade, chat.use |
| student | document.view, quiz.take, chat.use |

---

## User Management Service API

**Base Path:** `/api/auth/` and `/api/users/`  
**Port:** 8001

### Authentication Endpoints

#### POST /api/auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "student",
      "created_at": "2024-01-15T10:30:00Z"
    }
  },
  "message": "User registered successfully"
}
```

#### POST /api/auth/login

Authenticate and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "student"
    }
  }
}
```

#### POST /api/auth/logout

Invalidate current session.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

#### POST /api/auth/refresh

Refresh access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 86400
  }
}
```

#### GET /api/auth/health

Health check endpoint.

**Response (200):**
```json
{
  "status": "healthy",
  "service": "user-mgmt",
  "version": "1.0.0"
}
```

### User Management Endpoints

#### GET /api/users/me

Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "permissions": ["chat.use", "quiz.take", "document.view"],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### PUT /api/users/me

Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "first_name": "Johnny",
  "last_name": "Doe"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "Johnny",
    "last_name": "Doe",
    "role": "student",
    "updated_at": "2024-01-16T08:00:00Z"
  }
}
```

#### GET /api/users/ (Admin only)

List all users.

**Headers:** `Authorization: Bearer <token>`  
**Required Permission:** `user.manage`

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `role` (string): Filter by role

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "users": [
      {
        "id": "uuid",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

#### GET /api/users/{user_id} (Admin only)

Get specific user by ID.

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### PUT /api/users/{user_id}/role (Admin only)

Update user role.

**Request:**
```json
{
  "role": "instructor"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "User role updated successfully"
}
```

---

## Chat Service API

**Base Path:** `/api/chat/`  
**Port:** 8000

### Endpoints

#### GET /api/chat/health

Health check endpoint.

**Response (200):**
```json
{
  "status": "healthy",
  "service": "chat",
  "version": "1.0.0",
  "kafka": "connected"
}
```

#### POST /api/chat/conversations

Create a new conversation.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "title": "Study Session - Physics"
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Study Session - Physics",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### GET /api/chat/conversations

List user's conversations.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (int): Page number
- `limit` (int): Items per page

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "conversations": [
      {
        "id": "uuid",
        "title": "Study Session - Physics",
        "last_message": "Can you explain Newton's laws?",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T11:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5
    }
  }
}
```

#### GET /api/chat/conversations/{conversation_id}

Get conversation with messages.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Study Session - Physics",
    "messages": [
      {
        "id": "uuid",
        "role": "user",
        "content": "Can you explain Newton's laws?",
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": "uuid",
        "role": "assistant",
        "content": "Newton's laws of motion are three fundamental principles...",
        "created_at": "2024-01-15T10:30:05Z"
      }
    ],
    "context": [
      {
        "type": "document",
        "document_id": "uuid",
        "title": "Physics Textbook Ch. 3"
      }
    ]
  }
}
```

#### POST /api/chat/conversations/{conversation_id}/messages

Send a message and get AI response.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "content": "Can you explain Newton's third law with an example?"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "user_message": {
      "id": "uuid",
      "role": "user",
      "content": "Can you explain Newton's third law with an example?",
      "created_at": "2024-01-15T10:35:00Z"
    },
    "assistant_message": {
      "id": "uuid",
      "role": "assistant",
      "content": "Newton's third law states that for every action...",
      "created_at": "2024-01-15T10:35:03Z"
    }
  }
}
```

#### POST /api/chat/conversations/{conversation_id}/context

Add document context to conversation.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "document_id": "uuid"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Document context added to conversation"
}
```

#### DELETE /api/chat/conversations/{conversation_id}

Delete a conversation.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "message": "Conversation deleted successfully"
}
```

---

## Document Service API

**Base Path:** `/api/documents/`  
**Port:** 8002

### Endpoints

#### GET /api/documents/health

Health check endpoint.

**Response (200):**
```json
{
  "status": "healthy",
  "service": "document",
  "version": "1.0.0",
  "kafka": "connected",
  "s3": "connected"
}
```

#### POST /api/documents/upload

Upload a new document.

**Headers:**  
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Required Permission:** `document.upload`

**Request (form-data):**
- `file`: File (PDF, DOCX, TXT, MD)
- `title`: Document title
- `description`: Optional description

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Physics Chapter 3",
    "file_name": "physics_ch3.pdf",
    "file_type": "application/pdf",
    "file_size": 2048576,
    "status": "processing",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "message": "Document uploaded. Processing started."
}
```

#### GET /api/documents/

List user's documents.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (int): Page number
- `limit` (int): Items per page
- `status` (string): Filter by status (uploaded, processing, processed, error)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "documents": [
      {
        "id": "uuid",
        "title": "Physics Chapter 3",
        "file_name": "physics_ch3.pdf",
        "file_type": "application/pdf",
        "file_size": 2048576,
        "status": "processed",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 10
    }
  }
}
```

#### GET /api/documents/{document_id}

Get document details.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Physics Chapter 3",
    "description": "Newton's Laws of Motion",
    "file_name": "physics_ch3.pdf",
    "file_type": "application/pdf",
    "file_size": 2048576,
    "status": "processed",
    "content_preview": "First 500 characters of extracted text...",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

#### GET /api/documents/{document_id}/download

Get pre-signed URL for download.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "download_url": "https://s3.amazonaws.com/...",
    "expires_in": 3600
  }
}
```

#### GET /api/documents/{document_id}/content

Get extracted text content.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "document_id": "uuid",
    "content": "Full extracted text content...",
    "extracted_at": "2024-01-15T10:35:00Z"
  }
}
```

#### DELETE /api/documents/{document_id}

Delete a document.

**Headers:** `Authorization: Bearer <token>`  
**Required Permission:** `document.delete`

**Response (200):**
```json
{
  "status": "success",
  "message": "Document deleted successfully"
}
```

### Notes Endpoints

#### POST /api/documents/{document_id}/notes

Create note from document.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "title": "Key Concepts - Newton's Laws",
  "content": "My notes about the document..."
}
```

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "document_id": "uuid",
    "title": "Key Concepts - Newton's Laws",
    "content": "My notes about the document...",
    "created_at": "2024-01-15T11:00:00Z"
  }
}
```

#### GET /api/documents/{document_id}/notes

List notes for a document.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "notes": [
      {
        "id": "uuid",
        "title": "Key Concepts - Newton's Laws",
        "content": "My notes...",
        "created_at": "2024-01-15T11:00:00Z"
      }
    ]
  }
}
```

#### POST /api/documents/{document_id}/generate-notes

Auto-generate notes using AI.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "AI Generated Notes",
    "content": "## Summary\n\nThis document covers...\n\n## Key Points\n\n1. ...",
    "created_at": "2024-01-15T11:05:00Z"
  },
  "message": "Notes generated successfully"
}
```

---

## Quiz Service API

**Base Path:** `/api/quiz/`  
**Port:** 8003

### Endpoints

#### GET /api/quiz/health

Health check endpoint.

**Response (200):**
```json
{
  "status": "healthy",
  "service": "quiz",
  "version": "1.0.0",
  "kafka": "connected",
  "s3": "connected"
}
```

#### POST /api/quiz/generate

Generate quiz from document.

**Headers:** `Authorization: Bearer <token>`  
**Required Permission:** `quiz.create`

**Request:**
```json
{
  "document_id": "uuid",
  "title": "Physics Chapter 3 Quiz",
  "num_questions": 10,
  "question_types": ["multiple_choice", "true_false"],
  "time_limit_minutes": 30
}
```

**Response (202):**
```json
{
  "status": "success",
  "data": {
    "quiz_id": "uuid",
    "status": "generating",
    "estimated_time": 30
  },
  "message": "Quiz generation started"
}
```

#### GET /api/quiz/

List available quizzes.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (int): Page number
- `limit` (int): Items per page
- `status` (string): Filter by status

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "quizzes": [
      {
        "id": "uuid",
        "title": "Physics Chapter 3 Quiz",
        "num_questions": 10,
        "time_limit_minutes": 30,
        "status": "published",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5
    }
  }
}
```

#### GET /api/quiz/{quiz_id}

Get quiz details (without answers for students).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Physics Chapter 3 Quiz",
    "description": "Test your knowledge of Newton's Laws",
    "time_limit_minutes": 30,
    "num_questions": 10,
    "passing_score": 70,
    "questions": [
      {
        "id": "uuid",
        "question_text": "What is Newton's First Law also known as?",
        "question_type": "multiple_choice",
        "points": 1,
        "options": [
          {"id": "uuid", "text": "Law of Inertia"},
          {"id": "uuid", "text": "Law of Acceleration"},
          {"id": "uuid", "text": "Law of Action-Reaction"},
          {"id": "uuid", "text": "Law of Gravity"}
        ]
      }
    ]
  }
}
```

#### POST /api/quiz/{quiz_id}/start

Start a quiz attempt.

**Headers:** `Authorization: Bearer <token>`  
**Required Permission:** `quiz.take`

**Response (201):**
```json
{
  "status": "success",
  "data": {
    "attempt_id": "uuid",
    "quiz_id": "uuid",
    "started_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-01-15T11:00:00Z",
    "time_remaining_seconds": 1800
  }
}
```

#### POST /api/quiz/{quiz_id}/attempts/{attempt_id}/answer

Submit answer for a question.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "question_id": "uuid",
  "selected_option_id": "uuid"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "question_id": "uuid",
    "answered": true
  }
}
```

#### POST /api/quiz/{quiz_id}/attempts/{attempt_id}/submit

Submit quiz for grading.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "attempt_id": "uuid",
    "status": "graded",
    "score": 80,
    "passing_score": 70,
    "passed": true,
    "correct_answers": 8,
    "total_questions": 10,
    "completed_at": "2024-01-15T10:45:00Z",
    "results": [
      {
        "question_id": "uuid",
        "question_text": "What is Newton's First Law also known as?",
        "your_answer": "Law of Inertia",
        "correct_answer": "Law of Inertia",
        "is_correct": true,
        "points_earned": 1
      }
    ]
  }
}
```

#### GET /api/quiz/{quiz_id}/attempts

List user's attempts for a quiz.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "attempts": [
      {
        "id": "uuid",
        "started_at": "2024-01-15T10:30:00Z",
        "completed_at": "2024-01-15T10:45:00Z",
        "score": 80,
        "status": "graded"
      }
    ]
  }
}
```

#### PUT /api/quiz/{quiz_id} (Instructor only)

Update quiz settings.

**Headers:** `Authorization: Bearer <token>`  
**Required Permission:** `quiz.create`

**Request:**
```json
{
  "title": "Updated Quiz Title",
  "time_limit_minutes": 45,
  "status": "published"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Updated Quiz Title",
    "time_limit_minutes": 45,
    "status": "published",
    "updated_at": "2024-01-16T09:00:00Z"
  }
}
```

#### DELETE /api/quiz/{quiz_id} (Instructor only)

Delete a quiz.

**Headers:** `Authorization: Bearer <token>`  
**Required Permission:** `quiz.create`

**Response (200):**
```json
{
  "status": "success",
  "message": "Quiz deleted successfully"
}
```

---

## Error Codes Reference

| Code | Description |
|------|-------------|
| AUTH_INVALID_CREDENTIALS | Invalid email or password |
| AUTH_TOKEN_EXPIRED | JWT token has expired |
| AUTH_TOKEN_INVALID | JWT token is invalid |
| AUTH_INSUFFICIENT_PERMISSIONS | User lacks required permission |
| USER_NOT_FOUND | User ID does not exist |
| USER_EMAIL_EXISTS | Email already registered |
| DOCUMENT_NOT_FOUND | Document ID does not exist |
| DOCUMENT_PROCESSING_FAILED | Document processing error |
| DOCUMENT_TOO_LARGE | File exceeds size limit |
| DOCUMENT_INVALID_TYPE | Unsupported file type |
| QUIZ_NOT_FOUND | Quiz ID does not exist |
| QUIZ_GENERATION_FAILED | Quiz generation error |
| QUIZ_ATTEMPT_EXPIRED | Time limit exceeded |
| QUIZ_ALREADY_SUBMITTED | Attempt already submitted |
| CONVERSATION_NOT_FOUND | Conversation ID does not exist |
| RATE_LIMIT_EXCEEDED | Too many requests |
| INTERNAL_ERROR | Unexpected server error |

