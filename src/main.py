
import logging
import sys
from typing import Iterator
from settings import Settings
from models import TransactionData
from llm_client import HuggingFaceClient
from agent import PaymentFailureAgent

def setup_logging(log_level: str) -> None:
    """Configures application logging.

    Args:
        log_level: The string representation of the log level.
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def transaction_generator() -> Iterator[TransactionData]:
    """Generates mock transaction data for testing.

    Yields:
        TransactionData instances.
    """
    mock_data = [
        {
            "transaction_id": "TXN-99812-FLW",
            "amount": 15000.0,
            "currency": "NGN",
            "status": "failed",
            "error_code": "E01",
            "error_message": "Insufficient Funds",
            "gateway_response": "Issuer declined transaction: 51",
            "metadata": {"customer_id": "CUS-123"}
        },
        {
            "transaction_id": "TXN-99813-FLW",
            "amount": 50.0,
            "currency": "USD",
            "status": "failed",
            "error_code": "E05",
            "error_message": "Do not honor",
            "gateway_response": "High risk transaction blocked",
            "metadata": {"customer_id": "CUS-456"}
        }
    ]
    
    for data in mock_data:
        yield TransactionData(**data)

if __name__ == "__main__":
    settings = Settings()
    setup_logging(settings.log_level)
    
    llm_client = HuggingFaceClient(
        model_name=settings.hf_model_name,
        max_new_tokens=settings.max_new_tokens
    )
    agent = PaymentFailureAgent(llm_client=llm_client)
    
    transactions = transaction_generator()
    results = agent.process_batch(transactions)
    
    successful_analyses = [result for result in results if result]
    
    for analysis in successful_analyses:
        analysis_dict = {key: value for key, value in analysis.dict().items()}
        logging.info(f"Analysis complete for {analysis.transaction_id}: {analysis_dict}")
