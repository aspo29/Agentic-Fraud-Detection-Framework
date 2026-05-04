import json
import asyncio
import logging
from kafka import KafkaConsumer, KafkaProducer
from core.orchestrator.router import RouteEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-worker")

async def run_worker():
    logger.info("Starting Agentic Fraud Detection Worker...")
    
    # Initialize Route Engine
    # Note: RouteEngine uses 'localhost' for redis/kafka by default in its __init__
    # We might need to adjust this if running inside Docker, but for local terminal it's fine.
    engine = RouteEngine()
    
    # Initialize Kafka Consumer
    consumer = KafkaConsumer(
        "fraud-detection-transactions",
        bootstrap_servers=["localhost:9092"],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id="agent-worker-group",
        auto_offset_reset='latest'
    )
    
    # Initialize Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=["localhost:9092"],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    logger.info("Worker is ready and listening for transactions...")
    
    try:
        for message in consumer:
            txn_data = message.value
            transaction_id = txn_data.get("transaction_id")
            payload = txn_data.get("payload", {})
            
            logger.info(f"Processing transaction: {transaction_id}")
            
            # Run the agentic pipeline
            results = await engine.route(payload)
            
            # Prepare response
            # Extract scores and decision for the API to consume
            response = {
                "transaction_id": transaction_id,
                "decision": results.get("synthesis", {}).get("decision", "REVIEW"),
                "risk_score": results.get("synthesis", {}).get("risk_score", 0.5),
                "agent_scores": [
                    {
                        "agent_name": "Velocity",
                        "score": results.get("velocity", {}).get("score", 0),
                        "confidence": 1.0,
                        "reasoning": results.get("velocity", {}).get("reasoning", "")
                    },
                    {
                        "agent_name": "Geo",
                        "score": results.get("geo", {}).get("score", 0),
                        "confidence": 1.0,
                        "reasoning": results.get("geo", {}).get("reasoning", "")
                    },
                    {
                        "agent_name": "Behavior",
                        "score": results.get("behavior", {}).get("score", 0),
                        "confidence": 0.8,
                        "reasoning": results.get("behavior", {}).get("reasoning", "")
                    }
                ]
            }
            
            # Publish result back to Kafka
            producer.send("fraud-detection-responses", value=response)
            producer.flush()
            
            logger.info(f"Published decision for: {transaction_id}")
            
    except Exception as e:
        logger.error(f"Worker error: {e}")
    finally:
        consumer.close()
        producer.close()

if __name__ == "__main__":
    asyncio.run(run_worker())
