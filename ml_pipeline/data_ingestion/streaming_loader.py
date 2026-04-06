"""
Streaming Data Loader
Consumes real-time transaction data from Kafka and prepares it for ML pipeline.
Supports batch processing and checkpointing.
"""

import json
import logging
import threading
import time
from typing import Callable, Optional, Dict, Any, List
from datetime import datetime
from collections import deque
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingDataLoader:
    """
    Real-time data loader for streaming transactions.
    Consumes from Kafka, applies transformations, and pushes to ML pipeline.
    """
    
    def __init__(self, 
                 bootstrap_servers: str = "localhost:9092",
                 topic: str = "transactions",
                 group_id: str = "fraud_ml_group",
                 batch_size: int = 100,
                 batch_timeout_ms: int = 5000):
        """
        Initialize streaming loader.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            topic: Kafka topic to consume from
            group_id: Consumer group ID
            batch_size: Number of records to accumulate before processing
            batch_timeout_ms: Maximum time to wait for batch
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms
        
        self.consumer = None
        self.is_running = False
        self.consumer_thread = None
        self.batch_buffer = deque(maxlen=batch_size * 2)
        self.callbacks = []
        self.last_commit_time = time.time()
    
    def _init_kafka_consumer(self):
        """Initialize Kafka consumer (lazy)."""
        try:
            from kafka import KafkaConsumer
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='latest',
                enable_auto_commit=False,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8') if x else None
            )
            logger.info(f"Connected to Kafka topic: {self.topic}")
        except ImportError:
            raise ImportError("kafka-python not installed. Run: pip install kafka-python")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def register_callback(self, callback: Callable[[List[Dict]], None]):
        """
        Register a callback function to receive batches of transactions.
        
        Args:
            callback: Function that takes a list of transaction dicts and processes them
        """
        self.callbacks.append(callback)
    
    def _process_batch(self, batch: List[Dict]):
        """Process a batch of transactions through all registered callbacks."""
        if not batch:
            return
        
        logger.info(f"Processing batch of {len(batch)} transactions")
        for callback in self.callbacks:
            try:
                callback(batch)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def _consumer_loop(self):
        """Main consumer loop running in separate thread."""
        while self.is_running:
            try:
                # Poll for messages with timeout
                msg_pack = self.consumer.poll(timeout_ms=1000)
                for topic_partition, messages in msg_pack.items():
                    for msg in messages:
                        # Add to buffer
                        transaction = msg.value
                        transaction['_kafka_offset'] = msg.offset
                        transaction['_kafka_partition'] = msg.partition
                        transaction['_kafka_timestamp'] = msg.timestamp
                        self.batch_buffer.append(transaction)
                        
                        # Check if batch is ready
                        if len(self.batch_buffer) >= self.batch_size:
                            batch = list(self.batch_buffer)
                            self.batch_buffer.clear()
                            self._process_batch(batch)
                            
                            # Commit offsets
                            self.consumer.commit()
                            self.last_commit_time = time.time()
                
                # Check for timeout-based batch
                if (len(self.batch_buffer) > 0 and 
                    (time.time() - self.last_commit_time) * 1000 >= self.batch_timeout_ms):
                    batch = list(self.batch_buffer)
                    self.batch_buffer.clear()
                    self._process_batch(batch)
                    self.consumer.commit()
                    self.last_commit_time = time.time()
                    
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                time.sleep(1)
    
    def start(self):
        """Start consuming messages in background thread."""
        if self.is_running:
            logger.warning("Streaming loader is already running")
            return
        
        self._init_kafka_consumer()
        self.is_running = True
        self.consumer_thread = threading.Thread(target=self._consumer_loop, daemon=True)
        self.consumer_thread.start()
        logger.info("Streaming data loader started")
    
    def stop(self):
        """Stop consuming and clean up."""
        self.is_running = False
        if self.consumer_thread:
            self.consumer_thread.join(timeout=5)
        if self.consumer:
            self.consumer.close()
        logger.info("Streaming data loader stopped")
    
    def process_single_message(self, message: Dict) -> Dict:
        """
        Process a single transaction message (for testing or direct ingestion).
        
        Args:
            message: Transaction dictionary
        
        Returns:
            Processed message with added metadata
        """
        message['_processed_at'] = datetime.utcnow().isoformat()
        # Simulate basic feature extraction
        message['_features'] = self._extract_basic_features(message)
        return message
    
    def _extract_basic_features(self, transaction: Dict) -> Dict:
        """Extract basic features from a raw transaction."""
        features = {}
        
        # Amount features
        amount = transaction.get('amount', 0)
        features['amount_log'] = np.log(amount + 1) if amount > 0 else 0
        features['amount_normalized'] = min(amount / 10000, 1.0)
        
        # Time features
        timestamp = transaction.get('timestamp')
        if timestamp:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            features['hour_of_day'] = timestamp.hour
            features['day_of_week'] = timestamp.weekday()
            features['is_weekend'] = 1 if timestamp.weekday() >= 5 else 0
        
        return features
    
    def simulate_stream(self, data_source: str, interval_seconds: float = 0.1, limit: Optional[int] = None):
        """
        Simulate a stream from a static dataset (for testing).
        
        Args:
            data_source: Path to CSV or DataFrame
            interval_seconds: Delay between messages
            limit: Maximum number of messages to send
        """
        if isinstance(data_source, str):
            df = pd.read_csv(data_source)
        elif isinstance(data_source, pd.DataFrame):
            df = data_source
        else:
            raise ValueError("data_source must be file path or DataFrame")
        
        records = df.to_dict('records')
        if limit:
            records = records[:limit]
        
        logger.info(f"Simulating stream of {len(records)} records")
        for i, record in enumerate(records):
            processed = self.process_single_message(record)
            self._process_batch([processed])
            time.sleep(interval_seconds)
            if i % 100 == 0:
                logger.info(f"Simulated {i+1}/{len(records)} transactions")

# Helper for batch streaming from Kafka
class KafkaBatchLoader:
    """
    Simple batch loader for offline training using historical Kafka data.
    """
    
    def __init__(self, bootstrap_servers: str = "localhost:9092", topic: str = "transactions"):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
    
    def fetch_batch(self, start_offset: int = 0, max_records: int = 10000) -> List[Dict]:
        """
        Fetch a batch of historical records from Kafka.
        
        Args:
            start_offset: Starting offset
            max_records: Maximum number of records to fetch
        """
        from kafka import KafkaConsumer
        consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        # Seek to start offset
        for partition in consumer.assignment():
            consumer.seek(partition, start_offset)
        
        records = []
        for msg in consumer:
            records.append(msg.value)
            if len(records) >= max_records:
                break
        
        consumer.close()
        return records

# Example usage
if __name__ == "__main__":
    # For testing with simulated data
    loader = StreamingDataLoader()
    
    # Define a simple callback to print received transactions
    def print_batch(batch):
        print(f"Received {len(batch)} transactions")
        for tx in batch[:3]:  # print first 3
            print(f"  {tx.get('transaction_id')}: ${tx.get('amount')}")
    
    loader.register_callback(print_batch)
    
    # Simulate stream from a CSV file (create sample if needed)
    # loader.simulate_stream("data/synthetic/generated_transactions.csv", interval_seconds=0.05, limit=200)
    
    # For real Kafka:
    # loader.start()
    # time.sleep(60)
    # loader.stop()