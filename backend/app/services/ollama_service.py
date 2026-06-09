import requests
import logging
import json
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """
    Service to communicate with local Ollama server running Gemma 2B.
    This completely replaces OpenAI GPT dependency.
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.generate_url = f"{self.base_url}/api/generate"
        self.tags_url = f"{self.base_url}/api/tags"

    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(
                self.tags_url,
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def is_model_available(self) -> bool:
        """Check if Gemma model is downloaded."""
        try:
            response = requests.get(self.tags_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                return any(self.model in m for m in models)
            return False
        except Exception:
            return False

    def generate(self, prompt: str) -> str:
        """
        Send prompt to Ollama and get response from Gemma 2B.
        This is the core function that replaces OpenAI API calls.
        """
        if not self.is_available():
            logger.error("Ollama server is not running")
            raise ConnectionError(
                "Ollama is not running. "
                "Please start it with: ollama serve"
            )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 600,
                "stop": ["<end_of_turn>", "<start_of_turn>"]
            }
        }

        try:
            logger.info(
                f"Sending prompt to Ollama "
                f"(model: {self.model}, "
                f"length: {len(prompt)} chars)"
            )

            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                result = data.get("response", "").strip()
                logger.info(
                    f"Ollama responded successfully "
                    f"({len(result)} chars)"
                )
                return result
            else:
                logger.error(
                    f"Ollama error: {response.status_code} "
                    f"- {response.text}"
                )
                raise Exception(
                    f"Ollama returned error: {response.status_code}"
                )

        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            raise Exception(
                "Response took too long. "
                "Try a shorter message or restart Ollama."
            )
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama")
            raise ConnectionError(
                "Cannot connect to Ollama. "
                "Make sure 'ollama serve' is running."
            )
        except Exception as e:
            logger.error(f"Ollama generate error: {e}")
            raise


# Singleton instance
ollama_service = OllamaService()
