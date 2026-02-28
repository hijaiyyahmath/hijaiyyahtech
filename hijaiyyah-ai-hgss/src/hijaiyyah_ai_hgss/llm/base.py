from __future__ import annotations
from abc import ABC, abstractmethod

class LLMBase(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generates a response from the LLM."""
        pass

    @abstractmethod
    def get_usage(self) -> dict:
        """Returns token usage information."""
        pass
