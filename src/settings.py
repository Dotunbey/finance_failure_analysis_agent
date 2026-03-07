#!src/settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Settings for the application."""
    hf_model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    max_new_tokens: int = 128
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        """Pydantic configuration class."""
        env_file = ".env"
