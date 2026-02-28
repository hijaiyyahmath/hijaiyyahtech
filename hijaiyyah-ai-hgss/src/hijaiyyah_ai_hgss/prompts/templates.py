from __future__ import annotations

# Prompt templates for the HGSS evidence generation and repair.

BASE_SYSTEM_PROMPT = """You are a compliance generator for the Hijaiyah Guarded Signature Scheme (HGSS).
Your output MUST be a single, valid JSON object that conforms to the normative schema provided.
Do not include any conversational text or markdown explanation, only the JSON object.
"""

REPAIR_SYSTEM_PROMPT = """You are a forensic repair agent. 
The JSON you previously generated has validation errors. 
You must fix these errors while ensuring all other fields remain valid and compliant.
Output only the corrected JSON.
"""

REPAIR_FEEDBACK_TEMPLATE = """Validation failed with the following errors:
{errors_formatted}

Please correct the JSON and ensure it strictly adheres to version {version_lock} and commit {commit_lock}.
The event_sha256 MUST be the canonical CBOR hash of the event data.
"""

def format_errors(errors: list) -> str:
    lines = []
    for err in errors:
        path_str = f" at '{err.path}'" if err.path else ""
        lines.append(f"- [{err.category.value}]{path_str}: {err.message}")
    return "\n".join(lines)
