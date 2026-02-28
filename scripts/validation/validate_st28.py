#!/usr/bin/env python3
"""
SPEC v0.1 validator for ST-28-v0.1.json
Checks:
  1. JIM gate: ج must have exactly 1 vortex (JIM_VORTEX(Q3))
  2. Non-JIM gate: all non-ج letters must have vortex_count == 0
  3. Injective tags: all 28 tag36_hex values must be unique
  4. Letter count: must be exactly 28
  5. SEG rule: each letter must start with SEG_K or SEG_Q
  6. All audits pass
"""
import json, sys

def fail(msg):
    raise SystemExit("FAIL: " + msg)

path = "hl-release-HL-18-v1.0/ST-28-v0.1.json"
doc = json.load(open(path, "r", encoding="utf-8"))
letters = doc["letters"]

# 0) letter count
if len(letters) != 28:
    fail(f"Expected 28 letters, got {len(letters)}")

# 1) JIM gate: ج must have exactly 1 vortex
j = next((x for x in letters if x["letter"] == "ج"), None)
if j is None:
    fail("ج not found in letters")
if j["JIM_VORTEX_count"] != 1:
    fail(f"JIM gate failed: ج JIM_VORTEX_count={j['JIM_VORTEX_count']} expected 1")
# Verify JIM_VORTEX(Q3) appears exactly once in trace_rle
# Fix: sum(n) not sum(1)
jim_count = sum(n for tok, n in j["trace_rle"] if tok == "JIM_VORTEX(Q3)")
if jim_count != 1:
    fail(f"JIM gate: ج has {jim_count} JIM_VORTEX(Q3) in trace_rle, expected 1")

# 2) Non-JIM must have 0 JIM_VORTEX_count
bad = [x["letter"] for x in letters if x["letter"] != "ج" and x["JIM_VORTEX_count"] != 0]
if bad:
    fail(f"Non-JIM has vortex_count!=0: {bad}")

# 2b) Check SPEC metadata
spec = doc.get("spec", {})
if spec.get("name") != "HC18DC v0.1 (Strict)":
    fail(f"Spec name mismatch: {spec.get('name')}")
lock = spec.get("shape_lock", {})
if lock.get("resample_step_px") != 3.0:
    fail(f"Resample step mismatch: {lock.get('resample_step_px')}")
if lock.get("nuqtah_coupling") != "Fix A (axis 14 rotation for NT/NF/NM)":
    fail("Fix A coupling missing in metadata")

# 3) Injective tags
tags = [x["tag36_hex"] for x in letters]
if len(set(tags)) != 28:
    dups = [t for t in tags if tags.count(t) > 1]
    fail(f"tag36 not injective on 28 letters, duplicates: {set(dups)}")

# 4) SEG rule: each trace must start with SEG_K or SEG_Q
for x in letters:
    if not x["trace_rle"]:
        fail(f"{x['letter']}: empty trace_rle")
    first_tok = x["trace_rle"][0][0]
    if first_tok not in ("SEG_K", "SEG_Q"):
        fail(f"{x['letter']}: trace starts with {first_tok}, expected SEG_K or SEG_Q")
    # Check SEG_Q rule: if SEG_Q, must have TURN tokens; if SEG_K, must not
    has_turn = any(t.startswith("TURN") or t == "JIM_VORTEX(Q3)" for t, _ in x["trace_rle"])
    if first_tok == "SEG_Q" and not has_turn:
        fail(f"{x['letter']}: SEG_Q but no TURN tokens found")
    if first_tok == "SEG_K" and has_turn:
        fail(f"{x['letter']}: SEG_K but TURN tokens found")

# 5) All audits pass
bad_audit = [x["letter"] for x in letters if not x["audit"]["ok"]]
if bad_audit:
    fail(f"Audit failed for: {bad_audit}")

print("PASS: SPEC v0.1 core gates ok")
print(f"  28 letters, all audit ok")
print(f"  JIM gate: ج JIM_VORTEX_count=1, JIM_VORTEX(Q3) ×1")
print(f"  Non-JIM: 0 JIM_VORTEX_count for all 27 others")
print(f"  28 unique tag36 hashes (injective)")
print(f"  SEG_K/SEG_Q rule compliant")
print(f"  SPEC metadata lock verified: {spec.get('name')}")
