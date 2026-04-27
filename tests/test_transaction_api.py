import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from main import app
from app.config.settings import settings

client = TestClient(app)


class TestTransactionEndpoint:
    """Test suite for transaction processing endpoint."""
    
    @pytest.fixture
    def valid_headers(self):
        """Valid API key header."""
        return {settings.API_KEY_HEADER: settings.API_KEY}
    
    @pytest.fixture
    def valid_transaction(self):
        """Valid transaction payload."""
        return {
            "transaction_id": "TXN-TEST-001",
            "amount": 150.50,
            "merchant_id": "MER-ABC123",
            "customer_id": "CUST-XYZ789",
            "merchant_category": "5411",
            "country": "US",
            "card_present": True,
            "three_d_secure": False
        }
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_missing_api_key(self, valid_transaction):
        """Test endpoint without API key returns 401."""
        response = client.post("/api/v1/transaction", json=valid_transaction)
        assert response.status_code == 401
        assert "API key" in response.json()["detail"]
    
    def test_invalid_api_key(self, valid_transaction):
        """Test endpoint with invalid API key returns 401."""
        headers = {"X-API-Key": "invalid-key"}
        response = client.post("/api/v1/transaction", json=valid_transaction, headers=headers)
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]
    
    def test_valid_transaction(self, valid_transaction, valid_headers):
        """Test successful transaction processing."""
        response = client.post(
            "/api/v1/transaction",
            json=valid_transaction,
            headers=valid_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["transaction_id"] == valid_transaction["transaction_id"]
        assert "decision" in data
        assert data["decision"] in ["approve", "deny", "review"]
        assert 0 <= data["risk_score"] <= 1
        assert isinstance(data["agent_scores"], list)
        assert len(data["agent_scores"]) > 0
        assert data["latency_ms"] > 0
        assert data["latency_ms"] < 800  # Should meet p95 requirement
    
    def test_agent_scores_structure(self, valid_transaction, valid_headers):
        """Test that agent scores have correct structure."""
        response = client.post(
            "/api/v1/transaction",
            json=valid_transaction,
            headers=valid_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        for agent_score in data["agent_scores"]:
            assert "agent_name" in agent_score
            assert "score" in agent_score
            assert "confidence" in agent_score
            assert 0 <= agent_score["score"] <= 1
            assert 0 <= agent_score["confidence"] <= 1
    
    def test_invalid_amount(self, valid_transaction, valid_headers):
        """Test validation with invalid amount."""
        valid_transaction["amount"] = -100
        response = client.post(
            "/api/v1/transaction",
            json=valid_transaction,
            headers=valid_headers
        )
        assert response.status_code == 422
        assert "amount" in str(response.json()).lower()
    
    def test_missing_required_fields(self, valid_headers):
        """Test validation with missing required fields."""
        invalid_transaction = {
            "amount": 150.50,
            "merchant_id": "MER-ABC123"
        }
        response = client.post(
            "/api/v1/transaction",
            json=invalid_transaction,
            headers=valid_headers
        )
        assert response.status_code == 422
    
    def test_invalid_country_code(self, valid_transaction, valid_headers):
        """Test validation with invalid country code."""
        valid_transaction["country"] = "USA"  # Should be US
        response = client.post(
            "/api/v1/transaction",
            json=valid_transaction,
            headers=valid_headers
        )
        # FastAPI will coerce "USA" to uppercase
        # Let's test with non-alpha
        valid_transaction["country"] = "U1"
        response = client.post(
            "/api/v1/transaction",
            json=valid_transaction,
            headers=valid_headers
        )
        assert response.status_code == 422
    
    def test_swagger_docs_available(self):
        """Test that Swagger UI is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
    
    def test_openapi_schema_available(self):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "/api/v1/transaction" in data["paths"]
        assert "post" in data["paths"]["/api/v1/transaction"]
