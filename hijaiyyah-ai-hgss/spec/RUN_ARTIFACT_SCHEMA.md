# RUN ARTIFACT SCHEMA — Hijaiyyah-AI HGSS VM v1.0

Status: NORMATIVE

## 1. Layout
Each run MUST create:

`artifacts/runs/<run_id>/`

Each case MUST create:

`artifacts/runs/<run_id>/case_<case_id>/`

## 2. Required Per-Case Files (Always-Save)
The following files MUST exist:

- `baseline_raw.txt` — baseline LLM output (raw)
- `baseline_event_raw.json` — parsed baseline JSON (if parsable)
- `guarded_iter_0_raw.txt`, `guarded_iter_1_raw.txt`, ... — guarded iterations
- `ct.bin` — deterministic ciphertext bytes (harness)
- `trace.jsonl` — deterministic trace
- `lease_input.json` — normalized lease payload
- `lease_token.bin` — lease token bytes for lease_token_sha256
- `event_single.json` — final evidence event after autofill
- `auditlog.jsonl` — single-line JSONL containing final event

## 3. Run Manifest
Each run MUST create:

`artifacts/runs/<run_id>/manifest.json`

Manifest MUST contain per-case status summary:
- baseline ok_raw_at_1, err_top
- guarded ok_raw_at_1, ok_final_at_k, repair_steps, err_top

## 4. Oracle Conformance
Final `event_single.json` MUST conform to:

`deps/hgss-hc18dc/spec/AUDIT_EVIDENCE_SCHEMA.md`

and MUST pass:

`python deps/hgss-hc18dc/tools/hgss_verify_evidence.py --evidence event_single.json`
