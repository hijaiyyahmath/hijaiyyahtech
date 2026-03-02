# OPS Runbook — Hijaiyyah-AI

## 1. Local Development
Run a single guarded case for debugging:
```bash
python tools/run_guarded_once.py --task-id ev_min_001
```

## 2. A/B Testing
Run the full benchmark suite:
```bash
python tools/run_ab_test.py --dataset datasets/tasks/hgss_evidence_cases.jsonl --out reports/ab_report.json
```

## 3. Requirements
- Python >= 3.10
- Valid LLM API Key in `.env`
- Vendored `hgss-hc18dc` dependency in `deps/`

## 4. Maintenance
- **Update Locks**: If the normative HGSS release changes, update `spec/RELEASE_IDENTITY.md` and `src/hijaiyyah_ai_hgss/config.py`.
- **Expand Taxonomy**: Add new error types as the underlying validator evolves.
