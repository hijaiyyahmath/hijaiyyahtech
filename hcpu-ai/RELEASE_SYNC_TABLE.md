# HCPU-AI Release Sync Table

This table track the normative synchronization of the Release ID across the HCPU-AI module.

| File | Status | Expected String |
| :--- | :--- | :--- |
| `src/hcpu_ai/constants.py` | [x] | `RELEASE_ID = "HCPU-AI-v1.0+local.1"` |
| `spec/HCPU_AI_v1_0.md` | [x] | Header with Release ID |
| `spec/HCPU_AI_MODES.md` | [x] | Part of context |
| `spec/HCPU_AI_RELEASE_LOCK.md` | [x] | Lock definition |
| `specs/HCPU_AI_release_integrity_local.yaml` | [x] | `id: HCPU-AI-v1.0+local.1` |

## Verification
Run the following tool to ensure synchronization:
```powershell
python tools/check_release_lock.py
```
