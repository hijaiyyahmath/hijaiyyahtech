import struct
from typing import Tuple

class Memory:
    def __init__(self, size: int = 1024 * 1024):
        self.data = bytearray(size)

    def write_words(self, address: int, words: list[int]):
        for i, word in enumerate(words):
            struct.pack_into("<I", self.data, address + i * 4, word & 0xFFFFFFFF)

    def read_words(self, address: int, count: int) -> list[int]:
        words = []
        for i in range(count):
            word = struct.unpack_from("<I", self.data, address + i * 4)[0]
            words.append(word)
        return words

    def read_v18(self, address: int) -> list[int]:
        return self.read_words(address, 18)
