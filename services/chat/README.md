# Chat Service

## Overview
Handles conversational AI, speech-to-text (STT), and text-to-speech (TTS) features.

## Port
- **8000**

## Database
- PostgreSQL Schema: `chat`
- No S3 bucket (as per requirements)

## Responsibilities
- Chat conversations management
- AI-powered responses
- Speech-to-text transcription
- Text-to-speech generation
- Conversation context management

## Kafka Topics
### Produces
- `chat.message` - New chat messages
- `audio.transcription.requested` - STT requests
- `audio.generation.requested` - TTS requests

### Consumes
- `document.processed` - To update conversation context
- `audio.transcription.completed` - STT results
- `audio.generation.completed` - TTS results

## API Endpoints
See `docs/api_contracts_phase2.md` for full API specification.

## Environment Variables
```
DATABASE_URL=postgresql://chat_svc:password@rds-endpoint:5432/platform_main?options=-csearch_path=chat
KAFKA_BOOTSTRAP_SERVERS=kafka-node:9092
OPENAI_API_KEY=your-openai-key
```

## Running Locally
```bash
cd services/chat
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker
```bash
docker build -t chat-service .
docker run -p 8000:8000 --env-file .env chat-service
```

