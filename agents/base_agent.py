"""Base agent class with common functionality."""

import os
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
from loguru import logger
from datetime import datetime

from database import get_db


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(
        self,
        agent_name: str,
        prompt_file: str,
        model_config_path: str = "config/model_config.yaml",
    ):
        self.agent_name = agent_name
        self.db = get_db()

        # Load model configuration
        with open(model_config_path) as f:
            config = yaml.safe_load(f)

        self.model_config = config["agent_models"].get(
            agent_name, config["models"]["primary"]
        )
        self.global_model_config = config["models"][
            self.model_config.get("model", "primary")
        ]

        # Initialize Anthropic client
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Load system prompt
        prompt_path = Path("prompts/agents") / prompt_file
        with open(prompt_path) as f:
            self.system_prompt = f.read()

        logger.info(f"Initialized {agent_name}")

    def create_message(
        self,
        user_message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Create a message with Claude using configured settings."""
        cache_namespace = self.model_config.get("cache_namespace", self.agent_name)

        # Prepare message parameters
        params = {
            "model": self.global_model_config["model"],
            "max_tokens": max_tokens or self.global_model_config.get("max_tokens", 8000),
            "temperature": temperature or self.model_config.get("temperature", 0.7),
            "system": self.system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        }

        # Add cache control if enabled
        if self.global_model_config.get("cache_control", {}).get("enabled"):
            cache_key = f"{cache_namespace}_{datetime.now().strftime('%Y%m%d')}"
            params["cache_control"] = {
                "enabled": True,
                "type": "persistent",
                "key": cache_key,
            }

        try:
            response = self.client.messages.create(**params)
            return {
                "content": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "stop_reason": response.stop_reason,
            }
        except Exception as e:
            logger.error(f"Error creating message in {self.agent_name}: {e}")
            raise

    def update_status(
        self,
        status: str,
        error_message: Optional[str] = None,
        metrics: Optional[Dict] = None,
    ):
        """Update agent status in database."""
        try:
            self.db.update_agent_status(
                agent_name=self.agent_name,
                status=status,
                error_message=error_message,
                metrics=metrics,
            )
        except Exception as e:
            logger.error(f"Error updating status for {self.agent_name}: {e}")

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """Main execution method. Must be implemented by subclasses."""
        pass

    def __enter__(self):
        """Context manager entry."""
        self.update_status("running")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is not None:
            self.update_status("error", error_message=str(exc_val))
            logger.error(f"{self.agent_name} failed: {exc_val}")
            return False
        else:
            self.update_status("idle")
            return True
