from __future__ import annotations

import hashlib
import hmac
import json
import struct
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from hgss.crypto.key_provider import KeyProvider, KeyRef
from hgss.nonce.lease_token import verify_lease_token_es256, LeaseTokenVerified
from hgss.nonce.lease_policy import LeasePolicy


# ---------------------------
# Normative dataset locks (final)
# ---------------------------
MH28_SHA256_HEX = "7393659dfe979cf85b1cf6293179f7ba1f49b4eedd1af19f002170148ce00380"
CSGI28_SHA256_HEX = "530845fbc3815ea9f02c75d44bda0e1aa096ec93729942d24d2d8bb0bd56c9d5"
MH28_SHA256 = bytes.fromhex(MH28_SHA256_HEX)
CSGI28_SHA256 = bytes.fromhex(CSGI28_SHA256_HEX)

# Normative Hijaiyyah order (index -> letter_id)
HIJAIYYAH_28 = [
    "ا","ب","ت","ث","ج","ح","خ","د","ذ","ر","ز","س","ش","ص","ض","ط","ظ",
    "ع","غ","ف","ق","ك","ل","م","ن","و","ه","ي"
]

LANES = 18


# ---------------------------
# Trap codes (HCVM)
# ---------------------------
E_ILLEGAL_OPCODE = 1
E_ILLEGAL_ENCODING = 2
E_CONFORMANCE_SETFLAG_REQUIRED = 5
E_AUDIT_DERIVED_MISMATCH = 6
E_AUDIT_RHO_NEGATIVE = 7
E_AUDIT_MOD4 = 8
E_AUDIT_EPS_RANGE = 9

E_LEASE_EXHAUSTED = 21
E_LEASE_PREFIX_MISMATCH = 22
E_LEASE_SIGNATURE_INVALID = 23
E_DATASET_LOCK_FAIL = 24
E_CRYPTO_FAIL = 25


class Trap(Exception):
    def __init__(self, err: int, msg: str = ""):
        super().__init__(f"TRAP({err}) {msg}")
        self.err = err


def _u32(x: int) -> int:
    return x & 0xFFFFFFFF


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _hmac_sha256(key: bytes, msg: bytes) -> bytes:
    return hmac.new(key, msg, hashlib.sha256).digest()


def decode_iw(word: int) -> Tuple[int,int,int,int,int,int]:
    opcode = (word >> 24) & 0xFF
    rd = (word >> 20) & 0xF
    ra = (word >> 16) & 0xF
    rb = (word >> 12) & 0xF
    subop = (word >> 8) & 0xF
    imm8 = word & 0xFF
    return opcode, rd, ra, rb, subop, imm8


def fetch_u32_le(code: bytes, pc: int) -> int:
    if pc + 4 > len(code):
        raise Trap(E_ILLEGAL_ENCODING, "CODE_OOB")
    return struct.unpack_from("<I", code, pc)[0]


@dataclass
class LeaseEvidence:
    lease_id: str
    key_id: bytes
    node_id: bytes
    prefix32: int
    start_ctr: int
    end_ctr: int
    cur_ctr: int
    token: Optional[bytes] = None  # COSE_Sign1 token

    @staticmethod
    def from_json(path: str) -> "LeaseEvidence":
        obj = json.loads(open(path, "r", encoding="utf-8").read())
        # key_id/node_id in hex for determinism
        key_id = bytes.fromhex(obj["key_id_hex"])
        node_id = bytes.fromhex(obj["node_id_hex"])
        return LeaseEvidence(
            lease_id=str(obj["lease_id"]),
            key_id=key_id,
            node_id=node_id,
            prefix32=int(obj["prefix32"]),
            start_ctr=int(obj["start_ctr"]),
            end_ctr=int(obj["end_ctr"]),
            cur_ctr=int(obj.get("cur_ctr", obj["start_ctr"])),
            token=bytes.fromhex(obj["token_hex"]) if "token_hex" in obj else None
        )


class Memory:
    """
    Simple byte-addressable memory with little-endian helpers.
    """
    def __init__(self, size: int = 1<<20):
        self.mem = bytearray(size)

    def write(self, addr: int, data: bytes):
        if addr < 0 or addr + len(data) > len(self.mem):
            raise Trap(E_ILLEGAL_ENCODING, "MEM_OOB")
        self.mem[addr:addr+len(data)] = data

    def read(self, addr: int, n: int) -> bytes:
        if addr < 0 or addr + n > len(self.mem):
            raise Trap(E_ILLEGAL_ENCODING, "MEM_OOB")
        return bytes(self.mem[addr:addr+n])

    def w_u32(self, addr: int, x: int):
        self.write(addr, struct.pack("<I", _u32(x)))

    def r_u32(self, addr: int) -> int:
        return struct.unpack_from("<I", self.mem, addr)[0]

    def w_u64(self, addr: int, x: int):
        self.write(addr, struct.pack("<Q", x & 0xFFFFFFFFFFFFFFFF))

    def r_u64(self, addr: int) -> int:
        return struct.unpack_from("<Q", self.mem, addr)[0]


class MasterTables:
    """
    Loads:
    - v18 master table mapping letter_index -> [18 u32]
    - csgi_entry_sha256 mapping letter_index -> 32 bytes

    For demo/test, can be injected (preloaded).
    """
    def __init__(self, v18_by_index: Dict[int, List[int]], csgi_sha_by_index: Dict[int, bytes]):
        self.v18 = v18_by_index
        self.csgi_sha = csgi_sha_by_index

    @staticmethod
    def minimal_demo():
        # Minimal set for ج(4), ا(0), م(23). Not real dataset, but deterministic.
        # For real banking system, replace with CSV/JSON loaders bound to dataset locks.
        v18 = {
            4:  [3,0,0,0, 0,0,0,0,0, 0,1,0,0,0, 0,0,1, 0],   # Jim: AQ=1
            0:  [0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0, 0],   # Alif: All zero
            23: [2,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0, 0],   # Mim: All zero (hat=2)
        }
        csgi = {
            4: _sha256("CSGI:ج".encode("utf-8")),
            0: _sha256("CSGI:ا".encode("utf-8")),
            23: _sha256("CSGI:م".encode("utf-8")),
        }
        return MasterTables(v18, csgi)

    def jim_mask(self) -> List[int]:
        J = self.v18[4]  # index 4 = ج
        return [int(x) & 1 for x in J]


class TranscriptBuilder:
    """
    HGSS/HC18DC deterministic transcript builder (simplified but normatively bound):
    - Header binds MH28+CSGI hashes.
    - Records contain v18 + closed_hint + csgi_entry_sha + vc1 bit+energy.
    - Aggregates: VC1_AGG (H6), GEO_AGG (H7).
    """
    def __init__(self, key_id: bytes, txid: bytes):
        self.key_id = key_id
        self.txid = txid
        self.records: List[bytes] = []
        self.vc1_hasher = hashlib.sha256()
        self.geo_hasher = hashlib.sha256()
        self.final_bytes: Optional[bytes] = None
        self.vc1_agg: Optional[bytes] = None
        self.geo_agg: Optional[bytes] = None

    @staticmethod
    def _energy(v18: List[int]) -> Tuple[int,int,int]:
        hat = int(v18[0])
        k_z = int(v18[8])
        q_t = int(v18[10])
        q_d = int(v18[11])
        q_s = int(v18[12])
        q_z = int(v18[13])
        U = q_t + 4*q_d + q_s + q_z + 2*k_z
        rho = hat - U
        return hat, U, rho

    @staticmethod
    def _vc1_bit(v18: List[int], jim_mask: List[int]) -> int:
        acc = 0
        for j in range(18):
            acc ^= ((int(v18[j]) & 1) & int(jim_mask[j]))
        return acc

    def append_record(self, v18: List[int], closed_hint: int, csgi_entry_sha256: bytes, jim_mask: List[int]):
        if len(v18) != 18:
            raise Trap(E_ILLEGAL_ENCODING, "V18_DIM")
        if closed_hint not in (0,1):
            raise Trap(E_ILLEGAL_ENCODING, "CLOSED_HINT_RANGE")
        if len(csgi_entry_sha256) != 32:
            raise Trap(E_ILLEGAL_ENCODING, "CSGI_SHA_DIM")

        b = self._vc1_bit(v18, jim_mask)
        hat, U, rho = self._energy(v18)

        # Update aggregates (normative binding)
        self.vc1_hasher.update(bytes([b]))
        self.vc1_hasher.update(struct.pack("<III", _u32(hat), _u32(U), _u32(rho)))

        self.geo_hasher.update(csgi_entry_sha256)
        self.geo_hasher.update(b"\x00"*32)  # mainpath_sha256 placeholder (all-zero in demo)
        self.geo_hasher.update(bytes([closed_hint]))

        # Canonical record bytes (simplified fixed layout):
        rec = bytearray()
        rec += bytes([closed_hint]) + b"\x00\x00\x00"
        rec += struct.pack("<" + "I"*18, *[_u32(x) for x in v18])
        rec += csgi_entry_sha256
        rec += b"\x00"*32  # mainpath_sha256 placeholder
        rec += bytes([b]) + b"\x00\x00\x00"
        rec += struct.pack("<III", _u32(hat), _u32(U), _u32(rho))
        self.records.append(bytes(rec))

    def finalize(self) -> Tuple[bytes, bytes, bytes]:
        self.vc1_agg = self.vc1_hasher.digest()
        self.geo_agg = self.geo_hasher.digest()

        header = bytearray()
        header += b"HGSS|HC18DC|v1.0|"
        header += MH28_SHA256
        header += CSGI28_SHA256
        header += struct.pack("<I", len(self.records))
        header += self.vc1_agg
        header += self.geo_agg
        header += struct.pack("<H", len(self.key_id)) + self.key_id
        header += struct.pack("<H", len(self.txid)) + self.txid

        self.final_bytes = bytes(header) + b"".join(self.records)
        return self.final_bytes, self.vc1_agg, self.geo_agg


class HCVM:
    """
    HCVM: deterministic crypto VM (Cube).
    Implements demo ISA required for HGSS cluster pipeline.
    """
    def __init__(
        self,
        code: bytes,
        mem: Memory,
        tables: MasterTables,
        lease: LeaseEvidence,
        master_secret: bytes,
        key_id: bytes,
        txid: bytes,
        key_provider: Optional[KeyProvider] = None,
        authority_pubkey: Optional[ec.EllipticCurvePublicKey] = None,
        verify_dataset_files: bool = False,
    ):
        self.code = code
        self.mem = mem
        self.tables = tables
        self.lease = lease
        self.master_secret = master_secret
        self.key_id = key_id
        self.txid = txid
        self.key_provider = key_provider
        self.authority_pubkey = authority_pubkey
        self.verify_dataset_files = verify_dataset_files

        # registers
        self.PC = 0
        self.S = [0] * 16
        self.V = [[0] * 18 for _ in range(16)]
        self.H = [b"\x00"*32 for _ in range(8)]

        self.CLOSED_HINT = 0
        self.prev_was_setflag = False

        self.halted = False
        self.ERR = 0

        self.trx: Optional[TranscriptBuilder] = None
        self.trx_bytes: Optional[bytes] = None

        self.k_aead: Optional[bytes] = None
        self.k_mac: Optional[bytes] = None
        self.last_nonce12: Optional[bytes] = None
        self.last_ciphertext: Optional[bytes] = None
        self.last_aad: Optional[bytes] = None

        self.key_ref: Optional[KeyRef] = None
        self.lease_verified: Optional[LeaseTokenVerified] = None

    def trap(self, err: int, msg: str = ""):
        self.ERR = err
        self.halted = True
        raise Trap(err, msg)

    # ---- Normative helper: prefix32 derivation (little-endian trunc)
    @staticmethod
    def expected_prefix32(key_id: bytes, node_id: bytes) -> int:
        d = _sha256(b"HGSS|HC18DC|NONCE|v1|" + key_id + node_id)
        return int.from_bytes(d[:4], "little")

    def op_verify_locks(self):
        # In full deployment, compute file hashes and compare to constants.
        # For test harness, we treat constants as locked truth.
        # If verify_dataset_files=True, integrate actual file hashing layer here.
        if len(MH28_SHA256) != 32 or len(CSGI28_SHA256) != 32:
            self.trap(E_DATASET_LOCK_FAIL, "LOCK_LEN")

        # Verify lease evidence binds to key_id and prefix32
        if self.lease.key_id != self.key_id:
            self.trap(E_DATASET_LOCK_FAIL, "LEASE_KEY_ID_MISMATCH")

        exp = self.expected_prefix32(self.key_id, self.lease.node_id)
        if int(self.lease.prefix32) != exp:
            self.trap(E_LEASE_PREFIX_MISMATCH, "PREFIX32_MISMATCH")

        # Banking Hardening: Verify Lease Signature
        if self.authority_pubkey is not None:
            if self.lease.token is None:
                self.trap(E_LEASE_SIGNATURE_INVALID, "MISSING_LEASE_TOKEN")
            try:
                verified = verify_lease_token_es256(self.lease.token, self.authority_pubkey)
                # Check expiry
                policy = LeasePolicy()
                if not policy.check_not_expired(verified.payload_map["expires_at"]):
                    self.trap(E_LEASE_SIGNATURE_INVALID, "LEASE_EXPIRED")
                
                # Check contents match evidence
                pm = verified.payload_map
                if pm["key_id_hex"] != self.key_id.hex() or pm["prefix32"] != self.lease.prefix32:
                    self.trap(E_LEASE_SIGNATURE_INVALID, "LEASE_TOKEN_CONTENT_MISMATCH")
                
                self.lease_verified = verified
            except Exception as e:
                self.trap(E_LEASE_SIGNATURE_INVALID, str(e))

    def audit_v18(self, v18: List[int], closed_hint: int):
        # Lane order assumed HL-18. Derived totals:
        hat = int(v18[0])
        nt,nf,nm = map(int, v18[1:4])
        km,kt,kd,ka,kz = map(int, v18[4:9])
        qa,qt,qd,qs,qz = map(int, v18[9:14])
        AN,AK,AQ = map(int, v18[14:17])
        eps = int(v18[17])

        if AN != (nt+nf+nm) or AK != (km+kt+kd+ka+kz) or AQ != (qa+qt+qd+qs+qz):
            self.trap(E_AUDIT_DERIVED_MISMATCH, "DERIVED")

        U = qt + 4*qd + qs + qz + 2*kz
        rho = hat - U
        if rho < 0:
            self.trap(E_AUDIT_RHO_NEGATIVE, "RHO_NEG")

        if eps not in (0,1):
            self.trap(E_AUDIT_EPS_RANGE, "EPS_RANGE")

        if closed_hint == 1 and (hat % 4) != 0:
            self.trap(E_AUDIT_MOD4, "MOD4")

    def derive_keys(self):
        # salt = MH28_SHA256; info includes aggregates + key_id + alg
        if self.trx is None or self.trx.vc1_agg is None or self.trx.geo_agg is None:
            self.trap(E_CRYPTO_FAIL, "KDF_NO_AGG")

        info = b"|".join([
            b"HC18DC", b"KDF", b"v1.0",
            b"aesgcm",
            b"KEYID=" + self.key_id,
            b"VC1=" + self.trx.vc1_agg,
            b"GEO=" + self.trx.geo_agg,
        ])

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=MH28_SHA256,
            info=info,
        )
        okm = hkdf.derive(self.master_secret)
        self.k_aead = okm[:32]
        self.k_mac = okm[32:64]

    def derive_keys_hsm(self):
        if self.key_provider is None:
            return self.derive_keys()
        
        if self.trx is None or self.trx.vc1_agg is None or self.trx.geo_agg is None:
            self.trap(E_CRYPTO_FAIL, "KDF_NO_AGG")

        k_aead, k_mac, ref = self.key_provider.derive_keys(
            key_id=self.key_id,
            vc1_agg=self.trx.vc1_agg,
            geo_agg=self.trx.geo_agg,
            aead_alg="aesgcm"
        )
        self.k_aead = k_aead
        self.k_mac = k_mac
        self.key_ref = ref

    def build_aad(self) -> bytes:
        if self.trx is None or self.trx.vc1_agg is None or self.trx.geo_agg is None:
            self.trap(E_CRYPTO_FAIL, "AAD_NO_AGG")
        return b"|".join([
            b"HGSS", b"HC18DC", b"v1.0",
            MH28_SHA256, CSGI28_SHA256,
            self.trx.vc1_agg, self.trx.geo_agg,
            b"KEYID=" + self.key_id,
            b"TXID=" + self.txid,
        ])

    def nonce_next(self, dst_ptr: int, lease_ptr: int):
        # Lease struct in memory (deterministic replay evidence)
        prefix32 = self.mem.r_u32(lease_ptr + 0)
        cur = self.mem.r_u64(lease_ptr + 8)
        end = self.mem.r_u64(lease_ptr + 16)

        exp_prefix32 = self.expected_prefix32(self.key_id, self.lease.node_id)
        if prefix32 != exp_prefix32:
            self.trap(E_LEASE_PREFIX_MISMATCH, "LEASE_PREFIX_MEM_MISMATCH")

        if cur > end:
            self.trap(E_LEASE_EXHAUSTED, "LEASE_EXHAUSTED")

        nonce12 = struct.pack("<I", prefix32) + struct.pack("<Q", cur)
        self.mem.write(dst_ptr, nonce12)
        self.last_nonce12 = nonce12

        # increment and store back
        self.mem.w_u64(lease_ptr + 8, cur + 1)

    def step(self):
        if self.halted:
            return

        w = fetch_u32_le(self.code, self.PC)
        opcode, rd, ra, rb, subop, imm8 = decode_iw(w)

        # SETFLAG: keep exact semantics like CMM-18C (CLOSED_HINT only)
        if opcode == 0x30:
            if (rd, ra, rb) != (0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "SETFLAG_FIELDS")
            if subop != 0:
                self.trap(E_ILLEGAL_ENCODING, "SETFLAG_SUBOP")
            if imm8 not in (0,1):
                self.trap(E_ILLEGAL_ENCODING, "SETFLAG_IMM8")
            self.CLOSED_HINT = imm8
            self.prev_was_setflag = True
            self.PC += 4
            return

        # For any non-SETFLAG instruction, consume/clear latch
        prev = self.prev_was_setflag
        self.prev_was_setflag = False

        # LDI_S (imm32 extension)
        if opcode == 0x40:
            if (ra, rb, subop, imm8) != (0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "LDI_FIELDS")
            imm32 = fetch_u32_le(self.code, self.PC + 4)
            self.S[rd] = imm32
            self.PC += 8
            return

        if opcode == 0x01:  # VERIFY_LOCKS
            if (rd,ra,rb,subop,imm8) != (0,0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "VERIFY_FIELDS")
            self.op_verify_locks()
            self.PC += 4
            return

        if opcode == 0x02:  # TRX_INIT (Rd = scalar ptr reg)
            if (ra,rb,subop,imm8) != (0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "TRX_INIT_FIELDS")
            base_ptr = self.S[rd]
            if base_ptr == 0:
                self.trap(E_ILLEGAL_ENCODING, "TRX_PTR_ZERO")
            self.trx = TranscriptBuilder(key_id=self.key_id, txid=self.txid)
            self.PC += 4
            return

        if opcode == 0x10:  # LDH_V18 Vd, #index
            if (ra,rb,subop) != (0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "LDH_V18_FIELDS")
            idx = imm8
            if idx not in self.tables.v18:
                self.trap(E_ILLEGAL_ENCODING, f"LDH_V18_UNKNOWN_IDX:{idx}")
            self.V[rd] = [int(x) for x in self.tables.v18[idx]]
            self.PC += 4
            return

        if opcode == 0x11:  # LDH_CSGI_H Hd, #index
            if (ra,rb,subop) != (0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "LDH_CSGI_FIELDS")
            idx = imm8
            if idx not in self.tables.csgi_sha:
                self.trap(E_ILLEGAL_ENCODING, f"LDH_CSGI_UNKNOWN_IDX:{idx}")
            self.H[rd] = self.tables.csgi_sha[idx]
            self.PC += 4
            return

        if opcode == 0x20:  # AUDIT_V18 (Vs = Rd) + CORE-1
            if not prev:
                self.trap(E_CONFORMANCE_SETFLAG_REQUIRED, "CORE1")
            if (ra,rb,subop,imm8) != (0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "AUDIT_FIELDS")
            Vs = rd  # NORMATIVE
            self.audit_v18(self.V[Vs], self.CLOSED_HINT)
            self.PC += 4
            return

        if opcode == 0x12:  # VC1 Sd, Vs (Vs=Ra)
            if (rb,subop,imm8) != (0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "VC1_FIELDS")
            if self.trx is None:
                self.trap(E_ILLEGAL_ENCODING, "VC1_NO_TRX")
            v = self.V[ra]
            jim_mask = self.tables.jim_mask()
            bit = TranscriptBuilder._vc1_bit(v, jim_mask)
            hat, U, rho = TranscriptBuilder._energy(v)
            self.S[rd] = bit
            self.S[(rd+1) & 0xF] = _u32(hat)
            self.S[(rd+2) & 0xF] = _u32(U)
            self.S[(rd+3) & 0xF] = _u32(rho)
            self.PC += 4
            return

        if opcode == 0x03:  # TRX_APPEND Vs,Hcsgi (Vs=Ra, Hcsgi=Rb)
            if (subop,imm8) != (0,0):
                self.trap(E_ILLEGAL_ENCODING, "TRX_APPEND_FIELDS")
            if self.trx is None:
                self.trap(E_ILLEGAL_ENCODING, "TRX_APPEND_NO_TRX")
            v = self.V[ra]
            csgi_sha = self.H[rb]
            jim_mask = self.tables.jim_mask()
            self.trx.append_record(v, self.CLOSED_HINT, csgi_sha, jim_mask)
            self.PC += 4
            return

        if opcode == 0x04:  # TRX_FINALIZE
            if (rd,ra,rb,subop,imm8) != (0,0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "TRX_FINALIZE_FIELDS")
            if self.trx is None:
                self.trap(E_ILLEGAL_ENCODING, "TRX_FINALIZE_NO_TRX")
            self.trx_bytes, vc1_agg, geo_agg = self.trx.finalize()
            self.H[6] = vc1_agg
            self.H[7] = geo_agg
            self.PC += 4
            return

        if opcode == 0x05:  # COMMIT_SHA256 (H0)
            if (rd,ra,rb,subop,imm8) != (0,0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "COMMIT_FIELDS")
            if self.trx_bytes is None:
                self.trap(E_CRYPTO_FAIL, "NO_TRX_BYTES")
            self.H[0] = _sha256(self.trx_bytes)
            self.PC += 4
            return

        if opcode == 0x06:  # KDF_HKDF_SHA256
            if (rd,ra,rb,subop,imm8) != (0,0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "KDF_FIELDS")
            self.derive_keys_hsm()
            self.PC += 4
            return

        if opcode == 0x07:  # HMAC_SHA256 (H3)
            if (rd,ra,rb,subop,imm8) != (0,0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "HMAC_FIELDS")
            if self.k_mac is None:
                self.trap(E_CRYPTO_FAIL, "NO_KMAC")
            self.H[3] = _hmac_sha256(self.k_mac, self.H[0])
            self.PC += 4
            return

        if opcode == 0x50:  # NONCE_NEXT (Rd=dst ptr scalar, Ra=lease ptr scalar)
            if (rb,subop,imm8) != (0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "NONCE_FIELDS")
            dst_ptr = self.S[rd]
            lease_ptr = self.S[ra]
            if dst_ptr == 0 or lease_ptr == 0:
                self.trap(E_ILLEGAL_ENCODING, "NONCE_PTR_ZERO")
            self.nonce_next(dst_ptr, lease_ptr)
            self.PC += 4
            return

        if opcode == 0x70:  # AEAD_AESGCM_ENC
            if (rd,ra,rb,subop,imm8) != (0,0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "AEAD_FIELDS")
            if self.k_aead is None or self.trx_bytes is None:
                self.trap(E_CRYPTO_FAIL, "AEAD_MISSING_INPUT")
            if self.last_nonce12 is None:
                # nonce expected to be in memory at S2, but we also store last_nonce12 on NONCE_NEXT
                self.trap(E_CRYPTO_FAIL, "AEAD_NO_NONCE")

            ct_ptr = self.S[3]  # convention: S3 points to ciphertext buffer
            if ct_ptr == 0:
                self.trap(E_ILLEGAL_ENCODING, "CT_PTR_ZERO")

            aad = self.build_aad()
            self.last_aad = aad
            try:
                ct = AESGCM(self.k_aead).encrypt(self.last_nonce12, self.trx_bytes, aad)
            except Exception as e:
                self.trap(E_CRYPTO_FAIL, "AESGCM_FAIL")

            self.last_ciphertext = ct
            self.mem.write(ct_ptr, ct)
            self.S[12] = len(ct)  # store length for tooling
            self.PC += 4
            return

        if opcode == 0xFF:  # HALT
            if (rd,ra,rb,subop,imm8) != (0,0,0,0,0):
                self.trap(E_ILLEGAL_ENCODING, "HALT_FIELDS")
            self.halted = True
            return

        self.trap(E_ILLEGAL_OPCODE, f"OP={opcode:#x}")

    def run(self, max_steps: int = 100000):
        steps = 0
        while not self.halted and steps < max_steps:
            self.step()
            steps += 1
        return steps
