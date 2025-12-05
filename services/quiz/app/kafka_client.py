"""
Kafka client for Quiz Service
"""
from aiokafka import AIOKafkaProducer
from typing import Optional
import json
import logging
import uuid
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class KafkaProducerClient:
    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None
    
    async def start(self):
        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            await self._producer.start()
            logger.info("Kafka producer connected")
        except Exception as e:
            logger.error(f"Failed to connect Kafka producer: {e}")
            self._producer = None
    
    async def stop(self):
        if self._producer:
            await self._producer.stop()
    
    def is_connected(self) -> bool:
        return self._producer is not None
    
    async def send_event(self, topic: str, payload: dict, key: Optional[str] = None, correlation_id: Optional[str] = None):
        if not self._producer:
            logger.warning(f"Kafka not connected, skipping: {topic}")
            return
        
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": topic,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "source": settings.SERVICE_NAME,
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "payload": payload
        }
        
        try:
            await self._producer.send_and_wait(topic, event, key=key)
            logger.info(f"Event sent to {topic}")
        except Exception as e:
            logger.error(f"Failed to send event: {e}")


kafka_producer = KafkaProducerClient()

