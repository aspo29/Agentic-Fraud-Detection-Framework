from kafka import KafkaProducer
import json


class KafkaEventProducer:

    def __init__(self, bootstrap_servers="localhost:9092"):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    def send(self, topic: str, message: dict):
        self.producer.send(topic, value=message)
        self.producer.flush()