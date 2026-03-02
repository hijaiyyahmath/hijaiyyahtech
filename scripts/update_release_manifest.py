#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

def main():
    root = Path(__file__).resolve().parents[1]
    
    # Paths
    release_id_path = root / "AuditorBundle" / "RELEASE_ID.json"
    manifest_json_path = root / "web" / "apps" / "hijaiyyahmath-org" / "public" / "releases" / "auditor_bundles.json"
    dist_sha_path = root / "dist" / "SHA256SUMS.txt"
    
    if not release_id_path.exists():
        print(f"Error: {release_id_path} not found")
        sys.exit(1)
    if not manifest_json_path.exists():
        print(f"Error: {manifest_json_path} not found")
        sys.exit(1)
    if not dist_sha_path.exists():
        print(f"Error: {dist_sha_path} not found")
        sys.exit(1)
        
    # Load Release ID
    with open(release_id_path, "r", encoding="utf-8") as f:
        rel_id = json.load(f)
        
    # Load Tarball SHA256 from dist/SHA256SUMS.txt
    # Format: <hash>  <filename>
    with open(dist_sha_path, "r", encoding="utf-8") as f:
        line = f.readline()
        tar_sha = line.split()[0]
        tar_name = line.split()[1]
        
    # Build URLs (Assuming standard GitHub release pattern)
    tag = rel_id.get("release_channel", "stack-v1.0")
    base_url = f"https://github.com/hijaiyyahmath/hijaiyyahtech/releases/download/{tag}"
    
    new_entry = {
        "bundle_id": rel_id["bundle_id"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "hl18_release_id": rel_id["hl18_release_id"],
        "hisa_vm_release_id": rel_id["hisa_vm_release_id"],
        "tar_url": f"{base_url}/{tar_name}",
        "tar_sha256": tar_sha,
        "sha256sums_url": f"{base_url}/SHA256SUMS.txt",
        "docker_image": "ghcr.io/hijaiyyah/stack-auditor",
        "docker_digest": None, # Should be updated if Docker build is automated
        "github_release_url": f"https://github.com/hijaiyyahmath/hijaiyyahtech/releases/tag/{tag}"
    }
    
    # Load existing manifest
    with open(manifest_json_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    # Check if bundle_id already exists (update it) or append
    exists = False
    for i, entry in enumerate(manifest):
        if entry["bundle_id"] == new_entry["bundle_id"]:
            manifest[i] = new_entry
            exists = True
            break
    
    if not exists:
        manifest.insert(0, new_entry) # Most recent first
        
    # Save
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
        f.write("\n")
        
    print(f"Successfully updated {manifest_json_path.name} with {new_entry['bundle_id']}")

if __name__ == "__main__":
    main()
