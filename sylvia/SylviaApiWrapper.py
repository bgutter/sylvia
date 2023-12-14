#
# SylviaApiWrapper.py
#
# The simple, exposed code interface for Sylvia. Used by the EPC
# server and console interface.
#

from .PhoneticDictionary import *
from .PronunciationInferencer import *
from .Poem import *


class Sylvia(object):
    """
    Combined API wrapper for Sylvia.
    """

    def __init__(self, phoneticDictionary=None, pronunciationInferencer=None):
        """
        Construct a new Sylvia instance.

        Args:
            phoneticDictionary      - PhoneticDictionary to use. If None, the default will be loaded.
            pronunciationInferencer - PronunciationInferencer to use. If None, the default will be loaded.
        """
        self.pd = phoneticDictionary
        self.pi = pronunciationInferencer
        if self.pd is None:
            self.pd = loadDefaultPhoneticDictionary()
        if self.pi is None:
            self.pi = PronunciationInferencer()

    def getPronunciation(self, word, findAll=False):
        """
        Return the pronunciation, or pronunciations, for a word.

        Args:
            findAll - When False, return only the most likely pronunciation as a list of phonemes. This is
                      the first one listed in the dictionary, or an inferred pronunciation if not present.
                      When True, return a 2-tuple where the first item is a list of pronunciations from
                      the dictionary (potentially an empty list), and the second item is the inferred
                      pronunciation.

        Returns:
            See documentation on findAll argument.
        """
        dictEntries = self.pd.findPronunciations(word)
        if findAll or len(dictEntries) <= 0:
            inferred = self.pi.pronounce(word)
        if findAll:
            return (dictEntries, inferred)
        else:
            return dictEntries[0] if len(dictEntries) >= 1 else inferred

    @property
    def phoneticPatterns(self):
        """
        List all supported phonetic patterns.
        """
        return self.pd.getRhymeLevels()

    def generatePhoneticRegex(self, pronunciationOrWord, phoneticPattern):
        """
        Generate a specialized phonetic regular expression.

        Args:
            pronunciationOrWord - The base pronunciation or word.
            rhymeLevel          - The type of regular expression to generate for 'word'.

        Returns:
            If given a pronunciation, a string representing a phonetic regex. If given
            a word, then a list of regexes -- one per possible pronunciation.
        """
        assert phoneticPattern in self.phoneticPatterns
        ret = self.pd.getRhymeRegex(pronunciationOrWord, phoneticPattern)
        if isinstance(pronunciationOrWord, list):
            ret = ret[0]
        return ret
