# LLVM ABI POINTER (Normative)

This document dictates how an LLVM compiler (or any frontend language tool) targeting CMM-18C should interact with the compliance validation hardware.

## Intrinsic Canonical Form
```llvm
declare void @llvm.cmm18c.audit.with_closed_hint.ptr(ptr %p_v18, i1 %closed)
```

## Alignment Rule
The pointer `%p_v18` must point to a 16-byte aligned `uint32_t[18]` buffer.
- Assembly Level: `addr % 16 == 0`.
- Failure traps machine with `MISALIGNED_V18_PTR (10)`.

## Normative Lowering
Compilers generating CMM-18C `.cmm` (or ELF) must lower this intrinsic into exactly three instructions:
```asm
LDV Vt, [p_v18]
SETFLAG CLOSED_HINT, closed
AUDIT Vt
```
This guarantees the *CORE-1 Rule* (SETFLAG -> AUDIT adjacency) is statically satisfied at compile time.
