# streaming/kafka_producer.py
import json
import logging
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer
import asyncio

logger = logging.getLogger(__name__)

class KafkaTransactionProducer:
    """
    Async Kafka producer for sending transactions to a topic.
    """
    
    def __init__(self, bootstrap_servers: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer: Optional[AIOKafkaProducer] = None
    
    async def start(self):
        """Start the producer and establish connection."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        logger.info(f"Kafka producer started, topic={self.topic}")
    
    async def stop(self):
        """Stop the producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def send_transaction(self, transaction: Dict[str, Any], key: Optional[str] = None):
        """
        Send a transaction to Kafka.
        Optionally use a key (e.g., user_id) for partitioning.
        """
        if not self.producer:
            raise RuntimeError("Producer not started. Call start() first.")
        
        key_bytes = key.encode('utf-8') if key else None
        await self.producer.send_and_wait(self.topic, value=transaction, key=key_bytes)
        logger.debug(f"Sent transaction {transaction.get('transaction_id')} to {self.topic}")
    
    async def send_batch(self, transactions: list, key_func=None):
        """Send multiple transactions (no wait for each)."""
        if not self.producer:
            raise RuntimeError("Producer not started.")
        
        for tx in transactions:
            key = key_func(tx) if key_func else None
            key_bytes = key.encode('utf-8') if key else None
            await self.producer.send(self.topic, value=tx, key=key_bytes)
        await self.producer.flush()
        logger.info(f"Sent batch of {len(transactions)} transactions")


# Singleton instance (optional)
_producer_instance = None

async def get_producer(bootstrap_servers: str = "localhost:9092", topic: str = "transactions") -> KafkaTransactionProducer:
    global _producer_instance
    if _producer_instance is None:
        _producer_instance = KafkaTransactionProducer(bootstrap_servers, topic)
        await _producer_instance.start()
    return _producer_instance