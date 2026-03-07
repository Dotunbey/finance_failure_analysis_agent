
import logging
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from settings import Settings
from models import TransactionData, WebhookPayload, WebhookResponse
from agent import PaymentFailureAgent
from dependencies import get_agent, initialize_agent

def setup_logging(log_level: str) -> None:
    """Configures application logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

settings = Settings()
setup_logging(settings.log_level)

app = FastAPI(
    title="Flutterwave Autonomous Payment Failure Analyst",
    description="Locally hosted LLM agent for analyzing failed transactions via webhooks.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event() -> None:
    """Handles startup actions like loading the model into memory."""
    try:
        initialize_agent(settings)
    except Exception as error:
        logging.error(f"Failed to start application: {error}")
        sys.exit(1)

@app.post(
    "/webhooks/transactions/failed", 
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK
)
async def process_failed_transaction_webhook(
    payload: WebhookPayload,
    agent: PaymentFailureAgent = Depends(get_agent)
) -> WebhookResponse:
    """Webhook endpoint to receive and analyze failed transactions.

    Args:
        payload: The incoming webhook payload containing transaction details.
        agent: The injected PaymentFailureAgent instance.

    Returns:
        A WebhookResponse containing the analysis.
        
    Raises:
        HTTPException: If the analysis fails or payload is invalid.
    """
    if payload.event_type != "payment.failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Unsupported event type. Expected 'payment.failed'."
        )

    try:
        transaction = TransactionData(
            transaction_id=payload.data.get("transaction_id", "UNKNOWN"),
            amount=payload.data.get("amount", 0.0),
            currency=payload.data.get("currency", "UNKNOWN"),
            status=payload.data.get("status", "failed"),
            error_code=payload.data.get("error_code", "UNKNOWN"),
            error_message=payload.data.get("error_message", "UNKNOWN"),
            gateway_response=payload.data.get("gateway_response", "UNKNOWN"),
            metadata=payload.data.get("metadata", {})
        )
        
        analysis = agent.analyze_transaction(transaction)
        
        return WebhookResponse(
            status="success",
            message="Transaction analyzed successfully.",
            analysis=analysis
        )
    except ValueError as error:
        logging.error(f"Validation or parsing error: {error}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=str(error)
        )
    except Exception as error:
        logging.error(f"Unexpected error during analysis: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during analysis."
        )

if __name__ == "__main__":
    uvicorn.run(
        "server:app", 
        host=settings.api_host, 
        port=settings.api_port, 
        reload=False  # Keep false in production, especially with large models
    )
