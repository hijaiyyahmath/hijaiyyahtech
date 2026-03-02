; Canonical LLVM IR example for CMM-18C Intrinsic
; Target: cmm18c-unknown-unknown

declare void @llvm.cmm18c.audit.with_closed_hint.ptr(ptr %p_v18, i1 %closed)

define void @process_v18(ptr %buf) {
entry:
  ; Canonical pointer-based audit
  call void @llvm.cmm18c.audit.with_closed_hint.ptr(ptr %buf, i1 1)
  ret void
}

; NORMATIVE LOWERING expected:
; LDV      v0, [%buf + 0]
; SETFLAG  closed_hint, 1
; AUDIT    v0
