import json
import asyncio
import time
import logging
from typing import Dict, Any, Optional
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from app.config.settings import settings

logger = logging.getLogger(__name__)


class KafkaService:
    """Service for Kafka message handling."""
    
    _producer: Optional[KafkaProducer] = None
    _consumer: Optional[KafkaConsumer] = None
    
    @classmethod
    def get_producer(cls) -> KafkaProducer:
        """Get or create Kafka producer."""
        if cls._producer is None:
            cls._producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
        return cls._producer
    
    @classmethod
    def get_consumer(cls) -> KafkaConsumer:
        """Get or create Kafka consumer."""
        if cls._consumer is None:
            cls._consumer = KafkaConsumer(
                settings.KAFKA_RESPONSE_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id="fraud-detection-api",
                auto_offset_reset='latest',
                enable_auto_commit=True
            )
        return cls._consumer
    
    @classmethod
    async def publish_transaction(cls, transaction_id: str, payload: Dict[str, Any]) -> bool:
        """Publish transaction to Kafka topic.
        
        Args:
            transaction_id: Unique transaction ID
            payload: Transaction payload
            
        Returns:
            bool: True if published successfully
        """
        try:
            producer = cls.get_producer()
            message = {
                "transaction_id": transaction_id,
                "payload": payload,
                "timestamp": time.time()
            }
            
            future = producer.send(settings.KAFKA_TRANSACTION_TOPIC, value=message)
            record_metadata = future.get(timeout=5)
            logger.info(f"Published transaction {transaction_id} to {record_metadata.topic}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to publish transaction {transaction_id}: {e}")
            return False
    
    @classmethod
    async def poll_decision(cls, transaction_id: str, timeout_ms: int = None) -> Optional[Dict[str, Any]]:
        """Poll for decision from Kafka topic.
        
        Args:
            transaction_id: Transaction ID to poll for
            timeout_ms: Maximum time to wait for response
            
        Returns:
            Dict with decision or None if timeout
        """
        timeout_ms = timeout_ms or settings.KAFKA_RESPONSE_TIMEOUT_MS
        start_time = time.time()
        
        try:
            consumer = cls.get_consumer()
            
            while True:
                elapsed_ms = (time.time() - start_time) * 1000
                if elapsed_ms > timeout_ms:
                    logger.warning(f"Timeout waiting for decision for transaction {transaction_id}")
                    return None
                
                remaining_timeout = int((timeout_ms - elapsed_ms) / 1000)
                messages = consumer.poll(timeout_ms=remaining_timeout, max_records=10)
                
                for topic_partition, records in messages.items():
                    for message in records:
                        if message.value.get("transaction_id") == transaction_id:
                            logger.info(f"Received decision for transaction {transaction_id}")
                            return message.value
                
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
        except Exception as e:
            logger.error(f"Error polling for decision {transaction_id}: {e}")
            return None
    
    @classmethod
    def close(cls):
        """Close Kafka connections."""
        if cls._producer:
            cls._producer.close()
        if cls._consumer:
            cls._consumer.close()
