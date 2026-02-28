import json
import hashlib
import rfc8785

path = 'hl-release-HL-18-v1.0/ST28_MANIFEST.json'
new_runner_hash = 'baf17ce1b6e89938bc6a9288688e9e42cc10ef25796ba9dc68c6f9ab97d9febb'

with open(path, 'r', encoding='utf-8') as f:
    man = json.load(f)

man['integrity']['verify_runner']['sha256'] = new_runner_hash

if 'manifest_sha256' in man:
    del man['manifest_sha256']

# RFC 8785 JCS Canonicalization
seal = hashlib.sha256(rfc8785.dumps(man)).hexdigest()
man['manifest_sha256'] = seal

with open(path, 'w', encoding='utf-8') as f:
    json.dump(man, f, indent=2)

print(f"New Seal: {seal}")
