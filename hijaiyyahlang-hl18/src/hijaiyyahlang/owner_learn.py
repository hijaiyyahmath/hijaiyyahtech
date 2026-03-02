"""
owner_learn.py — Owner-Learning Recognizer

Continuous recognition from codex sequences using bigram frequency model.
Input standardized via letter_id (NFC + strip tatweel, H28-only).
"""
from __future__ import annotations
import json
import math
from typing import Dict, Optional, Tuple

from hijaiyyahlang.ir import letter_id, H28_SET, validate_letter


class OwnerModel:
    """
    Bigram frequency model for owner writing pattern recognition.
    Operates on letter_id sequences (NFC + strip tatweel).
    """

    def __init__(self):
        self._bigrams: Dict[Tuple[str, str], int] = {}
        self._unigrams: Dict[str, int] = {}
        self._total_bigrams: int = 0
        self._total_words: int = 0

    def observe(self, word: str) -> None:
        """
        Update bigram frequencies from a word.
        word: string of Hijaiyyah letters (e.g. "بسم").
        Tatweel (U+0640) is stripped before processing.
        """
        # Strip tatweel first, then validate each character
        cleaned = word.replace("\u0640", "")
        letters = [validate_letter(ch) for ch in cleaned]
        if len(letters) < 1:
            return

        self._total_words += 1

        # Unigrams
        for lid in letters:
            self._unigrams[lid] = self._unigrams.get(lid, 0) + 1

        # Bigrams (including start/end markers)
        tokens = ["^"] + letters + ["$"]
        for i in range(len(tokens) - 1):
            pair = (tokens[i], tokens[i + 1])
            self._bigrams[pair] = self._bigrams.get(pair, 0) + 1
            self._total_bigrams += 1

    def recognize(self, word: str) -> float:
        """
        Compute similarity score of `word` to the owner profile.
        Returns float in [0.0 .. 1.0].
        Higher = more similar to observed patterns.
        """
        if self._total_bigrams == 0:
            return 0.0  # no training data

        letters = [validate_letter(ch) for ch in word]
        if len(letters) < 1:
            return 0.0

        tokens = ["^"] + letters + ["$"]
        log_prob = 0.0
        n_bigrams = len(tokens) - 1
        vocab_size = len(H28_SET) + 2  # +2 for ^ and $

        for i in range(n_bigrams):
            pair = (tokens[i], tokens[i + 1])
            count = self._bigrams.get(pair, 0)
            # Laplace smoothing
            prob = (count + 1) / (self._total_bigrams + vocab_size)
            log_prob += math.log(prob)

        # Normalize to [0, 1] using sigmoid-like transform
        avg_log = log_prob / n_bigrams
        # Map avg_log from [-inf, 0] to [0, 1]
        score = 1.0 / (1.0 + math.exp(-avg_log - 3.0))
        return min(1.0, max(0.0, score))

    def save(self, path: str) -> None:
        """Save owner profile to JSON."""
        data = {
            "version": "OwnerModel-1.0",
            "total_words": self._total_words,
            "total_bigrams": self._total_bigrams,
            "unigrams": self._unigrams,
            "bigrams": {f"{a}|{b}": c
                        for (a, b), c in self._bigrams.items()},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> OwnerModel:
        """Load owner profile from JSON."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        model = cls()
        model._total_words = data["total_words"]
        model._total_bigrams = data["total_bigrams"]
        model._unigrams = data.get("unigrams", {})
        model._bigrams = {
            tuple(k.split("|", 1)): v
            for k, v in data["bigrams"].items()
        }
        return model
