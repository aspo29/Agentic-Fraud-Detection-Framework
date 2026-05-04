# How to Run the Agentic Fraud Detection Framework

This guide walks you through running the entire end-to-end framework, including the ML model training, starting the infrastructure (Kafka, Redis, Neo4j, MLflow), and running the FastAPI servers.

## Prerequisites

Ensure you have the following installed on your system:
- **Python 3.11+**
- **Docker & Docker Compose** (Crucial for running Kafka, Redis, Neo4j, and MLflow)
- **Git**

---

## Step 1: Environment Setup

First, set up your Python virtual environment and install the required dependencies.

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt
```

---

## Step 2: Start Infrastructure (Docker)

The framework relies on several background services. We use Docker Compose to spin them up simultaneously.

```bash
# Start all background services in detached mode
docker-compose up -d
```

**Services Started:**
- **Redis** (Port `6379`): Used by Velocity and Geo agents for sliding windows.
- **Kafka & Zookeeper** (Port `9092`): Event streaming for transactions.
- **MLflow** (Port `5001`): Model lifecycle tracking.
- **Neo4j** (Port `7687` / `7474`): Graph database for account linkage.
- **PostgreSQL**: Backend database for MLflow.

*You can verify everything is running with `docker-compose ps`.*

---

## Step 3: Generate Data and Train ML Models

Before starting the API, you need to generate synthetic data and train the Machine Learning models so they are registered in MLflow and saved locally.

```bash
# Ensure you are at the project root and your virtual environment is active
export PYTHONPATH=$(pwd)

# 1. Generate Synthetic Transactions
python ml_pipeline/data_generation/synthetic_data_generator.py

# 2. Build the Graph Dataset for Neo4j/GNN
python ml_pipeline/data_generation/graph_dataset_builder.py

# 3. Train the Isolation Forest (Anomaly Detection)
python ml_pipeline/models/isolation_forest_model.py

# 4. Train the Random Forest (Rules Ensemble)
python ml_pipeline/models/random_forest_model.py

# 5. Train the LSTM Behavioral Model
python ml_pipeline/models/lstm_behavioral_model.py

# 6. Train the Graph Neural Network
python ml_pipeline/models/gnn_account_linkage.py
```

*Note: You can view the training metrics and models in the MLflow UI by visiting `http://localhost:5000` in your browser.*

---

## Step 4: Run the Main Fraud Detection API

Now that the infrastructure is up and the models are trained, start the primary FastAPI server which orchestrates the agents.

```bash
# Start the FastAPI server for Transaction Processing
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is now live at:
- **Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** `http://localhost:8000/api/v1/health`

---

## Step 5: Run the Agentic Worker (Pipeline Consumer)

The API publishes transactions to Kafka, but a background worker is needed to actually run the multi-agent orchestration and return a verdict.

```bash
# Open a NEW terminal window and activate the environment
source venv/bin/activate
export PYTHONPATH=$(pwd)

# Start the background agent worker
python worker.py
```

---

## Step 6: Run the OTP Interlock API (Dual-Path)

Open a **new terminal window**, activate the virtual environment, and start the OTP microservice.

```bash
# Activate environment in the new terminal
source venv/bin/activate
export PYTHONPATH=$(pwd)

# Start the OTP Interlock server on a different port
python api/server.py
```

---

## Step 7: Test the System

You can test the end-to-end flow using `curl` or the Swagger UI.

### 1. Test a Transaction (Agent Pipeline)
Send a transaction to the main API. The Orchestrator will route it through the Velocity, Geo, Behavior, and Synthesis agents.

```bash
curl -X POST http://localhost:8000/api/v1/transaction \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-12345" \
  -d '{
    "transaction_id": "TXN-TEST-001",
    "amount": 85000.00,
    "merchant_id": "MER-ABC123",
    "customer_id": "CUST-SITA789",
    "merchant_category": "5411",
    "country": "NP",
    "metadata": {
      "transaction_type": "P2P_TRANSFER"
    }
  }'
```

### 2. Trigger OTP Interlock
If the synthesis agent flags the transaction as suspicious, you can trigger the dual-path OTP flow.

```bash
# Request OTP
curl -X POST http://localhost:8001/api/v1/otp/send \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "CUST-SITA789",
    "transaction_id": "TXN-TEST-001",
    "email": "sita@example.com",
    "phone_number": "+9779800000000"
  }'

# Verify OTP
# (In production, the codes are sent to your phone/email. Ensure credentials are set in .env)
curl -X POST http://localhost:8001/api/v1/otp/verify \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "CUST-SITA789",
    "transaction_id": "TXN-TEST-001",
    "email_otp": "XXXXXX",
    "sms_otp": "YYYYYY",
    "phone_number": "+9779800000000"
  }'
```

> [!IMPORTANT]
> For the OTP Interlock to work in production, you must set your **SendGrid/Twilio/Sparrow** credentials in the `.env` file. If no credentials are provided, the service will raise a configuration error.

---

## Shutting Down

When you are finished testing, you can stop the servers by pressing `Ctrl+C` in their respective terminal windows. To stop and remove the Docker containers, run:

```bash
docker-compose down
```
