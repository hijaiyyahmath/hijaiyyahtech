#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdalign.h>

#include "cmm18c_types.h"

/* Simulasi: closed berasal dari pipeline CSGI/MainPath (metadata injeksi). */
static bool closed_hint_from_csgi_mainpath(void) {
  return true; /* contoh: MainPath closed */
}

int main(void) {
  /* Normatif: v18 buffer harus 16-byte aligned */
  CMM18C_ALIGNED_V18(v18);

  /* Isi contoh (dummy). Untuk program real, v18 berasal dari master table atau hasil pipeline. */
  for (unsigned i = 0; i < CMM18C_V18_LANES; i++) v18[i] = 0;

  bool closed = closed_hint_from_csgi_mainpath();

#if defined(__CMM18C__) && defined(__clang__) && !defined(CMM18C_NO_BUILTIN_AUDIT_PTR)
  /* Builtin path: paling sesuai untuk integrasi LLVM */
  cmm18c_audit_with_closed_hint_ptr((const uint32_t (*)[CMM18C_V18_LANES])&v18, closed);

#elif defined(__CMM18C__) && defined(CMM18C_USE_INLINE_ASM)
  /* Inline asm path: untuk bring-up assembler/RTL awal */
  cmm18c_audit_with_closed_hint_ptr_asm((const uint32_t (*)[CMM18C_V18_LANES])&v18, closed);

#else
  /* Host fallback (x86) — biasanya panggil emulator VM, bukan intrinsic.
     Di repo kamu, ini bisa diganti: call into python/c emulator. */
  printf("Host build: intrinsic not executed. Use CMM18C toolchain.\n");
#endif

  /* Jika terjadi pelanggaran audit/konformansi/alignment pada target,
     CPU akan TRAP/HALT dan tidak sampai sini. */
  printf("Program finished (no trap).\n");

  /* WARNING: ini sengaja membuat misalignment test (jangan untuk produksi) */
  /*
  uint8_t *raw = (uint8_t*)v18;
  const uint32_t (*misaligned)[18] = (const uint32_t (*)[18])(raw + 4); // +4 => tidak aligned 16
  cmm18c_audit_with_closed_hint_ptr(misaligned, closed); // harus TRAP MISALIGNED_V18_PTR
  */

  return 0;
}
