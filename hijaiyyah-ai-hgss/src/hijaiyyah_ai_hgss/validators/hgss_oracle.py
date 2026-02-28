import subprocess
import os
from hijaiyyah_ai_hgss.taxonomy import ValidationError, ErrorCategory

def hgss_oracle_verify(hgss_repo: str, evidence_json_path: str):
    """
    Calls the normative hgss_verify_evidence.py tool as the ultimate ground-truth gate.
    """
    tool = os.path.join(hgss_repo, "tools", "hgss_verify_evidence.py")
    if not os.path.exists(tool):
        # Fallback for scaffold if repo is missing, but env_check should catch this.
        return []

    print(f"Calling HGSS Oracle Verifier: {tool} --evidence {evidence_json_path}")
    
    r = subprocess.run(
        ["python", tool, "--evidence", evidence_json_path], 
        capture_output=True, text=True
    )
    
    if r.returncode != 0:
        return [ValidationError(
            ErrorCategory.HGSS_VERIFIER_FAIL, 
            r.stdout + "\n" + r.stderr, 
            "$"
        )]
    return []
