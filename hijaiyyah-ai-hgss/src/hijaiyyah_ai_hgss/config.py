from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai_compat")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    mode: str = os.getenv("MODE", "guarded") # 'baseline' or 'guarded'
    max_repair_iters: int = int(os.getenv("MAX_REPAIR_ITERS", "3"))

    hgss_repo: str = os.getenv("HGSS_REPO", "deps/hgss-hc18dc")
    hgss_version_lock: str = os.getenv("HGSS_VERSION_LOCK", "HGSS-HCVM-v1.HC18DC")
    hgss_commit_lock: str = os.getenv("HGSS_COMMIT_LOCK", "e392c68")

def load_config() -> Config:
    # In a real app, we would load .env here.
    return Config()
