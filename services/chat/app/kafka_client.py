"""
Kafka client for event publishing and consuming
"""
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from typing import Optional
import json
import logging
import uuid
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class KafkaProducerClient:
    """Kafka producer wrapper"""
    
    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None
    
    async def start(self):
        """Start the Kafka producer"""
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
        """Stop the Kafka producer"""
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer stopped")
    
    def is_connected(self) -> bool:
        """Check if producer is connected"""
        return self._producer is not None
    
    async def send_event(self, topic: str, payload: dict, key: Optional[str] = None, correlation_id: Optional[str] = None):
        """Send event to Kafka topic"""
        if not self._producer:
            logger.warning(f"Kafka producer not connected, skipping event: {topic}")
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
            logger.info(f"Event sent to {topic}: {event['event_id']}")
        except Exception as e:
            logger.error(f"Failed to send event to {topic}: {e}")


class KafkaConsumerClient:
    """Kafka consumer wrapper"""
    
    def __init__(self, topics: list, group_id: str):
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._topics = topics
        self._group_id = group_id
        self._running = False
    
    async def start(self):
        """Start the Kafka consumer"""
        try:
            self._consumer = AIOKafkaConsumer(
                *self._topics,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=self._group_id,
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            await self._consumer.start()
            self._running = True
            logger.info(f"Kafka consumer started for topics: {self._topics}")
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
    
    async def stop(self):
        """Stop the Kafka consumer"""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka consumer stopped")
    
    async def consume(self):
        """Consume messages"""
        if not self._consumer:
            return
        
        async for msg in self._consumer:
            if not self._running:
                break
            yield msg.value


# Global instances
kafka_producer = KafkaProducerClient()
kafka_consumer = KafkaConsumerClient(
    topics=["document.processed", "audio.transcription.completed", "audio.generation.completed"],
    group_id="chat-consumer-group"
)

