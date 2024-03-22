def isDevanagariWord(word: str) -> bool:
    devanagari_range = (0x0900, 0x097F)
    return all(ord(char) >= devanagari_range[0] and ord(char) <= devanagari_range[1] for char in word)


def isKannadaWord(word: str) -> bool:
    kannada_range = (0x0C80, 0x0CFF)
    return all(ord(char) >= kannada_range[0] and ord(char) <= kannada_range[1] for char in word)