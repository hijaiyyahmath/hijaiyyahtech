import struct

def assemble_words(*words: int) -> bytes:
    return b"".join(struct.pack("<I", w & 0xFFFFFFFF) for w in words)
