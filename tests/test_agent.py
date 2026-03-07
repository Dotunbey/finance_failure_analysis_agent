
import pytest
from unittest.mock import MagicMock
from src.models import TransactionData, PaymentFailureAnalysis
from src.agent import PaymentFailureAgent
from src.llm_client import HuggingFaceClient

@pytest.fixture
def mock_transaction() -> TransactionData:
    """Fixture providing a mock transaction for testing."""
    return TransactionData(
        transaction_id="TXN-TEST-001",
        amount=5000.0,
        currency="NGN",
        status="failed",
        error_code="E01",
        error_message="Insufficient Funds",
        gateway_response="Declined",
        metadata={}
    )

@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Fixture providing a mocked LLM client."""
    client = MagicMock(spec=HuggingFaceClient)
    client.generate_response.return_value = '{"transaction_id": "TXN-TEST-001", "root_cause": "No money", "suggested_action": "Add money", "confidence_score": 0.9}'
    return client

def test_agent_parsing(mock_llm_client: MagicMock, mock_transaction: TransactionData) -> None:
    """Tests if the agent correctly parses the LLM JSON response.

    Args:
        mock_llm_client: The mocked client dependency.
        mock_transaction: The mocked transaction data.
    """
    agent = PaymentFailureAgent(llm_client=mock_llm_client)
    result = agent.analyze_transaction(mock_transaction)
    
    assert isinstance(result, PaymentFailureAnalysis)
    assert result.transaction_id == "TXN-TEST-001"
    assert result.confidence_score == 0.9
