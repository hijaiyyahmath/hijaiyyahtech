from __future__ import annotations
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class TestCase:
    id: str
    task: str
    system_prompt: str
    user_prompt: str

def load_dataset(path: str) -> list[TestCase]:
    cases = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            cases.append(TestCase(
                id=data["id"],
                task=data["task"],
                system_prompt=data["system_prompt"],
                user_prompt=data["user_prompt"]
            ))
    return cases

def load_jsonl_cases(path: str) -> list[dict]:
    """Loads JSONL cases as raw dictionaries for industrial harness."""
    cases = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            cases.append(json.loads(line))
    return cases
