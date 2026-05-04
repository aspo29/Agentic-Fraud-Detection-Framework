import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application
    APP_NAME: str = "Agentic Fraud Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # API Configuration
    API_KEY: str = os.getenv("API_KEY", "test-api-key-12345")
    API_KEY_HEADER: str = "X-API-Key"
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TRANSACTION_TOPIC: str = "fraud-detection-transactions"
    KAFKA_RESPONSE_TOPIC: str = "fraud-detection-responses"
    
    # Timeouts
    TRANSACTION_TIMEOUT_MS: int = 800  # p95 latency requirement
    KAFKA_RESPONSE_TIMEOUT_MS: int = 750
    
    # Redis for caching/async response handling
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # MLflow Configuration
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    MLFLOW_EXPERIMENT_NAME: str = "fraud-detection-transactions"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
