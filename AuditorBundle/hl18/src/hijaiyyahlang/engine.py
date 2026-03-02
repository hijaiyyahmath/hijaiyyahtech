from __future__ import annotations
from dataclasses import dataclass
from typing import List
from .dataset import Dataset18, cod_word
from .normalize import normalize_letter_id

@dataclass(frozen=True)
class EncodedWord:
    text: str
    letters: List[str]
    v18: List[int]

def encode_text(ds: Dataset18, text: str) -> EncodedWord:
    # Normalize each character
    norm_text = "".join(normalize_letter_id(c) for c in text if not c.isspace())
    v = cod_word(norm_text, ds)
    return EncodedWord(text=text, letters=list(norm_text), v18=v)
