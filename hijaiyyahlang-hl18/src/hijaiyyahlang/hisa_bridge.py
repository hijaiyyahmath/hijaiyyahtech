from __future__ import annotations
import subprocess, re
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
    lines = []
    for i, lid in enumerate(NORMATIVE_28):
        v = word_v18 if i == 0 else ds.require(lid)
        lines.append(lid + "," + ",".join(str(x) for x in v))
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
        cp_asm = subprocess.run(asm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if cp_asm.returncode != 0 or not binp.exists():
            raise ConformanceError(
                "HISA-ASM failed\n"
                f"cmd={asm_cmd}\n"
                f"stdout={cp_asm.stdout.decode('utf-8','replace')}\n"
                f"stderr={cp_asm.stderr.decode('utf-8','replace')}"
            )

        run_cmd = list(self.cfg.run_cmd) + ["--program", str(binp), "--master", str(master_csv)]
        cp_run = subprocess.run(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
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
        return self._parse_text(text)

    def _parse_text(self, text: str) -> HisaAuditResult:
        status = None
        regs: Dict[str, int] = {}
        trap_code = None
        trap_name = None
        trap_full = None
        audit_res = None

        for line in text.splitlines():
            m = _STATUS_RE.match(line)
            if m:
                status = m.group("status")
                continue
            m = _REGS_RE.match(line)
            if m:
                regs = _parse_regs_kv(m.group("regs"))
                continue
            m = _TRAP_RE.match(line)
            if m:
                trap_code = int(m.group("code"))
                trap_name = m.group("name")
                trap_full = f"TRAP({trap_code}) {trap_name}"
                continue
            m = _AUDIT_RE.match(line)
            if m:
                audit_res = m.group("res")
                continue

        if status is None:
            raise ConformanceError("HISA-VM output missing 'Status:'")

        if status == "HALT_SUCCESS":
            ok = True
        elif status == "TRAP_TRIGGERED":
            ok = False
        else:
            raise ConformanceError(f"Unknown HISA-VM Status: {status!r}")

        err = regs.get("ERR", 0)
        if ok and (err != 0 or trap_full is not None):
            raise ConformanceError("Inconsistent PASS: HALT_SUCCESS but ERR/TRAP present")
        if (not ok) and trap_full is None:
            raise ConformanceError("Inconsistent TRAP: TRAP_TRIGGERED but Trap Code missing")

        return HisaAuditResult(
            ok=ok,
            status=status,
            trap=trap_full,
            trap_code=trap_code,
            trap_name=trap_name,
            registers=regs,
            details={"raw": text, "audit_result_line": audit_res},
        )
