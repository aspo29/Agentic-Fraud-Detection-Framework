# Agentic Fraud Detection Framework - REST API

## Overview

This is the implementation of **FD-60 (TASK-17.1): Transaction Processing FastAPI Endpoint** - a REST API layer for the Agentic Fraud Detection Framework that processes transaction payloads through an agent pipeline and returns fraud decisions with risk scores.

### Key Features

✅ **FastAPI REST Endpoint** - POST `/api/v1/transaction` for processing transactions  
✅ **API Key Authentication** - Secure endpoint with X-API-Key header validation (returns 401 on missing/invalid key)  
✅ **Input Validation** - Pydantic-based schema validation with field-level error responses (422 on bad payload)  
✅ **OpenAPI/Swagger Documentation** - Interactive Swagger UI at `/docs` with full API documentation  
✅ **Decision Response** - Returns `{decision, risk_score, agent_scores, latency_ms}` within 800ms (p95)  
✅ **Kafka Integration** - Publishes transactions to Kafka and polls for synthesis decisions  
✅ **Mock Fallback** - Uses mock agent scores when Kafka is unavailable (for testing)  
✅ **Structured Logging** - Comprehensive logging with transaction tracking  
✅ **Docker Ready** - Complete Docker & Docker Compose setup for end-to-end deployment

## Project Structure

```
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── .env                             # Environment configuration
├── Dockerfile                       # Container image definition
├── docker-compose.yml               # Multi-service orchestration
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py               # Transaction endpoint implementation
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic request/response models
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py                 # API key authentication
│   ├── services/
│   │   ├── __init__.py
│   │   ├── kafka_service.py        # Kafka producer/consumer
│   │   └── decision_service.py     # Mock decision synthesis
│   └── config/
│       ├── __init__.py
│       └── settings.py             # Application settings
├── core/                            # Agent execution pipeline
│   ├── orchestrator/
│   ├── infrastructure/
│   ├── agents/
│   │   ├── velocity_agent/
│   │   ├── geo_agent/
│   ├── decision_engine/
│   ├── fraud_engine/
│   ├── registry/
│   └── models/
└── tests/
    ├── __init__.py
    ├── test_transaction_api.py     # API Test suite
    ├── test_velocity_agent.py      # Agent Test suite
    └── test_geo_agent.py
```

## Dataflow Pipeline

```
                        transactions.raw (Kafka)
                                  ↓
                        Orchestrator Consumer
                                  ↓
                        Router Service
                                 ↓
                        Executor Pool (async workers)
                                 ↓
                        VelocityAgent  ↔ Redis (sliding window)
                                 ↓
                        GeoAgent
                                ↓
                        BehavioralAgent
                                ↓
                        SyntheticAgent (fusion of all agent scores)
                                ↓
                        Synthesis / Aggregation Layer
                                ↓
                        Decision Engine
                                 ↓
                        fraud.decision (Kafka)
                               ↓
                        BLOCK / REVIEW / ALLOW
```

## API Specification

### Transaction Processing Endpoint

**POST** `/api/v1/transaction`

#### Authentication

- Required header: `X-API-Key: {api_key}`
- Returns `401 Unauthorized` if missing or invalid

#### Request Body (JSON)

```json
{
  "transaction_id": "TXN-12345",
  "amount": 150.5,
  "merchant_id": "MER-ABC123",
  "customer_id": "CUST-XYZ789",
  "merchant_category": "5411",
  "country": "US",
  "card_present": true,
  "three_d_secure": false,
  "metadata": {}
}
```

**Field Validations:**

- `transaction_id`: Required, non-empty string
- `amount`: Required, > 0, ≤ 1,000,000
- `merchant_id`: Required, non-empty string
- `customer_id`: Required, non-empty string
- `merchant_category`: Required, non-empty string (MCC code)
- `country`: Required, 2-letter ISO country code (alpha only)
- `card_present`: Optional boolean (default: false)
- `three_d_secure`: Optional boolean (default: false)
- `metadata`: Optional dictionary for additional data

#### Response (HTTP 200)

```json
{
  "transaction_id": "TXN-12345",
  "decision": "approve",
  "risk_score": 0.15,
  "agent_scores": [
    {
      "agent_name": "velocity_agent",
      "score": 0.1,
      "confidence": 0.95,
      "reasoning": "Normal transaction velocity for customer"
    },
    {
      "agent_name": "amount_agent",
      "score": 0.2,
      "confidence": 0.85,
      "reasoning": "Slightly elevated amount but within historical patterns"
    }
  ],
  "latency_ms": 245.5,
  "timestamp": "2024-04-17T10:30:00.000Z"
}
```

**Decision Values:** `"approve"`, `"deny"`, `"review"`

#### Error Responses

**422 Unprocessable Entity** - Validation error

```json
{
  "detail": "Validation error",
  "errors": [
    {
      "loc": ["amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error"
    }
  ],
  "timestamp": "2024-04-17T10:30:00.000Z"
}
```

**401 Unauthorized** - Missing or invalid API key

```json
{
  "detail": "Invalid API key"
}
```

**500 Internal Server Error** - Server-side error

```json
{
  "detail": "Internal server error: ..."
}
```

### Health Check Endpoint

**GET** `/api/v1/health`

Returns service health status (no authentication required).

```json
{
  "status": "healthy",
  "service": "Agentic Fraud Detection API",
  "version": "1.0.0"
}
```

## Setup & Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Kafka & Zookeeper (if running locally without Docker)
- Redis (optional, for caching)

### Local Development Setup

1. **Clone repository** (if applicable)

```bash
cd /Users/macbookpro/Documents/project/python/Agentic-Fraud-Detection-Framework
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
# Copy and edit .env as needed
cat .env
```

5. **Run development server**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API Base**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Docker Deployment

1. **Build and start services**

```bash
docker-compose up -d
```

This starts:

- FastAPI API (port 8000)
- Kafka & Zookeeper (port 9092)
- Redis (port 6379)
- MLflow (port 5000)
- PostgreSQL (backend for MLflow)

2. **Verify services**

```bash
docker-compose ps
curl -H "X-API-Key: test-api-key-12345" http://localhost:8000/api/v1/health
```

3. **View logs**

```bash
docker-compose logs -f api
```

4. **Stop services**

```bash
docker-compose down
```

## Testing

### Run Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_transaction_api.py::TestTransactionEndpoint::test_valid_transaction -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Test velocity agent
PYTHONPATH=. pytest -v -s test/test_velocity_performance.py
```

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Valid transaction (with API key)
curl -X POST http://localhost:8000/api/v1/transaction \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-12345" \
  -d '{
    "transaction_id": "TXN-TEST-001",
    "amount": 150.50,
    "merchant_id": "MER-ABC123",
    "customer_id": "CUST-XYZ789",
    "merchant_category": "5411",
    "country": "US"
  }'

# Without API key (should return 401)
curl -X POST http://localhost:8000/api/v1/transaction \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "TXN-001", "amount": 100}'

# Invalid payload (should return 422)
curl -X POST http://localhost:8000/api/v1/transaction \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-12345" \
  -d '{"transaction_id": "", "amount": -100}'
```

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" and enter API key: `test-api-key-12345`
3. Try the `/api/v1/transaction` endpoint with test data

## Configuration

### Environment Variables (.env)

```env
# Application
DEBUG=False
HOST=0.0.0.0
PORT=8000

# API Configuration
API_KEY=test-api-key-12345

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
```

### Application Settings (app/config/settings.py)

- `TRANSACTION_TIMEOUT_MS`: 800ms (p95 latency requirement)
- `KAFKA_RESPONSE_TIMEOUT_MS`: 750ms (timeout for Kafka response polling)
- `API_KEY_HEADER`: "X-API-Key" (authentication header name)

## Kafka Integration

### Message Format

**Transaction Published to `fraud-detection-transactions` Topic:**

```json
{
  "transaction_id": "TXN-12345",
  "payload": {
    "transaction_id": "TXN-12345",
    "amount": 150.5,
    "merchant_id": "MER-ABC123",
    "customer_id": "CUST-XYZ789",
    "merchant_category": "5411",
    "country": "US",
    "card_present": true,
    "three_d_secure": false,
    "metadata": {}
  },
  "timestamp": 1713344400.5
}
```

**Decision Expected from `fraud-detection-responses` Topic:**

```json
{
  "transaction_id": "TXN-12345",
  "decision": "approve",
  "risk_score": 0.15,
  "agent_scores": [
    {
      "agent_name": "velocity_agent",
      "score": 0.1,
      "confidence": 0.95,
      "reasoning": "..."
    }
  ]
}
```

### Fallback Behavior

If Kafka is unavailable or times out:

- API uses `DecisionSynthesisService` to generate mock agent scores
- Mock uses heuristics based on transaction parameters
- Response is still returned with latency information

## Performance Characteristics

- **Latency Target**: < 800ms (p95)
- **Throughput**: Depends on Kafka pipeline capacity
- **Timeout Handling**: Kafka response poll times out after 750ms, then returns mock decision
- **Concurrent Requests**: Limited by server resources and Kafka throughput

## Related Issues

- **FD-26**: STORY-17 - Transaction Processing REST API
- **FD-61**: TASK-17.2 - OpenAPI Schema and API Documentation
- **FD-76**: SUBTASK-17.1a - API Key Authentication Middleware (Implemented)
- **FD-27**: STORY-18 - Real-Time Latency Optimisation
- **FD-28**: STORY-19 - Unit & Integration Test Suite
- **FD-29**: STORY-20 - Monitoring, Logging & MLflow Dashboard
- **FD-30**: STORY-21 - Docker Compose Deployment

## Next Steps

1. **FD-61**: Complete OpenAPI schema documentation (already auto-generated)
2. **FD-27**: Implement latency optimizations and performance tuning
3. **FD-28**: Expand test suite with integration tests (≥80% coverage target)
4. **FD-29**: Integrate MLflow tracking and structured logging
5. **FD-30**: Finalize Docker deployment configuration
6. Fallback in process()
7. Real Redis wiring

## Contributing

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Commit messages in format: `FD-XX: Brief description`

## License

TBD
