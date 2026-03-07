#!src/agent.py
import json
import logging
from typing import Iterator
from models import TransactionData, PaymentFailureAnalysis
from llm_client import HuggingFaceClient

logger = logging.getLogger(__name__)

class PaymentFailureAgent:
    """Agent responsible for analyzing payment failures."""

    def __init__(self, llm_client: HuggingFaceClient) -> None:
        self._llm_client = llm_client

    def _build_prompt(self, transaction: TransactionData) -> str:
        """Builds the analysis prompt for a transaction.

        Args:
            transaction: The failed transaction data.

        Returns:
            A formatted prompt string.
        """
        return (
            f"Analyze the following payment failure from Flutterwave gateway.\n"
            f"Transaction ID: {transaction.transaction_id}\n"
            f"Amount: {transaction.amount} {transaction.currency}\n"
            f"Error Code: {transaction.error_code}\n"
            f"Error Message: {transaction.error_message}\n"
            f"Gateway Response: {transaction.gateway_response}\n\n"
            f"Provide a JSON response with the following keys strictly:\n"
            f"'transaction_id' (string), 'root_cause' (string), "
            f"'suggested_action' (string), 'confidence_score' (float between 0 and 1)."
            f"\nDo not include any other text, only the JSON object."
        )

    def _parse_analysis(self, raw_response: str) -> PaymentFailureAnalysis:
        """Parses and validates the LLM response.

        Args:
            raw_response: The raw string response from the LLM.

        Returns:
            A validated PaymentFailureAnalysis object.

        Raises:
            ValueError: If parsing or validation fails.
        """
        try:
            start_index = raw_response.find("{")
            end_index = raw_response.rfind("}") + 1
            if start_index == -1 or end_index == 0:
                raise ValueError("No JSON object found in response.")
            
            json_str = raw_response[start_index:end_index]
            parsed_data = json.loads(json_str)
            return PaymentFailureAnalysis(**parsed_data)
        except (json.JSONDecodeError, ValueError) as error:
            logger.error(f"Failed to parse LLM response: {error}\nRaw output: {raw_response}")
            raise ValueError(f"Invalid LLM response format: {error}") from error

    def analyze_transaction(self, transaction: TransactionData) -> PaymentFailureAnalysis:
        """Analyzes a single failed transaction.

        Args:
            transaction: The transaction data to analyze.

        Returns:
            The analysis report.
        """
        logger.info(f"Analyzing transaction: {transaction.transaction_id}")
        prompt = self._build_prompt(transaction)
        raw_response = self._llm_client.generate_response(prompt)
        return self._parse_analysis(raw_response)
