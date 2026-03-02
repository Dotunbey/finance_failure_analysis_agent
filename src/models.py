
from dataclasses import dataclass
from typing import Dict, Any
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
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the transaction")
