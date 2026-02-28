from __future__ import annotations
import json
import os
import requests
from hijaiyyah_ai_hgss.llm.base import LLMBase
from hijaiyyah_ai_hgss.config import Config

class OpenAICompatLLM(LLMBase):
    def __init__(self, config: Config):
        self.config = config
        self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.config.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.config.llm_temperature,
            "max_tokens": self.config.llm_max_tokens
        }
        headers = {
            "Authorization": f"Bearer {self.config.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.config.llm_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            usage = data.get("usage", {})
            self.usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
            self.usage["completion_tokens"] += usage.get("completion_tokens", 0)
            self.usage["total_tokens"] += usage.get("total_tokens", 0)
            
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"ERROR: LLM generation failed: {str(e)}"

    def get_usage(self) -> dict:
        return self.usage

class OpenAICompatClient:
    """Industrial wrapper for OpenAICompatLLM."""
    def __init__(self, config: Config):
        self.llm = OpenAICompatLLM(config)
    
    @classmethod
    def from_env(cls):
        from hijaiyyah_ai_hgss.config import load_config
        return cls(load_config())
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return self.llm.generate(system_prompt, user_prompt)
