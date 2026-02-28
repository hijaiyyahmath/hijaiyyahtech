import os
import json
import shutil
from pathlib import Path

def sync():
    # Source path relative to script
    src_root = Path(__file__).parent.parent.parent.parent.parent
    hgss_artifacts = src_root / "hgss-hc18dc" / "artifacts"
    
    # Destination path
    dest_public = Path(__file__).parent.parent / "public" / "downloads" / "hgss"
    dest_public.mkdir(parents=True, exist_ok=True)
    
    evidence_src = hgss_artifacts / "event_single.json"
    if not evidence_src.exists():
        print(f" [!] Source evidence not found: {evidence_src}")
        return

    # 1. Copy evidence.json
    shutil.copy2(evidence_src, dest_public / "evidence.json")
    print(f" [OK] Synced evidence.json")

    # 2. Extract event_sha256 from evidence.json to create expected.json
    with open(evidence_src, "r") as f:
        data = json.load(f)
        event_sha256 = data.get("event_sha256", "")
    
    expected_data = {
        "expected_event_sha256": event_sha256
    }
    with open(dest_public / "evidence.expected.json", "w") as f:
        json.dump(expected_data, f, indent=2)
    print(f" [OK] Generated evidence.expected.json")

    # 3. Create dummy sha256.txt for the file itself (optional)
    with open(dest_public / "evidence.sha256.txt", "w") as f:
        f.write(f"{event_sha256}  evidence.json\n")
    print(f" [OK] Generated evidence.sha256.txt")

if __name__ == "__main__":
    sync()
