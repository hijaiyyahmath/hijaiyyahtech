# src/hisavm/constants.py
from __future__ import annotations

RELEASE_ID = "HISA-VM-v1.0+local.1"
TAG = "hisa-vm-v1.0-local.1"

LANES = 18
VREGS = 16
SREGS = 16

# Opcodes
OP_LDH_V18  = 0x10
OP_AUDIT    = 0x20
OP_SETFLAG  = 0x30
OP_HALT     = 0xFF

# Flags
FLAGID_CLOSED_HINT = 0  # subop for SETFLAG

# Normative Hijaiyyah order file
HIJAIYYAH_28_PATH_DEFAULT = "data/HIJAIYYAH_28.txt"
MASTER_CSV_PATH_DEFAULT = "data/MH-28-v1.0-18D.csv"
