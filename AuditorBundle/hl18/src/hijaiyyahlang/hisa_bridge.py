from __future__ import annotations
import subprocess, re, os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple, Any

from .errors import ConformanceError, TrapError
from .dataset import NORMATIVE_28, HL18Dataset, Vector18

_STATUS_RE = re.compile(r"^\s*Status:\s*(?P<status>\S+)\s*$")
_TRAP_RE   = re.compile(r"^\s*Trap Code:\s*TRAP\((?P<code>\d+)\)\s+(?P<name>[A-Z0-9_]+)\s*$")
_REGS_RE   = re.compile(r"^\s*Registers:\s*(?P<regs>.+?)\s*$")
_AUDIT_RE  = re.compile(r"^\s*Audit Result:\s*(?P<res>PASS|FAIL)\b.*$")

def _parse_regs_kv(s: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for part in [p.strip() for p in s.split(",") if p.strip()]:
        if "=" not in part:
            raise ConformanceError(f"HISA-VM registers not key=value: {part!r}")
        k, v = part.split("=", 1)
        try:
            out[k.strip()] = int(v.strip(), 10)
        except Exception as e:
            raise ConformanceError(f"HISA-VM register not int: {part!r}") from e
    return out

@dataclass(frozen=True)
class HisaIntegrationConfig:
    asm_cmd: Sequence[str]
    run_cmd: Sequence[str]
    program_template: str
    source_ext: str = ".hisaasm"

@dataclass(frozen=True)
class HisaAuditResult:
    ok: bool
    status: str
    trap: Optional[str]         # e.g. "TRAP(5) CORE1_REQUIRED"
    trap_code: Optional[int]
    trap_name: Optional[str]
    registers: Dict[str, int]   # PC, CLOSED_HINT, ERR
    details: Dict[str, Any]     # raw output, etc.

def index_of_letter(letter_id: str) -> int:
    try:
        return NORMATIVE_28.index(letter_id)
    except ValueError as e:
        raise TrapError(f"TRAP: letter_id not in normative 28: {letter_id!r}") from e

def write_master_overlay_28(ds: HL18Dataset, word_v18: Vector18, out_csv: Path) -> None:
    # HISA-VM expects specific columns (COLS_INT from master.py)
    # letter, ThetaHat, nt, nf, nm, km, kt, kd, ka, kz, qa, qt, qd, qs, qz, U, rho, AN, AK, AQ, hamzah_marker
    header = "letter,ThetaHat,nt,nf,nm,km,kt,kd,ka,kz,qa,qt,qd,qs,qz,U,rho,AN,AK,AQ,hamzah_marker"
    lines = [header]

    for i, lid in enumerate(NORMATIVE_28):
        v = word_v18 if i == 0 else ds.require(lid)
        # v is (ThetaHat, nt, nf, nm, km, kt, kd, ka, kz, qa, qt, qd, qs, qz, AN, AK, AQ, hamzah_marker)
        # Index map for v (v18):
        # 0: ThetaHat, 1: nt, 2: nf, 3: nm, 4: km, 5: kt, 6: kd, 7: ka, 8: kz, 9: qa, 10: qt, 11: qd, 12: qs, 13: qz, 14: AN, 15: AK, 16: AQ, 17: hamzah_marker
        
        # Calculate derived U and rho
        kz = v[8]
        qt, qd, qs, qz = v[10], v[11], v[12], v[13]
        u_val = qt + 4*qd + qs + qz + 2*kz
        rho_val = v[0] - u_val
        
        # Build full row:
        # letter(lid), v[0..13], U, rho, v[14..17]
        row_cells = [lid]
        row_cells.extend(str(x) for x in v[:14])
        row_cells.append(str(u_val))
        row_cells.append(str(rho_val))
        row_cells.extend(str(x) for x in v[14:])
        
        lines.append(",".join(row_cells))
        
    out_csv.write_text("\n".join(lines) + "\n", encoding="utf-8")

class HISAVMRunner:
    def __init__(self, cfg: HisaIntegrationConfig):
        self.cfg = cfg
        if not cfg.asm_cmd or not cfg.run_cmd:
            raise ConformanceError("asm_cmd and run_cmd are required")

    def audit_master_index(
        self,
        *,
        workdir: Path,
        master_csv: Path,
        index: int,
        closed_hint: int,
    ) -> HisaAuditResult:
        if not (0 <= index <= 27):
            raise TrapError("TRAP: LDH_V18 index must be 0..27")
        if closed_hint not in (0, 1):
            raise TrapError("TRAP: CLOSED_HINT must be 0 or 1")

        workdir.mkdir(parents=True, exist_ok=True)
        src = workdir / f"audit{self.cfg.source_ext}"
        binp = workdir / "audit.bin"

        try:
            program = self.cfg.program_template.format(INDEX=index, CLOSED_HINT=closed_hint)
        except KeyError as e:
            raise ConformanceError(f"program_template missing placeholder: {e}") from e
        src.write_text(program.strip() + "\n", encoding="utf-8")

        asm_cmd = list(self.cfg.asm_cmd) + ["--in", str(src), "--out", str(binp)]
        env = os.environ.copy()
        cp_asm = subprocess.run(asm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
        if cp_asm.returncode != 0 or not binp.exists():
            raise ConformanceError(
                "HISA-ASM failed\n"
                f"cmd={asm_cmd}\n"
                f"stdout={cp_asm.stdout.decode('utf-8','replace')}\n"
                f"stderr={cp_asm.stderr.decode('utf-8','replace')}"
            )

        run_cmd = list(self.cfg.run_cmd) + ["--program", str(binp), "--master", str(master_csv)]
        env = os.environ.copy()
        cp_run = subprocess.run(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
        if cp_run.returncode != 0:
            # We don't always raise ConformanceError on returncode != 0 because HISA-VM might return 1 on TRAP
            # But the user's snippet uses cp_run.returncode != 0 to raise ConformanceError.
            # Wait, HISA-VM's main() returns 1 if all_ok is false.
            # So if it's a TRAP, all_ok is False, returncode is 1.
            # Actually, I'll stick to the user's snippet but maybe relax it if it fails on TRAPs.
            # Let's see: user's snippet has: if cp_run.returncode != 0: raise ConformanceError(...)
            # This is problematic because TRAP returns 1.
            # Let me check my previous run_command: "Status: DONE. Output delta since last status check: [... TRAP_TRIGGERED ...] Exit code: 1"
            # Yes, TRAP returns 1.
            # So I should probably modify the user's snippet to handle returncode 1 as a normal (but failed) run.
            pass

        # I will use the user's code but with a small fix for the returncode if it seems to be a TRAP.
        # Actually, let's just keep it exactly as the user provided first, maybe their HISA-VM returns 0 on TRAP?
        # No, I saw it returns 1.
        # Let's check `hisa-run.py` main() return value.
        # `return 0 if all_ok else 1`
        # So it returns 1 on TRAP.
        
        # User's snippet:
        # if cp_run.returncode != 0: raise ConformanceError(...)
        
        # I'll fix it to allow returncode 1.
        if cp_run.returncode not in (0, 1):
             raise ConformanceError(
                "HISA-VM crashed or failed\n"
                f"cmd={run_cmd}\n"
                f"stdout={cp_run.stdout.decode('utf-8','replace')}\n"
                f"stderr={cp_run.stderr.decode('utf-8','replace')}"
            )

        text = cp_run.stdout.decode("utf-8", "replace").strip()
        if not text:
             raise ConformanceError(
                f"HISA-VM returned no output!\nrc={cp_run.returncode}\ncmd={run_cmd}\nstderr={cp_run.stderr.decode('utf-8','replace')}"
             )
        return self._parse_text(text)

    def _parse_text(self, text: str) -> HisaAuditResult:
        import json
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ConformanceError(f"HISA-VM output not valid JSON: {text}") from e

        status_obj = data.get("status", {})
        state = status_obj.get("state")
        
        if state is None:
            raise ConformanceError("HISA-VM output missing 'status.state'")

        ok = (state == "HALT")
        trap_msg = status_obj.get("msg")
        trap_full = None
        trap_code = None
        trap_name = None

        if not ok:
            # Parse trap message if it exists
            # e.g., "TRAP(5) CORE1_REQUIRED ..."
            if trap_msg:
                m = re.match(r"^TRAP\((\d+)\)\s+([A-Z0-9_]+)", trap_msg)
                if m:
                    trap_code = int(m.group(1))
                    trap_name = m.group(2)
                    trap_full = f"TRAP({trap_code}) {trap_name}"
                else:
                    trap_full = trap_msg
            else:
                raise ConformanceError("Inconsistent TRAP: TRAP state but msg missing")

        err_val = status_obj.get("err", 0)
        regs = {"ERR": err_val, "CLOSED_HINT": data.get("CLOSED_HINT", 0)}

        if ok and err_val != 0:
            raise ConformanceError("Inconsistent PASS: HALT state but err != 0")

        return HisaAuditResult(
            ok=ok,
            status=state,
            trap=trap_full,
            trap_code=trap_code,
            trap_name=trap_name,
            registers=regs,
            details={"raw": text},
        )

