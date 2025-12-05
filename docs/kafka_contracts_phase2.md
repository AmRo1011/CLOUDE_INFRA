# Kafka Message Contracts - Phase 2

This document defines the Kafka topic message schemas for event-driven communication between microservices.

## Table of Contents

1. [Overview](#overview)
2. [Topic Naming Convention](#topic-naming-convention)
3. [Common Message Format](#common-message-format)
4. [Document Service Topics](#document-service-topics)
5. [Quiz Service Topics](#quiz-service-topics)
6. [Chat Service Topics](#chat-service-topics)
7. [Consumer Groups](#consumer-groups)

---

## Overview

### Kafka Configuration

| Setting | Value |
|---------|-------|
| Bootstrap Servers | `kafka-node:9092` (AWS) / `kafka:29092` (Local) |
| Zookeeper | `kafka-node:2181` (AWS) / `zookeeper:2181` (Local) |
| Replication Factor | 1 (dev) / 3 (prod) |
| Partitions | 3 (default) |

### Service Communication Matrix

| Producer | Topic | Consumer(s) |
|----------|-------|-------------|
| Document | document.uploaded | Quiz, Chat |
| Document | document.processed | Quiz, Chat |
| Document | notes.generated | Chat |
| Quiz | quiz.requested | Quiz |
| Quiz | quiz.generated | Chat |
| Quiz | quiz.graded | (Notifications - future) |
| Chat | audio.transcription.requested | Chat (STT worker) |
| Chat | audio.transcription.completed | Chat |
| Chat | audio.generation.requested | Chat (TTS worker) |
| Chat | audio.generation.completed | Chat |
| Chat | chat.message | (Analytics - future) |

---

## Topic Naming Convention

Format: `<domain>.<event>`

- **domain**: Service domain (document, quiz, chat, audio)
- **event**: Action that occurred (uploaded, processed, generated, etc.)

Examples:
- `document.uploaded`
- `quiz.generated`
- `audio.transcription.completed`

---

## Common Message Format

All messages follow this envelope structure:

```json
{
  "event_id": "uuid",
  "event_type": "document.uploaded",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0",
  "source": "document-service",
  "correlation_id": "uuid",
  "payload": {
    // Event-specific data
  }
}
```

### Envelope Fields

| Field | Type | Description |
|-------|------|-------------|
| event_id | UUID | Unique identifier for this event |
| event_type | string | Full topic name (domain.event) |
| timestamp | ISO 8601 | When the event was produced |
| version | string | Schema version |
| source | string | Producing service name |
| correlation_id | UUID | Request tracing ID |
| payload | object | Event-specific data |

---

## Document Service Topics

### Topic: `document.uploaded`

**Producer:** Document Service  
**Consumers:** Quiz Service, Chat Service

Emitted when a new document is uploaded successfully.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "document.uploaded",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0",
  "source": "document-service",
  "correlation_id": "request-uuid",
  "payload": {
    "document_id": "doc-uuid",
    "user_id": "user-uuid",
    "title": "Physics Chapter 3",
    "file_name": "physics_ch3.pdf",
    "file_type": "application/pdf",
    "file_size": 2048576,
    "s3_key": "documents/user-uuid/doc-uuid/physics_ch3.pdf",
    "s3_bucket": "document-service-storage"
  }
}
```

### Topic: `document.processed`

**Producer:** Document Service  
**Consumers:** Quiz Service, Chat Service

Emitted when document text extraction is complete.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440001",
  "event_type": "document.processed",
  "timestamp": "2024-01-15T10:35:00.000Z",
  "version": "1.0",
  "source": "document-service",
  "correlation_id": "request-uuid",
  "payload": {
    "document_id": "doc-uuid",
    "user_id": "user-uuid",
    "title": "Physics Chapter 3",
    "status": "processed",
    "content_length": 15000,
    "content_preview": "First 500 characters of extracted text...",
    "metadata": {
      "pages": 25,
      "word_count": 5000,
      "language": "en"
    }
  }
}
```

### Topic: `document.processing_failed`

**Producer:** Document Service  
**Consumers:** (Notifications - future)

Emitted when document processing fails.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440002",
  "event_type": "document.processing_failed",
  "timestamp": "2024-01-15T10:35:00.000Z",
  "version": "1.0",
  "source": "document-service",
  "correlation_id": "request-uuid",
  "payload": {
    "document_id": "doc-uuid",
    "user_id": "user-uuid",
    "error_code": "EXTRACTION_FAILED",
    "error_message": "Unable to extract text from PDF",
    "retry_count": 3
  }
}
```

### Topic: `notes.generated`

**Producer:** Document Service  
**Consumers:** Chat Service

Emitted when AI-generated notes are created.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440003",
  "event_type": "notes.generated",
  "timestamp": "2024-01-15T10:40:00.000Z",
  "version": "1.0",
  "source": "document-service",
  "correlation_id": "request-uuid",
  "payload": {
    "note_id": "note-uuid",
    "document_id": "doc-uuid",
    "user_id": "user-uuid",
    "title": "AI Generated Notes - Physics Chapter 3",
    "summary": "Brief summary of the notes...",
    "key_topics": ["Newton's Laws", "Inertia", "Force", "Momentum"]
  }
}
```

---

## Quiz Service Topics

### Topic: `quiz.requested`

**Producer:** Quiz Service (API request)  
**Consumers:** Quiz Service (Worker)

Emitted when quiz generation is requested.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440010",
  "event_type": "quiz.requested",
  "timestamp": "2024-01-15T11:00:00.000Z",
  "version": "1.0",
  "source": "quiz-service",
  "correlation_id": "request-uuid",
  "payload": {
    "quiz_id": "quiz-uuid",
    "document_id": "doc-uuid",
    "creator_id": "user-uuid",
    "title": "Physics Chapter 3 Quiz",
    "config": {
      "num_questions": 10,
      "question_types": ["multiple_choice", "true_false"],
      "difficulty": "medium",
      "time_limit_minutes": 30
    }
  }
}
```

### Topic: `quiz.generated`

**Producer:** Quiz Service  
**Consumers:** Chat Service, (Notifications - future)

Emitted when quiz generation is complete.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440011",
  "event_type": "quiz.generated",
  "timestamp": "2024-01-15T11:02:00.000Z",
  "version": "1.0",
  "source": "quiz-service",
  "correlation_id": "request-uuid",
  "payload": {
    "quiz_id": "quiz-uuid",
    "document_id": "doc-uuid",
    "creator_id": "user-uuid",
    "title": "Physics Chapter 3 Quiz",
    "status": "draft",
    "num_questions": 10,
    "question_summary": {
      "multiple_choice": 7,
      "true_false": 3
    }
  }
}
```

### Topic: `quiz.generation_failed`

**Producer:** Quiz Service  
**Consumers:** (Notifications - future)

Emitted when quiz generation fails.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440012",
  "event_type": "quiz.generation_failed",
  "timestamp": "2024-01-15T11:02:00.000Z",
  "version": "1.0",
  "source": "quiz-service",
  "correlation_id": "request-uuid",
  "payload": {
    "quiz_id": "quiz-uuid",
    "document_id": "doc-uuid",
    "error_code": "INSUFFICIENT_CONTENT",
    "error_message": "Document does not contain enough content to generate quiz"
  }
}
```

### Topic: `quiz.graded`

**Producer:** Quiz Service  
**Consumers:** (Notifications - future)

Emitted when a quiz attempt is graded.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440013",
  "event_type": "quiz.graded",
  "timestamp": "2024-01-15T11:30:00.000Z",
  "version": "1.0",
  "source": "quiz-service",
  "correlation_id": "request-uuid",
  "payload": {
    "attempt_id": "attempt-uuid",
    "quiz_id": "quiz-uuid",
    "user_id": "user-uuid",
    "score": 80,
    "passing_score": 70,
    "passed": true,
    "correct_answers": 8,
    "total_questions": 10,
    "time_taken_seconds": 900
  }
}
```

---

## Chat Service Topics

### Topic: `audio.transcription.requested`

**Producer:** Chat Service (API)  
**Consumers:** Chat Service (STT Worker)

Emitted when speech-to-text is requested.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440020",
  "event_type": "audio.transcription.requested",
  "timestamp": "2024-01-15T12:00:00.000Z",
  "version": "1.0",
  "source": "chat-service",
  "correlation_id": "request-uuid",
  "payload": {
    "transcription_id": "trans-uuid",
    "conversation_id": "conv-uuid",
    "user_id": "user-uuid",
    "audio_format": "webm",
    "audio_duration_seconds": 15,
    "audio_data_base64": "base64-encoded-audio-or-s3-reference",
    "language_hint": "en"
  }
}
```

### Topic: `audio.transcription.completed`

**Producer:** Chat Service (STT Worker)  
**Consumers:** Chat Service

Emitted when transcription is complete.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440021",
  "event_type": "audio.transcription.completed",
  "timestamp": "2024-01-15T12:00:05.000Z",
  "version": "1.0",
  "source": "chat-service-stt",
  "correlation_id": "request-uuid",
  "payload": {
    "transcription_id": "trans-uuid",
    "conversation_id": "conv-uuid",
    "user_id": "user-uuid",
    "text": "Can you explain Newton's third law?",
    "confidence": 0.95,
    "language": "en",
    "duration_seconds": 15
  }
}
```

### Topic: `audio.generation.requested`

**Producer:** Chat Service (API)  
**Consumers:** Chat Service (TTS Worker)

Emitted when text-to-speech is requested.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440022",
  "event_type": "audio.generation.requested",
  "timestamp": "2024-01-15T12:01:00.000Z",
  "version": "1.0",
  "source": "chat-service",
  "correlation_id": "request-uuid",
  "payload": {
    "generation_id": "gen-uuid",
    "conversation_id": "conv-uuid",
    "message_id": "msg-uuid",
    "text": "Newton's third law states that for every action...",
    "voice": "default",
    "speed": 1.0
  }
}
```

### Topic: `audio.generation.completed`

**Producer:** Chat Service (TTS Worker)  
**Consumers:** Chat Service

Emitted when audio generation is complete.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440023",
  "event_type": "audio.generation.completed",
  "timestamp": "2024-01-15T12:01:10.000Z",
  "version": "1.0",
  "source": "chat-service-tts",
  "correlation_id": "request-uuid",
  "payload": {
    "generation_id": "gen-uuid",
    "conversation_id": "conv-uuid",
    "message_id": "msg-uuid",
    "audio_format": "mp3",
    "audio_duration_seconds": 25,
    "audio_url": "https://s3.../audio/gen-uuid.mp3"
  }
}
```

### Topic: `chat.message`

**Producer:** Chat Service  
**Consumers:** (Analytics - future)

Emitted for analytics/logging purposes.

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440030",
  "event_type": "chat.message",
  "timestamp": "2024-01-15T12:05:00.000Z",
  "version": "1.0",
  "source": "chat-service",
  "correlation_id": "request-uuid",
  "payload": {
    "message_id": "msg-uuid",
    "conversation_id": "conv-uuid",
    "user_id": "user-uuid",
    "role": "user",
    "content_length": 50,
    "has_context": true,
    "context_type": "document"
  }
}
```

---

## Consumer Groups

### Group Naming Convention

Format: `<service>-<purpose>-group`

### Consumer Group Assignments

| Group ID | Service | Topics |
|----------|---------|--------|
| `quiz-document-consumer-group` | Quiz | document.uploaded, document.processed |
| `quiz-worker-group` | Quiz | quiz.requested |
| `chat-document-consumer-group` | Chat | document.processed, notes.generated |
| `chat-quiz-consumer-group` | Chat | quiz.generated |
| `chat-stt-worker-group` | Chat | audio.transcription.requested |
| `chat-tts-worker-group` | Chat | audio.generation.requested |
| `chat-audio-consumer-group` | Chat | audio.transcription.completed, audio.generation.completed |

---

## Error Handling

### Dead Letter Topics

For failed message processing, use dead letter topics:

- `document.uploaded.dlq`
- `quiz.requested.dlq`
- `audio.transcription.requested.dlq`

### Retry Policy

| Attempt | Delay |
|---------|-------|
| 1 | 1 second |
| 2 | 5 seconds |
| 3 | 30 seconds |
| 4+ | Send to DLQ |

---

## Schema Registry (Future)

For production, consider using Confluent Schema Registry with Avro schemas for:

- Schema versioning
- Backward/forward compatibility
- Schema validation

---

## Testing Kafka Locally

### List Topics

```bash
docker exec platform-kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Create Topic

```bash
docker exec platform-kafka kafka-topics --create \
  --topic document.uploaded \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

### Produce Test Message

```bash
docker exec -it platform-kafka kafka-console-producer \
  --topic document.uploaded \
  --bootstrap-server localhost:9092
```

### Consume Messages

```bash
docker exec -it platform-kafka kafka-console-consumer \
  --topic document.uploaded \
  --bootstrap-server localhost:9092 \
  --from-beginning
```

---

## Implementation Notes

### Python (aiokafka)

```python
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json

# Producer
async def produce_event(topic: str, event: dict):
    producer = AIOKafkaProducer(
        bootstrap_servers='kafka:29092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await producer.start()
    try:
        await producer.send_and_wait(topic, event)
    finally:
        await producer.stop()

# Consumer
async def consume_events(topics: list, group_id: str):
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers='kafka:29092',
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    await consumer.start()
    try:
        async for msg in consumer:
            yield msg.value
    finally:
        await consumer.stop()
```

### Event Helper Class

```python
import uuid
from datetime import datetime

def create_event(event_type: str, payload: dict, correlation_id: str = None) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0",
        "source": SERVICE_NAME,
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "payload": payload
    }
```

