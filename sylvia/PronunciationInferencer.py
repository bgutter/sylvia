#
# PronunciationInferencer.py
#
# Guess the pronunciation for words
#
# Status: EXTREMELY EXPERIMENTAL
#

from PhonemeDetails import *
from LetterDetails import *

def get_all_substrings(input_string):
    """
    https://stackoverflow.com/questions/22469997/how-to-get-all-the-contiguous-substrings-of-a-string-in-python
    """
    length = len( input_string )
    return [ input_string[ i : j + 1 ] for i in xrange( length ) for j in xrange( i, length ) ]

def flatten_list( x ):
    """
    https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
    """
    if x.__class__ == list:
        return [a for i in x for a in flatten_list(i)]
    else:
        return [x]

class PronunciationRule( object ):
    """
    Single atomic rule for translating some sequence of letters
    (in context) into a sequence of phonemes.
    """

    def __init__( self, *args, **kwargs ):
        self.kwargs = kwargs

    def __repr__( self ):
        return str( [ str( k ) + ": " + str( v ) for k, v in self.kwargs.iteritems() ] )

    def applyOnce( self, word, startIdx, endIdx ):
        if 'sequence' in self.kwargs:
            #
            # Dumb sequence search
            #
            sequence = self.kwargs[ 'sequence' ]
            if 'alignEnd' in self.kwargs and self.kwargs[ 'alignEnd' ]:
                if endIdx != len( word ):
                    return None
                if word[ -len( sequence ) : ][:: -1 ] == sequence[::-1]:
                    return ( len( word ) - len( sequence ), len( word ), self.kwargs[ 'phonemes' ] )
                else:
                    return None
            idx = word[ startIdx : endIdx ].find( sequence )
            if idx >= 0:
                idx += startIdx
                return ( idx, idx + len( sequence ), self.kwargs[ 'phonemes' ] )
            return None

class PronunciationInferencer( object ):
    """
    Construct a ruleset for translating character patterns to
    pronunciations, or find character<->phoneme alignments.
    """

    def __init__( self ):
        self.rules = []
        self._generateRules()

    def addRule( self, rule, priorityOver=[] ):
        """
        Add a PronunciationRule
        """
        self.rules = [ rule ] + self.rules

    def dumpModel( self, path ):
        """
        Save model to a file
        """
        pass

    def _generateRules( self ):
        """
        Build up our ruleset
        """
        #if len( word ) == 0:
        #    return []
        #if len( word ) >= 2 and word[-1] == 's' and word[-2] != 's' and word[-2] in CONSONANT_LETTERS:
        #    return self._inferPronunciationPartial( word[:-1], 0, len( word ) - 1 ) + [ "Z" if word[-2] is not 't' else "S" ]

        #
        # Single letter defaults ensure we always have
        # Some guess at a pronunciation
        #
        singleLetterDefaults = { 'a': 'AE', 'b': 'B', 'c': 'K', 'd': 'D', 'e': 'EH', 'f': 'F', 'g': 'G', 'h': 'HH', 'i': 'IH', 'j': 'JH', 'k': 'K',
                                 'l': 'L', 'm': 'M', 'n': 'N', 'o': 'AA', 'p': 'P', 'q': 'K', 'r': 'R', 's': 'S', 't': 'T', 'u': 'AH', 'v': 'V',
                                 'w': 'W', 'x': [ 'K', 'S' ], 'y': 'Y', 'z': 'Z' }
        for l, p in singleLetterDefaults.iteritems():
            if p.__class__ != list:
                p = [ p ]
            self.addRule( PronunciationRule( sequence=l, phonemes=p, priority=0 ) )
        self.addRule( PronunciationRule( sequence="y", phonemes=[ "IY" ], alignEnd=True ) )

        #
        # Double vowel sounds
        #
        doubleVowels = { 'a' : 'AE', 'e' : "IY", 'o' : 'UW' }
        for l, p in doubleVowels.iteritems():
            if p.__class__ != list:
                p = [ p ]
            self.addRule( PronunciationRule( sequence=l+l, phonemes=p, priority=1 ) )

        #
        # Other high priority sequences
        #
        self.addRule( PronunciationRule( sequence="que", phonemes=[ "K" ], alignEnd=True ) )
        highPrioritySequences = { 'ck' : "K", 'er' : "ER", 'sh' : "SH", 'ai' : "EY", 'au' : "AO",
                                  'oi' : "OY", 'oy' : "OY", 'ng' : "NG", 'ie': "IY", 'ay' : "EY",
                                  'ea' : "IY", 'ch' : "CH", "or" : [ "AO", "R" ], "ur" : "ER", "ou" : "AO",
                                  'ign' : [ "AY", "N" ], 'igm' : [ "AY", "M" ], 'qu' : [ "K", "W" ],
                                  'oa' : "OW", 'ow' : "OW" }
        for l, p in highPrioritySequences.iteritems():
            if p.__class__ != list:
                p = [ p ]
            self.addRule( PronunciationRule( sequence=l, phonemes=p, priority=3 ) )

        #
        # Double consonant sounds
        #
        doubleConsonants = { 'b' : 'B', 'c' : 'S', 'd' : 'D', 'f' : 'F', 'g' : 'G', 'j' : 'JH', 'k' : 'K',
                             'l' : 'L', 'm' : 'M', 'm' : 'N', 'p' : 'P', 'r' : 'R', 's' : 'S', 't' : 'T',
                             'v' : 'V', 'w' : 'W', 'x' : [ 'K', 'S' ], 'z' : 'ZH' }
        for l, p in doubleConsonants.iteritems():
            if p.__class__ != list:
                p = [ p ]
            self.addRule( PronunciationRule( sequence=l+l, phonemes=p, priority=1 ) )

        #
        #
        #
        self.addRule( PronunciationRule( sequence="le", phonemes=[ "AH", "L" ], alignEnd=True ) )

        #
        # silent e patterns
        #
        silentELeadingVowels = { 'a' : 'EY', 'e' : 'IY', 'i' : 'AY', 'o' : 'OW', 'u' : 'UW' }
        silentELinkingNonDefaultConsonants = { 'c' : 'S', 'g' : 'JH' }
        for leadingVowel, vowelSound in silentELeadingVowels.iteritems():
            for linkingConsonant, consonantSound in singleLetterDefaults.iteritems():
                if linkingConsonant in VOWEL_LETTERS:
                    continue
                if linkingConsonant in silentELinkingNonDefaultConsonants.keys():
                    continue
                self.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'e', phonemes=flatten_list( [ vowelSound, consonantSound ] ), alignEnd=True ) )
            for linkingConsonant, consonantSound in silentELinkingNonDefaultConsonants.iteritems():
                self.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'e', phonemes=flatten_list( [ vowelSound, consonantSound ] ), alignEnd=True ) )

        #
        # ing patterns
        #
        for leadingVowel, vowelSound in silentELeadingVowels.iteritems():
            for linkingConsonant, consonantSound in singleLetterDefaults.iteritems():
                if linkingConsonant in VOWEL_LETTERS:
                    continue
                if linkingConsonant in silentELinkingNonDefaultConsonants.keys():
                    continue
                self.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'ing', phonemes=flatten_list( [ vowelSound, consonantSound, 'IH', 'NG' ] ), alignEnd=True ) )
            for linkingConsonant, consonantSound in silentELinkingNonDefaultConsonants.iteritems():
                self.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'ing', phonemes=flatten_list( [ vowelSound, consonantSound, 'IH', 'NG' ] ), alignEnd=True ) )

        #
        # ed patterns
        #
        self.addRule( PronunciationRule( sequence="ed", phonemes=[ "T" ], alignEnd=True ) )
        for leadingVowel, vowelSound in silentELeadingVowels.iteritems():
            for linkingConsonant, consonantSound in singleLetterDefaults.iteritems():
                if linkingConsonant in VOWEL_LETTERS:
                    continue
                if linkingConsonant in silentELinkingNonDefaultConsonants.keys():
                    continue
                if linkingConsonant is "t":
                    self.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'ed', phonemes=flatten_list( [ vowelSound, consonantSound, 'EH', 'D' ] ), alignEnd=True ) )
                else:
                    self.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'ed', phonemes=flatten_list( [ vowelSound, consonantSound, 'T' ] ), alignEnd=True ) )
            for linkingConsonant, consonantSound in silentELinkingNonDefaultConsonants.iteritems():
                self.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'ed', phonemes=flatten_list( [ vowelSound, consonantSound, 'T' ] ), alignEnd=True ) )

        #
        # y at end of word after consonants
        #
        for leadingVowel, vowelSound in silentELeadingVowels.iteritems():
            for linkingConsonant, consonantSound in singleLetterDefaults.iteritems():
                if linkingConsonant in VOWEL_LETTERS:
                    continue
                if linkingConsonant in silentELinkingNonDefaultConsonants.keys():
                    continue
                if linkingConsonant is 'x':
                    continue
                self.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'y', phonemes=flatten_list( [ vowelSound, consonantSound, 'IY' ] ), alignEnd=True ) )
            for linkingConsonant, consonantSound in silentELinkingNonDefaultConsonants.iteritems():
                self.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'y', phonemes=flatten_list( [ vowelSound, consonantSound, 'IY' ] ), alignEnd=True ) )

        #
        # o at end of word after consonants
        #

        #
        # Ending s (z sound after t) without breaking silent e and ing
        #

        #
        # le becomes "AH L"
        #

        #
        # Silent gh
        #
        self.addRule( PronunciationRule( sequence="gh", phonemes=[ "F" ] ) )
        self.addRule( PronunciationRule( sequence="igh", phonemes=[ "AY" ] ) )
        self.addRule( PronunciationRule( sequence="eigh", phonemes=[ "EY" ] ) )

        #
        # Silent k
        #

        #
        # gh and ph as f
        #

        #
        # ea in feathers?
        #

        #
        # ed becomes t after double consonants
        #

        #
        #
        #
        self.addRule( PronunciationRule( sequence="ew", phonemes=[ "UW" ], alignEnd=True ) )

        #
        # AI + ( T or D ) becomes EY, but AI + ( r ) becomes EH
        #

        #
        # Phoneme sound type cases bags -- Z vs IH Z
        #

        #
        # Alternativesx!! Sorted by liklihood
        #
        # ML component:
        #
        # Look at potential syllabifications
        # Find those syllables in other words
        # Vote
        # ????
        #

        self.addRule( PronunciationRule( sequence="ous", phonemes=[ "AH", "S" ], alignEnd=True ) )
        self.addRule( PronunciationRule( sequence="a", phonemes=[ "AH" ], alignEnd=True ) )

    def _pronouncePartial( self, word, startIdx, endIdx ):
        """
        Recursive prnunciation generation call
        """
        for rule in self.rules:
            ret = rule.applyOnce( word, startIdx, endIdx )
            if ret is not None:
                consumedCharsStart, consumedCharsStop, correspondingPhonemes = ret
                if consumedCharsStart > startIdx:
                    if consumedCharsStop < endIdx:
                        return self._pronouncePartial( word, startIdx, consumedCharsStart ) + correspondingPhonemes + self._pronouncePartial( word, consumedCharsStop, endIdx )
                    else:
                        return self._pronouncePartial( word, startIdx, consumedCharsStart ) + correspondingPhonemes
                else:
                    if consumedCharsStop < endIdx:
                        return correspondingPhonemes + self._pronouncePartial( word, consumedCharsStop, endIdx )
                    else:
                        return correspondingPhonemes
            else:
                # We'll try the next one
                pass
        assert( False )

    def pronounce( self, word ):
        """
        Do it.
        """
        return self._pronouncePartial( word, 0, len( word ) )
