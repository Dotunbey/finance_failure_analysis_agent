
import logging
from typing import Optional
from settings import Settings
from llm_client import HuggingFaceClient
from agent import PaymentFailureAgent

logger = logging.getLogger(__name__)

class AppState:
    """Manages application state and singletons."""
    agent: Optional[PaymentFailureAgent] = None

app_state = AppState()

def get_agent() -> PaymentFailureAgent:
    """FastAPI dependency to retrieve the initialized agent.

    Returns:
        The configured PaymentFailureAgent instance.
        
    Raises:
        RuntimeError: If the agent has not been initialized.
    """
    if app_state.agent is None:
        raise RuntimeError("Agent not initialized.")
    return app_state.agent

def initialize_agent(settings: Settings) -> None:
    """Initializes the LLM client and agent on startup.

    Args:
        settings: The application settings.
    """
    logger.info("Initializing Hugging Face Client and Agent...")
    llm_client = HuggingFaceClient(
        model_name=settings.hf_model_name,
        max_new_tokens=settings.max_new_tokens
    )
    app_state.agent = PaymentFailureAgent(llm_client=llm_client)
    logger.info("Agent successfully initialized.")
