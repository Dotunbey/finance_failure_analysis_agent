#!src/llm_client.py
import logging
from typing import Any
from transformers import pipeline

logger = logging.getLogger(__name__)

class HuggingFaceClient:
    """Client for interacting with a locally hosted Hugging Face model."""

    def __init__(self, model_name: str, max_new_tokens: int) -> None:
        self._model_name = model_name
        self._max_new_tokens = max_new_tokens
        self._pipeline = self._initialize_pipeline()

    def _initialize_pipeline(self) -> Any:
        """Initializes the Hugging Face text generation pipeline.

        Returns:
            The loaded transformers pipeline.
            
        Raises:
            RuntimeError: If model loading fails.
        """
        try:
            logger.info(f"Loading Hugging Face model: {self._model_name}")
            return pipeline(
                "text-generation",
                model=self._model_name,
                device_map="auto"
            )
        except Exception as error:
            logger.error(f"Failed to load model {self._model_name}: {error}")
            raise RuntimeError(f"Model initialization error: {error}") from error

    @property
    def model_name(self) -> str:
        """str: Gets the model name."""
        return self._model_name

    @model_name.setter
    def model_name(self, value: str) -> None:
        """Sets the model name."""
        self._model_name = value

    def generate_response(self, prompt: str) -> str:
        """Generates a response from the local Hugging Face model.

        Args:
            prompt: The prompt to send to the model.

        Returns:
            The text response from the model.

        Raises:
            RuntimeError: If generation fails.
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            formatted_prompt = self._pipeline.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            outputs = self._pipeline(
                formatted_prompt, 
                max_new_tokens=self._max_new_tokens,
                do_sample=False,
                return_full_text=False
            )
            return outputs[0].get("generated_text", "").strip()
        except Exception as error:
            logger.error(f"Failed to generate response: {error}")
            raise RuntimeError(f"Text generation error: {error}") from error
