"""
hcpu.py — HCPU Pure Stack VM Engine

Fetch-decode-execute cycle for HVM IR instructions.
Supports three conformance modes: CORE, FEEDBACK, OWNER.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from hijaiyahlang.core import audit_v18, add18, mod18, Vector, AuditResult
from hijaiyahlang.dataset import Dataset18
from hijaiyahlang.ir import IRInst, Op, NORMATIVE_OPS


class ConformanceMode(Enum):
    CORE     = auto()  # normative only: LOAD, ADD, AUDIT, MOD, HALT
    FEEDBACK = auto()  # + VALIDATE (side-effect)
    OWNER    = auto()  # + VALIDATE + LEARN (side-effect)


class NonNormativeError(RuntimeError):
    """Raised when a non-normative opcode is used in CORE mode."""
    pass


class HCPUError(RuntimeError):
    """General HCPU execution error."""
    pass


@dataclass
class TraceEntry:
    pc: int
    op: Op
    arg: Any
    stack_top: Optional[List[int]]
    event: Optional[str] = None


@dataclass
class ExecResult:
    ok: bool
    result: Optional[Vector] = None
    audit: Optional[AuditResult] = None
    trace: List[TraceEntry] = field(default_factory=list)
    steps: int = 0
    error: Optional[str] = None
    feedback_log: List[Any] = field(default_factory=list)


class HCPU:
    """Pure Stack VM for HijaiyahLang IR execution."""

    MAX_STEPS = 10_000

    def __init__(self, ds: Dataset18, *,
                 mode: ConformanceMode = ConformanceMode.CORE,
                 validator_loop: Any = None,
                 owner_model: Any = None):
        self.ds = ds
        self.mode = mode
        self.validator_loop = validator_loop
        self.owner_model = owner_model

        self._program: List[IRInst] = []
        self._stack: List[Vector] = []
        self._word_stack: List[str] = []  # for LEARN
        self._pc: int = 0
        self._halted: bool = False
        self._trace: List[TraceEntry] = []
        self._last_audit: Optional[AuditResult] = None
        self._feedback_log: List[Any] = []
        self._steps: int = 0

    def load(self, program: List[IRInst]) -> None:
        """Load IR program into instruction memory."""
        self._program = list(program)
        self._stack = []
        self._word_stack = []
        self._pc = 0
        self._halted = False
        self._trace = []
        self._last_audit = None
        self._feedback_log = []
        self._steps = 0

    def _check_mode(self, op: Op) -> None:
        """Enforce conformance mode restrictions."""
        if op not in NORMATIVE_OPS:
            if self.mode == ConformanceMode.CORE:
                raise NonNormativeError(
                    f"Opcode {op.name} rejected in CORE mode")
            if op == Op.LEARN and self.mode == ConformanceMode.FEEDBACK:
                raise NonNormativeError(
                    f"Opcode LEARN rejected in FEEDBACK mode "
                    f"(requires OWNER mode)")

    def _stack_top(self) -> Optional[List[int]]:
        return list(self._stack[-1]) if self._stack else None

    def step(self) -> TraceEntry:
        """Execute one instruction. Returns trace entry."""
        if self._halted:
            raise HCPUError("HCPU already halted")
        if self._pc >= len(self._program):
            raise HCPUError("PC past end of program (missing HALT?)")
        if self._steps >= self.MAX_STEPS:
            raise HCPUError(f"Step limit ({self.MAX_STEPS}) exceeded")

        inst = self._program[self._pc]
        self._check_mode(inst.op)

        event = None

        if inst.op == Op.LOAD:
            letter = inst.arg
            if letter not in self.ds.table:
                raise HCPUError(f"LOAD: letter {letter!r} not in dataset")
            v = list(self.ds.table[letter])
            self._stack.append(v)
            self._word_stack.append(letter)

        elif inst.op == Op.ADD:
            if len(self._stack) < 2:
                raise HCPUError("ADD: stack underflow (need 2 operands)")
            b = self._stack.pop()
            a = self._stack.pop()
            self._stack.append(add18(a, b))

        elif inst.op == Op.AUDIT:
            if len(self._stack) < 1:
                raise HCPUError("AUDIT: stack underflow")
            v = self._stack[-1]  # NON-DESTRUCTIVE: peek, don't pop
            ar = audit_v18(v)
            self._last_audit = ar
            if not ar.ok:
                event = f"AUDIT FAIL: {ar.checks}"
                raise HCPUError(f"AUDIT FAIL: {ar.checks}")
            event = "AUDIT PASS"

        elif inst.op == Op.MOD:
            if len(self._stack) < 1:
                raise HCPUError("MOD: stack underflow")
            v = self._stack.pop()
            self._stack.append(mod18(v, inst.arg))

        elif inst.op == Op.HALT:
            self._halted = True
            event = "HALT"

        elif inst.op == Op.VALIDATE:
            # Side-effect only: stack unchanged
            if len(self._stack) < 1:
                raise HCPUError("VALIDATE: stack underflow")
            v = self._stack[-1]  # peek
            if self.validator_loop is not None:
                fb = self.validator_loop.validate(v)
                self._feedback_log.append(fb)
                event = f"VALIDATE: {fb}"
            else:
                event = "VALIDATE: no validator attached"

        elif inst.op == Op.LEARN:
            # Side-effect only: stack unchanged
            word = "".join(self._word_stack)
            if self.owner_model is not None:
                self.owner_model.observe(word)
                event = f"LEARN: observed '{word}'"
            else:
                event = "LEARN: no owner model attached"

        entry = TraceEntry(
            pc=self._pc,
            op=inst.op,
            arg=inst.arg,
            stack_top=self._stack_top(),
            event=event,
        )
        self._trace.append(entry)
        self._pc += 1
        self._steps += 1
        return entry

    def run(self) -> ExecResult:
        """Execute program until HALT or error."""
        try:
            while not self._halted:
                self.step()
        except (HCPUError, NonNormativeError) as e:
            return ExecResult(
                ok=False,
                result=self._stack_top(),
                audit=self._last_audit,
                trace=list(self._trace),
                steps=self._steps,
                error=str(e),
                feedback_log=list(self._feedback_log),
            )
        return ExecResult(
            ok=True,
            result=self._stack_top(),
            audit=self._last_audit,
            trace=list(self._trace),
            steps=self._steps,
            feedback_log=list(self._feedback_log),
        )

    def trace(self) -> List[TraceEntry]:
        return list(self._trace)
