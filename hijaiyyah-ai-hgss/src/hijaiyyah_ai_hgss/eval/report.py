from __future__ import annotations
import json
from typing import List, Dict, Any

def save_report(path: str, metrics: Dict[str, Any], results: List[Dict[str, Any]]):
    report = {
        "summary": metrics,
        "details": results
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {path}")
