
import json
import logging
import requests
from typing import Dict, Any

def setup_logging() -> None:
    """Configures script logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def send_test_webhook(url: str, payload: Dict[str, Any]) -> None:
    """Sends a test webhook payload to the deployed agent.

    Args:
        url: The endpoint URL.
        payload: The webhook payload dictionary.
    """
    logging.info(f"Sending webhook to {url}")
    try:
        response = requests.post(url, json=payload, timeout=120.0)
        response.raise_for_status()
        
        data = response.json()
        logging.info("Webhook processed successfully.")
        logging.info(f"Response: {json.dumps(data, indent=2)}")
        
    except requests.exceptions.RequestException as error:
        logging.error(f"Webhook request failed: {error}")
        if hasattr(error, 'response') and error.response is not None:
            logging.error(f"Server response: {error.response.text}")

if __name__ == "__main__":
    setup_logging()
    
    target_url = "http://localhost:8000/webhooks/transactions/failed"
    
    test_payload = {
        "event_type": "payment.failed",
        "data": {
            "transaction_id": "TXN-FLW-LIVE-9921",
            "amount": 150000.0,
            "currency": "NGN",
            "status": "failed",
            "error_code": "05",
            "error_message": "Do Not Honor",
            "gateway_response": "Issuer restricted the card.",
            "metadata": {
                "customer_email": "user@example.com",
                "merchant_id": "MERCH-009"
            }
        }
    }
    
    send_test_webhook(url=target_url, payload=test_payload)
