ALL_ENGLISH_LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                       "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

ALL_FRENCH_LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                      "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                      "à", "â", "æ", "ç", "é", "è", "ê", "ë", "î", "ï", "ô", "œ", "ù", "û", "ü", "ÿ"]

ENGLISH_TO_FRENCH = {"a": "a", "b": "b", "c": "c", "d": "d", "e": "e", "f": "f", "g": "g", "h": "h", "i": "i", "j": "j", "k": "k", "l": "l", "m": "m",
                     "n": "n", "o": "o", "p": "p", "q": "q", "r": "r", "s": "s", "t": "t", "u": "u", "v": "v", "w": "w", "x": "x", "y": "y", "z": "z",
                     "à": "à", "â": "â", "æ": "æ", "ç": "ç", "é": "é", "è": "è", "ê": "ê", "ë": "ë", "î": "î", "ï": "ï", "ô": "ô", "œ": "œ", "ù": "ù", "û": "û", "ü": "ü", "ÿ": "ÿ"}

FRENCH_TO_ENGLISH = {"a": "a", "b": "b", "c": "c", "d": "d", "e": "e", "f": "f", "g": "g", "h": "h", "i": "i", "j": "j", "k": "k", "l": "l", "m": "m",
                     "n": "n", "o": "o", "p": "p", "q": "q", "r": "r", "s": "s", "t": "t", "u": "u", "v": "v", "w": "w", "x": "x", "y": "y", "z": "z",
                     "à": "a", "â": "a", "æ": "ae", "ç": "c", "é": "e", "è": "e", "ê": "e", "ë": "e", "î": "i", "ï": "i", "ô": "o", "œ": "oe", "ù": "u", "û": "u", "ü": "u", "ÿ": "y"}

SELECT_LETTER_DICT = {"English": ALL_ENGLISH_LETTERS,
                      "French": ALL_FRENCH_LETTERS}
CHECK_LETTER_DICT = {"EnglishToFrench": ENGLISH_TO_FRENCH,
                     "FrenchToEnglish": FRENCH_TO_ENGLISH}