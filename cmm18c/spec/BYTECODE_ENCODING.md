# Bytecode Encoding — CMM-18C v1.0 (Normatif)

Dokumen ini mengunci encoding biner instruksi CMM‑18C v1.0.
Seluruh word diserialisasi **little-endian**.

## 1) Instruction Word (IW) 32-bit

Format (MSB → LSB):
\[
[\texttt{opcode:8} \mid \texttt{Rd:4} \mid \texttt{Ra:4} \mid \texttt{Rb:4} \mid \texttt{subop:4} \mid \texttt{imm8:8}]
\]

Bit positions (normatif):
- `opcode`: bits **[31:24]**
- `Rd`    : bits **[23:20]**
- `Ra`    : bits **[19:16]**
- `Rb`    : bits **[15:12]**
- `subop` : bits **[11:8]**
- `imm8`  : bits **[7:0]**

Little-endian serialization:
- IW value `0x30000001` disimpan sebagai bytes: `01 00 00 30`.

## 2) Opcode Map (Normatif v1.0)
- `LDV`     = `0x11`
- `AUDIT`   = `0x20`
- `SETFLAG` = `0x30`
- `HALT`    = `0xFF`

## 3) Extension Words
Sebagian opcode memakai extension word 32-bit setelah IW.
Semua extension word juga serialized **little-endian**.

### 3.1 LDV extension (off32)
`LDV` selalu diikuti 1 word `off32` (u32).

## 4) Contoh Encoding (Normatif)

### 4.1 SETFLAG CLOSED_HINT,1
IW = `0x30000001`
Bytes = `01 00 00 30`

### 4.2 AUDIT V0 (Vs = Rd = 0)
IW = opcode `0x20`, `Rd=0`, field lain 0:
IW = `0x20000000`

### 4.3 AUDIT V3
IW = `0x20300000`  (karena `Rd=3` → `(3<<20)=0x00300000`)

### 4.4 LDV V0, [S0 + 0]
IW  = `0x11000000`
EXT = `0x00000000`
Byte stream (little-endian):
`00 00 00 11  00 00 00 00`

### 4.5 HALT
IW = `0xFF000000`
