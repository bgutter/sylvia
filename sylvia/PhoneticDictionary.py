#
# PhoneticDictionary.py
#
# Interface with the CMU Pronouncing Dictionary to find words
# based on their pronunciation.
#

from .PhonemeDetails import *
from .LetterDetails import *

import pkg_resources
import sys
import re
import os
import itertools
import code


def loadDefaultPhoneticDictionary():
    """
    Load the encoded dictionary distributed with Sylvia.
    """
    return PhoneticDictionary(
        binFile=pkg_resources.resource_stream("sylvia", "data/cmudict.sylviabin")
    )


def dictListAdd(d, k, v):
    """
    Maintain a dictionary whose values are lists of values.
    """
    if k not in d:
        d[k] = [v]
    else:
        d[k].append(v)


def encodePhonemeString(phonemeString):
    """
    Encode to some character value above 127. This is to keep our encoded values
    outside of the typical ASCII range, and hopefully avoid anyone getting cute with
    the built-in character classes. It's probably a bad, broken, idea, but it seems
    to work fine.
    """
    return PHONEME_DETAILS__by_text[sanitizePhonemeString(phonemeString)].encoded()


def decodePhonemeByte(phonemeByte):
    """
    Returns the string for this byte.
    """
    return PHONEME_DETAILS__by_encoded[phonemeByte].decoded()


def encodePronunciation(pronunciationTokens):
    """
    Return the encoded version of a pronunciation.
    """
    return "".join([encodePhonemeString(p) for p in pronunciationTokens])


def decodePronunciation(pronunciationBuffer):
    """
    Return the decoded list corresponding to this encoded buffer.
    """
    return [decodePhonemeByte(x) for x in pronunciationBuffer]


def preprocessPhoneticRegex(regexTextUnpreprocessed):
    """
    Perform proper substitutions and fomatting to convert user
    input for regex into one which is Python-compliant, and will
    function on our encoded pronunciations.
    """
    encodedTokens = []
    for token in re.split("(%|#|@|(?:[^a-zA-Z#@%]+))", regexTextUnpreprocessed):
        if token == "#":
            encodedTokens.append(ANY_CONSONANT_SOUND_REGEX_TEXT)
            continue
        if token == "@":
            encodedTokens.append(ANY_VOWEL_SOUND_REGEX_TEXT)
            continue
        if token == "%":
            encodedTokens.append(ANY_SYLLABLE_REGEX_TEXT)
            continue
        tryPhoneme = sanitizePhonemeString(token)
        if tryPhoneme in list(PHONEME_DETAILS__by_text.keys()):
            encodedTokens.append(encodePhonemeString(tryPhoneme))
            continue
        encodedTokens.append(token.replace(" ", ""))
    return "".join(encodedTokens)


class PhoneticDictionary(object):
    """
    Software API for reading and working with dictionary files
    """

    def __init__(self, textFile=None, binFile=None, wordPopFile=None):
        """
        Read input file
        """
        if textFile is not None and wordPopFile is not None:
            self.load__text(textFile, wordPopFile)
        elif binFile is not None:
            self.load__bin(binFile)
        else:
            #
            # Need either a text phonetic dict and a text popularity map, OR a single bin file
            #
            assert False

    def load__text(self, finPhonetic, finPop):
        """
        Read text format dictionary into memory
        """
        wsre = re.compile(r"\s+")

        self.entries = {}
        self.popularities = {}

        #
        # Get pronunciations. May be multiple per word
        #
        for line in finPhonetic:
            if line[0:3] == ";;;":
                continue
            parts = [x for x in wsre.split(line) if len(x) > 0]
            word = sanitizeWord(parts[0])
            pronunciation = encodePronunciation(parts[1:])
            dictListAdd(self.entries, word, pronunciation)

        #
        # Get popularities. One for each unique word.
        #
        for line in finPop:
            parts = [x for x in wsre.split(line) if len(x) > 0]
            word = sanitizeWord(parts[0])
            self.popularities[word] = int(parts[1])

    def load__bin(self, fin):
        """
        Load binary format dictionary into memory
        """
        self.entries = {}
        self.popularities = {}
        buf = fin.read()
        lines = buf.split(b'\n')
        for line in lines:
            if len(line) == 0:
                continue
            word, popularity, pronunciation = line.split(b" ")
            self.popularities[word] = int(popularity)
            dictListAdd(self.entries, word, pronunciation)

    def getRhymeLevels(self):
        """
        Return list of supported rhyme levels for self.getRhymeRegex()
        """
        return ["default", "perfect", "loose"]

    def getEntries(self):
        """
        Get a list of all the words in the dictionary.
        """
        return list(self.entries.keys())

    def sortWordsByPopularity(self, words):
        """
        Return a closure which sorts words based on their popularity
        as the key function to sorted()
        """
        return sorted(words, key=lambda x: -self.findPopularity(x))

    def saveBin(self, outPath):
        """
        Dump compiled version of dictionary to disk.
        """
        with open(outPath, "wb") as fout:
            for word, encodedPronunciations in self.entries.items():
                for encodedPronunciation in encodedPronunciations:
                    # TODO: We actially shouldn't save popularity per-pronunciation, since it's keyed on text. Waste of space.
                    fout.write(
                        word
                        + " "
                        + str(self.findPopularity(word))
                        + " "
                        + encodedPronunciation
                        + "\n"
                    )
        fout.close()

    def regexSearch(self, regexTextUnpreprocessed):
        """
        Apply phonetic regex to each entry in the dict, returning
        a list of words.

        Regex will automatically be wrapped in '^' and '$'. Use '.*' before and after
        query if you do not wish to align the match to start and/or end.

        If you pass a list of regex, the result will contain those which match any.
        """
        if regexTextUnpreprocessed.__class__ == list:
            #
            # Call recursively to handle lists of regexes.
            # TODO: We're doing some pointless sorting here. Change to an inner/outer
            #       architecture.
            result = set()
            for r in regexTextUnpreprocessed:
                result |= set(self.regexSearch(r))
            return self.sortWordsByPopularity(list(result))

        matchingWords = []
        regex = re.compile(preprocessPhoneticRegex(regexTextUnpreprocessed) + "$")
        for word, encodedPronunciations in self.entries.items():
            for encodedPronunciation in encodedPronunciations:
                if regex.match(encodedPronunciation):
                    matchingWords.append(word)
        return self.sortWordsByPopularity(list(set(matchingWords)))

    def letterRegexSearch(self, regex):
        """
        Find words we know which match this regex. Note that this is a normal,
        character based regular expression, and has nothing to do with pronunciations.

        Regex will automatically be wrapped in '^' and '$'. Use '.*' before and after
        query if you do not wish to align the match to start and/or end.
        """
        matchingWords = []
        regex = re.compile("^" + regex + "$", flags=re.I)
        for word in list(self.entries.keys()):
            if regex.match(word):
                matchingWords.append(word)
        return self.sortWordsByPopularity(list(set(matchingWords)))

    def findPronunciations(self, word):
        """
        Return a list of pronunciations for word in dictionary
        """
        return [
            decodePronunciation(p) for p in self.entries.get(sanitizeWord(word), [])
        ]

    def findPopularity(self, word):
        """
        Spit out the popularity for given word.
        """
        return self.popularities.get(sanitizeWord(word), -1)

    def getRhymeRegex(self, pronunciationOrWord, level="default"):
        """
        Given a pronunciation or word, as well as a rhyme level, return a list
        of phoneme regexes which would strictly match "rhymes" for that word.

        The number of regexes returned will match the number of possible pronunciations
        for the provided word. If a pronunciation is passed, there will be only
        one item in the list
        """
        ret = []

        #
        # Define word and pronunciation from pronunciationOrWord
        # NOTE: word will remain None whenever a pronunciation has been passed.
        #
        word = None
        if isinstance(pronunciationOrWord, str):
            word = sanitizeWord(pronunciationOrWord)
            pronunciations = self.findPronunciations(word)
        elif pronunciationOrWord.__class__ == list:
            pronunciations = [pronunciationOrWord]
        else:
            raise TypeError(
                "Can't interpret pronunciationOrWord of type {}.".format(
                    pronunciationOrWord.__class__
                )
            )

        if level == "perfect":
            #
            # All words which:
            # - Contain the same sequence of phonemes as the given
            #   pronunciation, including and following the first vowel
            #   in the given pronunciation
            #
            # * Example:
            # [ CH AE T ER ] (from "chatter")
            #
            # Phonemes after and including the first vowel:
            # [ AE T ER]
            #
            # Anything can happen before:
            #
            # [ .* AE T ER ]
            #
            for pronunciation in pronunciations:
                mustEndWith = pronunciation[
                    [isVowelSound(x) for x in pronunciation].index(True) :
                ]
                ret.append(".* " + " ".join(mustEndWith))

        elif level == "default":
            #
            # Same as perfect, except:
            # - Consonant sounds can be interspersed between the
            #   matched sequence phonemes.
            #
            # * Example
            # Starting off from "perfect" example, allow interspersed
            # consonant sounds.
            #
            # [ .* AE #* T #* ER #* ]
            #
            for pronunciation in pronunciations:
                mustEndWith = pronunciation[
                    [isVowelSound(x) for x in pronunciation].index(True) :
                ]
                ret.append(".* " + " #*".join(mustEndWith) + "#*")

        elif level == "loose":
            #
            # This strategy ignores consonant sounds entirely. It
            # matches any word that:
            # - Contains the same sequence of vowel phonemes as the
            #   given pronunciation
            # - Contains no additional vowels after that sequence
            # - Can have any consonant sounds anywhere
            # - Can have any vowel sounds before the sequence.
            #
            # * Example
            #
            # [ CH AE T ER ] (from "chatter")
            #
            # Vowel sounds only:
            # [ AE ER ]
            #
            # Consonant sounds allowed in between:
            # [ AE #* ER #* ]
            #
            # Anything before:
            # [ .* AE #* ER #* ]
            #
            for pronunciation in pronunciations:
                ret.append(
                    ".* "
                    + " #*".join([x for x in pronunciation if isVowelSound(x)])
                    + " #*"
                )

        else:
            raise ValueError("Unknown rhyme level given: {}".format(level))

        return ret
