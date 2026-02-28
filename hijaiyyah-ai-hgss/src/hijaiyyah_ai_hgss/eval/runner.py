from __future__ import annotations
import time
from typing import Dict, List, Any

from hijaiyyah_ai_hgss.config import Config
from hijaiyyah_ai_hgss.llm.base import LLMBase
from hijaiyyah_ai_hgss.agent.repair_loop import RepairLoopAgent
from hijaiyyah_ai_hgss.eval.dataset import TestCase

def run_evaluation(config: Config, llm: LLMBase, dataset: List[TestCase]) -> List[Dict[str, Any]]:
    results = []
    agent = RepairLoopAgent(config, llm)
    
    for case in dataset:
        start_time = time.time()
        
        # In a real A/B test, we would run both modes.
        # Here we follow the current config mode.
        response, errors, iterations = agent.run(case.user_prompt, case.system_prompt)
        
        latency = (time.time() - start_time) * 1000 # ms
        
        results.append({
            "case_id": case.id,
            "success": len(errors) == 0,
            "iterations": iterations,
            "errors": [e.category.value for e in errors],
            "latency_ms": latency,
            "usage": llm.get_usage().copy() # simplified usage tracking
        })
        
    return results
