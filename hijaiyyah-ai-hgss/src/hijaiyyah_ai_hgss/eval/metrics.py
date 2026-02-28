from __future__ import annotations
from typing import List, Dict, Any

def compute_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    if total == 0: return {}
    
    success_count = sum(1 for r in results if r["success"])
    pass_rate = (success_count / total) * 100
    
    avg_iterations = sum(r["iterations"] for r in results) / total
    avg_latency = sum(r["latency_ms"] for r in results) / total
    
    # Error histogram
    error_hist = {}
    for r in results:
        for err in r["errors"]:
            error_hist[err] = error_hist.get(err, 0) + 1
            
    return {
        "total": total,
        "success_count": success_count,
        "pass_rate_pct": pass_rate,
        "avg_iterations": avg_iterations,
        "avg_latency_ms": avg_latency,
        "error_histogram": error_hist
    }
