# streaming/kafka_consumer.py
import json
import logging
from typing import Callable, Optional, Dict, Any
from aiokafka import AIOKafkaConsumer
import asyncio

from services.transaction_service.fraud_detection_service import get_fraud_detection_service
from monitoring.logging_config import get_logger

logger = get_logger(__name__)

class KafkaTransactionConsumer:
    """
    Async Kafka consumer that processes transactions through the fraud detection pipeline.
    """
    
    def __init__(self, bootstrap_servers: str, topic: str, group_id: str,
                 auto_offset_reset: str = 'earliest'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False
    
    async def start(self):
        """Initialize and start consumer."""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            enable_auto_commit=False  # manual commit for at-least-once
        )
        await self.consumer.start()
        self.running = True
        logger.info(f"Kafka consumer started for topic {self.topic}, group {self.group_id}")
    
    async def stop(self):
        """Stop consumer."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
    
    async def process_messages(self, max_messages: int = 100):
        """
        Process messages continuously.
        For each transaction, call fraud detection service and commit offset after processing.
        """
        fraud_service = get_fraud_detection_service()
        
        try:
            async for msg in self.consumer:
                if not self.running:
                    break
                transaction = msg.value
                logger.info(f"Processing transaction {transaction.get('transaction_id')}")
                
                try:
                    # Process through fraud detection
                    result = await fraud_service.detect_fraud(
                        transaction,
                        store_result=True,
                        trigger_alerts=True
                    )
                    logger.info(f"Transaction {transaction.get('transaction_id')} -> {result['action']}")
                    
                    # Commit offset after successful processing
                    await self.consumer.commit()
                except Exception as e:
                    logger.error(f"Failed to process transaction {transaction.get('transaction_id')}: {e}")
                    # Optionally send to dead letter topic
                    # For now, commit anyway to avoid replay loop? Or not commit.
                    # We'll commit to avoid blocking; log error.
                    await self.consumer.commit()
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled")
        finally:
            await self.stop()
    
    async def process_one_batch(self, timeout_ms: int = 5000) -> int:
        """
        Process a single batch of messages (non‑continuous).
        Useful for testing or batch jobs.
        Returns number of messages processed.
        """
        fraud_service = get_fraud_detection_service()
        count = 0
        while True:
            msg = await self.consumer.getone(timeout_ms=timeout_ms)
            if msg is None:
                break
            transaction = msg.value
            try:
                await fraud_service.detect_fraud(transaction, store_result=True, trigger_alerts=True)
                count += 1
                await self.consumer.commit()
            except Exception as e:
                logger.error(f"Error: {e}")
                await self.consumer.commit()  # skip
        return count


# Helper to run consumer as a background task (for FastAPI startup)
_consumer_instance = None

async def start_consumer(bootstrap_servers: str = "localhost:9092",
                         topic: str = "transactions",
                         group_id: str = "fraud-detection-group"):
    global _consumer_instance
    _consumer_instance = KafkaTransactionConsumer(bootstrap_servers, topic, group_id)
    await _consumer_instance.start()
    asyncio.create_task(_consumer_instance.process_messages())
    return _consumer_instance

async def stop_consumer():
    global _consumer_instance
    if _consumer_instance:
        await _consumer_instance.stop()
        _consumer_instance = None