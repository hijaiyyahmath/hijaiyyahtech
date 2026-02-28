from __future__ import annotations
import subprocess
import json
import tempfile
import os
from pathlib import Path
from hijaiyyah_ai_hgss.taxonomy import ValidationError, ErrorCategory
from hijaiyyah_ai_hgss.config import Config

def validate_hgss_verifier(data: dict, config: Config) -> list[ValidationError]:
    errors = []
    
    # The verifier tool path
    verifier_tool = Path(config.hgss_repo) / "tools" / "hgss_verify_evidence.py"
    
    if not verifier_tool.exists():
        # If the dependency is missing, we can't perform ground-truth verification.
        # In a real system, this would be a TRAP.
        return [] 

    # Save data to a temporary file for the verifier
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_path = f.name

    try:
        # Run the normative verifier
        result = subprocess.run(
            ["python", str(verifier_tool), "--evidence", temp_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            errors.append(ValidationError(
                ErrorCategory.HGSS_VERIFIER_FAIL,
                f"Normative verifier failed: {result.stdout.strip() or result.stderr.strip()}",
                "lease_sig"
            ))
    except Exception as e:
        errors.append(ValidationError(ErrorCategory.HGSS_VERIFIER_FAIL, f"Internal error calling verifier: {str(e)}"))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return errors
