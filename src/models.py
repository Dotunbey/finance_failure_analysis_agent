#!src/models.py
from dataclasses import dataclass
from typing import Dict, Any, List
from pydantic import BaseModel, Field

@dataclass
class TransactionData:
    """Data class representing a raw transaction record."""
    transaction_id: str
    amount: float
    currency: str
    status: str
    error_code: str
    error_message: str
    gateway_response: str
    metadata: Dict[str, Any]

class PaymentFailureAnalysis(BaseModel):
    """Pydantic model for validating the LLM analysis output."""
    transaction_id: str = Field(..., description="The ID of the analyzed transaction.")
    root_cause: str = Field(..., description="The determined root cause of the failure.")
    suggested_action: str = Field(..., description="Actionable step to resolve the issue.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the analysis.")

class WebhookPayload(BaseModel):
    """Pydantic model for incoming webhook requests."""
    event_type: str = Field(..., example="payment.failed")
    data: Dict[str, Any] = Field(
        ..., 
        example={
            "transaction_id": "TXN-99812-FLW",
            "amount": 15000.0,
            "currency": "NGN",
            "status": "failed",
            "error_code": "E01",
            "error_message": "Insufficient Funds",
            "gateway_response": "Issuer declined transaction: 51",
            "metadata": {"customer_id": "CUS-123"}
        }
    )

class WebhookResponse(BaseModel):
    """Pydantic model for webhook responses."""
    status: str
    message: str
    analysis: PaymentFailureAnalysis = None
