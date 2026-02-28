import json
from dataclasses import dataclass, asdict
from typing import Any, List, Optional

@dataclass
class TraceEntry:
    pc: int
    op: str
    regs_v: List[List[int]]
    regs_r: List[int]
    event: Optional[str] = None

class Tracer:
    def __init__(self):
        self.entries: List[TraceEntry] = []

    def record(self, pc: int, op: str, regs_v: List[List[int]], regs_r: List[int], event: Optional[str] = None):
        self.entries.append(TraceEntry(pc, op, regs_v, regs_r, event))

    def save_jsonl(self, path: str):
        with open(path, "w") as f:
            for e in self.entries:
                f.write(json.dumps(asdict(e)) + "\n")
