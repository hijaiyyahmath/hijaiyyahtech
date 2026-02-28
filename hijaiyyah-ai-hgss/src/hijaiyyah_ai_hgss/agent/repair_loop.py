from __future__ import annotations
import json
import re
import os
import uuid
from typing import Tuple, List, Dict, Any
from pathlib import Path

from hijaiyyah_ai_hgss.config import Config
from hijaiyyah_ai_hgss.llm.base import LLMBase
from hijaiyyah_ai_hgss.taxonomy import ValidationError, ErrorCategory
from hijaiyyah_ai_hgss.prompts.templates import (
    BASE_SYSTEM_PROMPT, 
    REPAIR_SYSTEM_PROMPT, 
    REPAIR_FEEDBACK_TEMPLATE, 
    format_errors
)
from hijaiyyah_ai_hgss.validators.schema_frozen import validate_schema
from hijaiyyah_ai_hgss.validators.cbor_event_hash import validate_event_sha256
from hijaiyyah_ai_hgss.validators.autofill import autofill_event_and_artifacts
from hijaiyyah_ai_hgss.validators.hgss_oracle import hgss_oracle_verify

class RepairLoopAgent:
    def __init__(self, config: Config, llm: LLMBase):
        self.config = config
        self.llm = llm

    def run(self, user_prompt: str, system_prompt: str = BASE_SYSTEM_PROMPT, case_id: str = "default") -> Tuple[str, List[ValidationError], int, str]:
        """
        Runs the LLM generation and repair loop.
        Returns: (final_response, errors, iterations_used, run_dir)
        """
        run_id = str(uuid.uuid4())[:8]
        run_dir = os.path.join("artifacts", "runs", run_id, f"case_{case_id}")
        os.makedirs(run_dir, exist_ok=True)

        iterations = 0
        current_response = self.llm.generate(system_prompt, user_prompt)
        
        # Guarded (Repair) Mode
        while iterations <= self.config.max_repair_iters:
            iterations += 1
            
            # 1. Extraction
            json_text = self._extract_json(current_response)
            if not json_text:
                errors = [ValidationError(ErrorCategory.FORMAT_INVALID_JSON, "Could not extract valid JSON from response")]
            else:
                try:
                    data = json.loads(json_text)
                    
                    # 2. Schema Validation (Strict)
                    errors = validate_schema(data)
                    
                    if not errors:
                        # 3. Mode B logic: AUTOFILL hashes and artifacts
                        if self.config.mode == "guarded":
                            print(f"Applying Deterministic Autofill to case {case_id}...")
                            data = autofill_event_and_artifacts(data, run_dir)
                            
                        # 4. Canonical Hash Check (just to be sure)
                        errors = validate_event_sha256(data)
                        
                        if not errors:
                            # 5. HGSS Oracle Verification (The Ground Truth)
                            evidence_path = os.path.join(run_dir, "event_single.json")
                            errors = hgss_oracle_verify(self.config.hgss_repo, evidence_path)
                            
                except json.JSONDecodeError as e:
                    errors = [ValidationError(ErrorCategory.FORMAT_INVALID_JSON, f"JSON parse error: {str(e)}")]

            if not errors:
                return current_response, [], iterations, run_dir
            
            # If errors exist and we have cycles left, feedback to LLM
            if iterations <= self.config.max_repair_iters:
                feedback = REPAIR_FEEDBACK_TEMPLATE.format(
                    errors_formatted=format_errors(errors),
                    version_lock=self.config.hgss_version_lock,
                    commit_lock=self.config.hgss_commit_lock
                )
                print(f"Case {case_id} iteration {iterations} failed. Repairing...")
                current_response = self.llm.generate(REPAIR_SYSTEM_PROMPT, f"Previous Output: {current_response}\n\n{feedback}")

        return current_response, errors, iterations, run_dir

    def _extract_json(self, text: str) -> str:
        # Match from first { to last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        return text.strip()
