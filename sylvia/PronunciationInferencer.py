#
# PronunciationInferencer.py
#
# Guess the pronunciation for words
#
# Status: EXTREMELY EXPERIMENTAL
#

from .PhonemeDetails import *
from .LetterDetails import *

import re

ACCEPTABLE_CHARS_RE = re.compile("[^a-zA-Z]")


def get_all_substrings(input_string):
    """
    https://stackoverflow.com/questions/22469997/how-to-get-all-the-contiguous-substrings-of-a-string-in-python
    """
    length = len(input_string)
    return [input_string[i : j + 1] for i in range(length) for j in range(i, length)]


def flatten_list(x):
    """
    https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
    """
    if x.__class__ == list:
        return [a for i in x for a in flatten_list(i)]
    else:
        return [x]


def superSanitizeWord(word):
    """
    We can work only with letters for now...
    TODO We really should start handling apostrophes. Else, we get things like:
      "she's" -> [ SH EH S ]
    instead of
      "she's" -> [ SH IY Z ]
    """
    return ACCEPTABLE_CHARS_RE.sub("", word)


class PronunciationRule(object):
    """
    Single atomic rule for translating some sequence of letters
    (in context) into a sequence of phonemes.
    """

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        return str([str(k) + ": " + str(v) for k, v in self.kwargs.items()])

    def applyOnce(self, word, startIdx, endIdx):
        if "sequence" in self.kwargs:
            #
            # Dumb sequence search
            #
            sequence = self.kwargs["sequence"]
            if "alignEnd" in self.kwargs and self.kwargs["alignEnd"]:
                if endIdx != len(word):
                    return None
                if len(sequence) > (len(word) - startIdx):
                    return None
                if word[-len(sequence) :][::-1] == sequence[::-1]:
                    return (
                        len(word) - len(sequence),
                        len(word),
                        self.kwargs["phonemes"],
                    )
                else:
                    return None
            if "alignStart" in self.kwargs and self.kwargs["alignStart"]:
                if startIdx != 0:
                    return None
                if len(sequence) > (len(word) - endIdx):
                    return None
                if word[:endIdx] == sequence:
                    return (0, len(sequence), self.kwargs["phonemes"])
                else:
                    return None
            idx = word[startIdx:endIdx].find(sequence)
            if idx >= 0:
                idx += startIdx
                return (idx, idx + len(sequence), self.kwargs["phonemes"])
            return None


class PronunciationInferencer(object):
    """
    Construct a ruleset for translating character patterns to
    pronunciations, or find character<->phoneme alignments.
    """

    def __init__(self):
        self.rules = []
        self._generateRules()

    def addRule(self, rule, priorityOver=[]):
        """
        Add a PronunciationRule
        """
        self.rules = [rule] + self.rules

    def dumpModel(self, path):
        """
        Save model to a file
        """
        pass

    def _generateRules(self):
        """
        Build up our ruleset
        """

        #
        # Single letter defaults ensure we always have
        # Some guess at a pronunciation
        #
        singleLetterDefaults = {
            "a": "AE",
            "b": "B",
            "c": "K",
            "d": "D",
            "e": "EH",
            "f": "F",
            "g": "G",
            "h": "HH",
            "i": "IH",
            "j": "JH",
            "k": "K",
            "l": "L",
            "m": "M",
            "n": "N",
            "o": "AA",
            "p": "P",
            "q": "K",
            "r": "R",
            "s": "S",
            "t": "T",
            "u": "AH",
            "v": "V",
            "w": "W",
            "x": ["K", "S"],
            "y": "Y",
            "z": "Z",
        }
        for l, p in singleLetterDefaults.items():
            if p.__class__ != list:
                p = [p]
            self.addRule(PronunciationRule(sequence=l, phonemes=p, priority=0))
        self.addRule(PronunciationRule(sequence="y", phonemes=["IY"], alignEnd=True))

        #
        # Override a single "o" if it appears at the end of a sequence
        #
        self.addRule(PronunciationRule(sequence="o", phonemes=["OW"], alignEnd=True))

        #
        # Double vowel sounds
        #
        doubleVowels = {"a": "AE", "e": "IY", "o": "UW"}

        #
        # Other high priority sequences
        #
        self.addRule(PronunciationRule(sequence="que", phonemes=["K"], alignEnd=True))
        highPrioritySequences = {
            "ck": "K",
            "er": "ER",
            "sh": "SH",
            "ai": "EY",
            "au": "AO",
            "oi": "OY",
            "oy": "OY",
            "ng": "NG",
            "ie": "IY",
            "ay": "EY",
            "ea": "IY",
            "ch": "CH",
            "or": ["AO", "R"],
            "ur": "ER",
            "ou": "AO",
            "ign": ["AY", "N"],
            "igm": ["AY", "M"],
            "qu": ["K", "W"],
            "oa": "OW",
            "ow": "OW",
            "ei": "IY",
            "th": "TH",
        }
        for l, p in highPrioritySequences.items():
            if p.__class__ != list:
                p = [p]
            self.addRule(PronunciationRule(sequence=l, phonemes=p, priority=3))

        #
        # Double consonant sounds
        #
        doubleConsonants = {
            "b": "B",
            "c": "S",
            "d": "D",
            "f": "F",
            "g": "G",
            "j": "JH",
            "k": "K",
            "l": "L",
            "m": "M",
            "m": "N",
            "p": "P",
            "r": "R",
            "s": "S",
            "t": "T",
            "v": "V",
            "w": "W",
            "x": ["K", "S"],
            "z": "ZH",
        }
        for l, p in doubleConsonants.items():
            if p.__class__ != list:
                p = [p]
            self.addRule(PronunciationRule(sequence=l + l, phonemes=p, priority=1))

        #
        # le$ becomes [ AH L ], like little, subtle, quibble...
        #
        self.addRule(
            PronunciationRule(sequence="le", phonemes=["AH", "L"], alignEnd=True)
        )

        #
        # silent e patterns
        #
        silentELeadingVowels = {"a": "EY", "e": "IY", "i": "AY", "o": "OW", "u": "UW"}
        silentELinkingNonDefaultConsonants = {"c": "S", "g": "JH"}
        for leadingVowel, vowelSound in silentELeadingVowels.items():
            for linkingConsonant, consonantSound in singleLetterDefaults.items():
                if linkingConsonant in VOWEL_LETTERS:
                    continue
                if linkingConsonant in list(silentELinkingNonDefaultConsonants.keys()):
                    continue
                self.addRule(
                    PronunciationRule(
                        sequence=leadingVowel + linkingConsonant + "e",
                        phonemes=flatten_list([vowelSound, consonantSound]),
                        alignEnd=True,
                    )
                )
            for (
                linkingConsonant,
                consonantSound,
            ) in silentELinkingNonDefaultConsonants.items():
                self.addRule(
                    PronunciationRule(
                        sequence=leadingVowel + linkingConsonant + "e",
                        phonemes=flatten_list([vowelSound, consonantSound]),
                        alignEnd=True,
                    )
                )

        #
        # ing patterns
        #
        for leadingVowel, vowelSound in silentELeadingVowels.items():
            for linkingConsonant, consonantSound in singleLetterDefaults.items():
                if linkingConsonant in VOWEL_LETTERS:
                    continue
                if linkingConsonant in list(silentELinkingNonDefaultConsonants.keys()):
                    continue
                self.addRule(
                    PronunciationRule(
                        sequence=leadingVowel + linkingConsonant + "ing",
                        phonemes=flatten_list([vowelSound, consonantSound, "IH", "NG"]),
                        alignEnd=True,
                    )
                )
            for (
                linkingConsonant,
                consonantSound,
            ) in silentELinkingNonDefaultConsonants.items():
                self.addRule(
                    PronunciationRule(
                        sequence=leadingVowel + linkingConsonant + "ing",
                        phonemes=flatten_list([vowelSound, consonantSound, "IH", "NG"]),
                        alignEnd=True,
                    )
                )

        #
        # ed patterns
        #
        self.addRule(PronunciationRule(sequence="ed", phonemes=["T"], alignEnd=True))
        for leadingVowel, vowelSound in silentELeadingVowels.items():
            for linkingConsonant, consonantSound in singleLetterDefaults.items():
                if linkingConsonant in VOWEL_LETTERS:
                    continue
                if linkingConsonant in list(silentELinkingNonDefaultConsonants.keys()):
                    continue
                if linkingConsonant == "t":
                    self.addRule(
                        PronunciationRule(
                            sequence=leadingVowel + linkingConsonant + "ed",
                            phonemes=flatten_list(
                                [vowelSound, consonantSound, "EH", "D"]
                            ),
                            alignEnd=True,
                        )
                    )
                else:
                    self.addRule(
                        PronunciationRule(
                            sequence=leadingVowel + linkingConsonant + "ed",
                            phonemes=flatten_list([vowelSound, consonantSound, "T"]),
                            alignEnd=True,
                        )
                    )
            for (
                linkingConsonant,
                consonantSound,
            ) in silentELinkingNonDefaultConsonants.items():
                self.addRule(
                    PronunciationRule(
                        sequence=leadingVowel + linkingConsonant + "ed",
                        phonemes=flatten_list([vowelSound, consonantSound, "T"]),
                        alignEnd=True,
                    )
                )

        #
        # y at end of word after consonants
        #
        for leadingVowel, vowelSound in silentELeadingVowels.items():
            for linkingConsonant, consonantSound in singleLetterDefaults.items():
                if linkingConsonant in VOWEL_LETTERS:
                    continue
                if linkingConsonant in list(silentELinkingNonDefaultConsonants.keys()):
                    continue
                if linkingConsonant == "x":
                    continue
                self.addRule(
                    PronunciationRule(
                        sequence=leadingVowel + linkingConsonant + "y",
                        phonemes=flatten_list([vowelSound, consonantSound, "IY"]),
                        alignEnd=True,
                    )
                )
            for (
                linkingConsonant,
                consonantSound,
            ) in silentELinkingNonDefaultConsonants.items():
                self.addRule(
                    PronunciationRule(
                        sequence=leadingVowel + linkingConsonant + "y",
                        phonemes=flatten_list([vowelSound, consonantSound, "IY"]),
                        alignEnd=True,
                    )
                )

        #
        # Double vowels
        #
        for l, p in doubleVowels.items():
            if p.__class__ != list:
                p = [p]
            self.addRule(PronunciationRule(sequence=l + l, phonemes=p, priority=1))

        #
        # Ending s (z sound after t) without breaking silent e and ing
        #

        #
        # ey -> [ IY ] as in keystone, hackney, etc
        #
        # TODO: This is probably a 50/50. EY is extremely common too (hey, survey, etc),
        #       and I can't think of a simple way to decide between them offhand.
        #
        #       Regardless, having something here prevents us from guessing the "e" and
        #       the "y" separately, which causes double vowel phonemes and messes up
        #       syllable counts.
        #
        self.addRule(PronunciationRule(sequence="ey", phonemes=["IY"]))

        #
        # Silent gh
        #
        self.addRule(PronunciationRule(sequence="gh", phonemes=["F"]))
        self.addRule(PronunciationRule(sequence="igh", phonemes=["AY"]))
        self.addRule(PronunciationRule(sequence="eigh", phonemes=["EY"]))

        #
        # Silent k
        #
        self.addRule(PronunciationRule(sequence="kn", phonemes=["N"], alignStart=True))

        #
        # ea in feathers?
        # Ambiguous: beather could be [ B IY DH ER ] or [ B EH DH ER ]

        #
        # ew becomes [ UW ], like in spew, skewer, hewn, etc.
        #
        self.addRule(PronunciationRule(sequence="ew", phonemes=["UW"], alignEnd=True))

        #
        # air becomes [ EH R ], like in hair, bair, stairs
        # ai, without an r, generally becomes EY
        #
        self.addRule(PronunciationRule(sequence="air", phonemes=["EH", "R"]))

        #
        # Phoneme sound type cases bags -- Z vs IH Z
        #

        #
        # ous$ -> [ AH S ]
        #
        self.addRule(
            PronunciationRule(sequence="ous", phonemes=["AH", "S"], alignEnd=True)
        )
        self.addRule(PronunciationRule(sequence="a", phonemes=["AH"], alignEnd=True))

        #
        # th -> [ DH ]
        #
        self.addRule(PronunciationRule(sequence="th", phonemes=["DH"], alignEnd=True))

    def _pronouncePartial(self, word, startIdx, endIdx):
        """
        Recursive prnunciation generation call
        """
        for rule in self.rules:
            ret = rule.applyOnce(word, startIdx, endIdx)
            if ret is not None:
                consumedCharsStart, consumedCharsStop, correspondingPhonemes = ret
                if consumedCharsStart > startIdx:
                    if consumedCharsStop < endIdx:
                        return (
                            self._pronouncePartial(word, startIdx, consumedCharsStart)
                            + correspondingPhonemes
                            + self._pronouncePartial(word, consumedCharsStop, endIdx)
                        )
                    else:
                        return (
                            self._pronouncePartial(word, startIdx, consumedCharsStart)
                            + correspondingPhonemes
                        )
                else:
                    if consumedCharsStop < endIdx:
                        return correspondingPhonemes + self._pronouncePartial(
                            word, consumedCharsStop, endIdx
                        )
                    else:
                        return correspondingPhonemes
            else:
                # We'll try the next one
                pass
        print(word)
        assert False

    def pronounce(self, word):
        """
        Do it.
        """
        word = sanitizeWord(word).lower()
        word = superSanitizeWord(word)
        return self._pronouncePartial(word, 0, len(word))
