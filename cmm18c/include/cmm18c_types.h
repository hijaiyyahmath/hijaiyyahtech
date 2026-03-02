#ifndef CMM18C_TYPES_H
#define CMM18C_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stdalign.h>

#ifdef __cplusplus
extern "C" {
#endif

/* =========================
 *  CMM-18C v1.0 Constants
 * ========================= */

#define CMM18C_V18_LANES        18u
#define CMM18C_LANE_WIDTH_BITS  32u
#define CMM18C_V18_BYTES        (CMM18C_V18_LANES * 4u)  /* 72 bytes */
#define CMM18C_V18_ALIGN        16u                      /* NORMATIVE alignment */

/* Lane indices (HL-18 order, normative) */
enum cmm18c_lane_index {
  CMM18C_L_HAT_THETA = 0,

  CMM18C_L_NT = 1,
  CMM18C_L_NF = 2,
  CMM18C_L_NM = 3,

  CMM18C_L_KM = 4,
  CMM18C_L_KT = 5,
  CMM18C_L_KD = 6,
  CMM18C_L_KA = 7,
  CMM18C_L_KZ = 8,

  CMM18C_L_QA = 9,
  CMM18C_L_QT = 10,
  CMM18C_L_QD = 11,
  CMM18C_L_QS = 12,
  CMM18C_L_QZ = 13,

  CMM18C_L_AN = 14,
  CMM18C_L_AK = 15,
  CMM18C_L_AQ = 16,

  CMM18C_L_EPS = 17
};

/* v18 in memory is an array of 18 x i32 (little-endian at byte level). */
typedef uint32_t cmm18c_v18_t[CMM18C_V18_LANES];

/* Helper macro for declaring aligned v18 buffers */
#define CMM18C_ALIGNED_V18(name) alignas(CMM18C_V18_ALIGN) uint32_t name[CMM18C_V18_LANES]

/* =========================
 *  Trap/Error codes (subset)
 * ========================= */
enum cmm18c_trap_cause {
  CMM18C_TRAP_NONE                       = 0,
  CMM18C_TRAP_ILLEGAL_OPCODE             = 1,
  CMM18C_TRAP_ILLEGAL_ENCODING           = 2,
  CMM18C_TRAP_ILLEGAL_REG                = 3,
  CMM18C_TRAP_ILLEGAL_FLAG               = 4,
  CMM18C_TRAP_CONFORMANCE_SETFLAG_REQ    = 5,
  CMM18C_TRAP_AUDIT_DERIVED_MISMATCH     = 6,
  CMM18C_TRAP_AUDIT_RHO_NEGATIVE         = 7,
  CMM18C_TRAP_AUDIT_MOD4                 = 8,
  CMM18C_TRAP_AUDIT_EPS_RANGE            = 9,
  CMM18C_TRAP_MISALIGNED_V18_PTR         = 10
};

/* =========================
 *  Intrinsic API (pointer ABI)
 * =========================
 * Canonical operation:
 *   audit.with_closed_hint.ptr(ptr p_v18, i1 closed)
 *
 * Semantics (normative lowering on CMM-18C target):
 *   LDV  Vt, [p_v18]
 *   SETFLAG CLOSED_HINT, closed
 *   AUDIT Vt
 *
 * Alignment rule (normative):
 *   p_v18 must be 16-byte aligned, else TRAP MISALIGNED_V18_PTR.
 */

/* Option A: builtin (recommended for LLVM integration)
 * Requires: Clang/LLVM provides this builtin for target cmm18c.
 */
#if defined(__clang__) && defined(__CMM18C__)
  #if __has_builtin(__builtin_cmm18c_audit_with_closed_hint_ptr)
    static inline __attribute__((always_inline))
    void cmm18c_audit_with_closed_hint_ptr(const uint32_t (*p_v18)[CMM18C_V18_LANES], bool closed) {
      __builtin_cmm18c_audit_with_closed_hint_ptr(p_v18, closed);
    }
  #else
    /* If builtin is not available yet, you can enable inline-asm path below. */
    #define CMM18C_NO_BUILTIN_AUDIT_PTR 1
  #endif
#endif

/* Option B: inline asm fallback (for early bring-up)
 * This requires your assembler to understand mnemonics: LDV, SETFLAG, AUDIT.
 * If not available, keep this disabled and rely on builtin integration.
 */
#if defined(__CMM18C__) && defined(CMM18C_USE_INLINE_ASM)
static inline __attribute__((always_inline))
void cmm18c_audit_with_closed_hint_ptr_asm(const uint32_t (*p_v18)[CMM18C_V18_LANES], bool closed) {
  /* NOTE:
   * - This is target-asm and assumes:
   *   - scalar reg s0 holds pointer
   *   - vector reg v0 is temp
   * - Exact asm syntax may be adjusted to your assembler.
   */
  __asm__ volatile(
    "mov.s s0, %0        \n"
    "ldv   v0, [s0+0]    \n"
    "setflag closed_hint, %1 \n"
    "audit v0            \n"
    :
    : "r"(p_v18), "r"(closed ? 1 : 0)
    : "s0", "v0", "memory"
  );
}
#endif

#ifdef __cplusplus
} /* extern "C" */
#endif

/* Compile-time sanity checks */
_Static_assert(CMM18C_V18_BYTES == 72u, "v18 size must be 72 bytes");
_Static_assert(sizeof(cmm18c_v18_t) == 72u, "cmm18c_v18_t must be 72 bytes");

#endif /* CMM18C_TYPES_H */
