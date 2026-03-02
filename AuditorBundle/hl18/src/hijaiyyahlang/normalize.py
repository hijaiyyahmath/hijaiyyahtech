import unicodedata

def normalize_letter_id(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u0640", "") # remove tatweel
    return s
