# HISA-VM Release Sync Table

This table defines the documents that MUST contain the current Release ID to ensure forensic consistency across the repository.

**Current Release ID**: `HISA-VM-v1.0+local.1`

| File Path | Requirement |
|---|---|
| `src/hisavm/constants.py` | `RELEASE_ID = "HISA-VM-v1.0+local.1"` |
| `spec/HISA_v1_0.md` | Must contain header with Release ID |
| `spec/HISA_ISA_TABLE.md` | Must contain header with Release ID |
| `spec/HISA_BYTECODE_ENCODING.md` | Must contain header with Release ID |
| `spec/HISA_TRAP_CONFORMANCE.md` | Must contain header with Release ID |
| `specs/HISA_release_integrity_local.yaml` | `release_id: "HISA-VM-v1.0+local.1"` |
| `RELEASE_SYNC_TABLE.md` | Must contain self-reference to Release ID |

## CI Verification
Use the following command to verify the lock:
```powershell
python tools/check_release_lock.py --expected HISA-VM-v1.0+local.1
```
