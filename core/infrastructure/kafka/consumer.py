import json
import logging
from kafka import KafkaConsumer

from core.orchestrator.router import RouteEngine
from core.infrastructure.kafka.topics import RAW_TRANSACTIONS_TOPIC

logger = logging.getLogger(__name__)


class TransactionConsumer:

    def __init__(self, bootstrap_servers="localhost:9092"):
        self.consumer = KafkaConsumer(
            RAW_TRANSACTIONS_TOPIC,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True
        )

        self.router = RouteEngine()

    def start(self):
        logger.info("Kafka Consumer started. Listening for transactions...")

        for message in self.consumer:
            transaction = message.value

            try:
                self.router.route(transaction)
            except Exception as e:
                logger.error(f"Pipeline error: {e}")