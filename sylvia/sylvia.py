#
# sylvia.py
#
# Interface with the CMU Pronouncing Dictionary to find words
# based on their pronunciation.
#

import string
import sys
import re
import argparse
import os
import itertools
import code

PHONEME_DETAILS__by_text = {}
PHONEME_DETAILS__by_encoded = {}
class PhonemeDetails( object ):
    EUPHONIOUS   = "e"
    CACOPHONIOUS = "c"
    encodedIndex = 0
    def __init__( self, text, isVowel, example, euphony ):
        self.text    = text
        self.index   = PhonemeDetails.encodedIndex
        self.isVowel = isVowel
        self.example = example
        self.euphony = euphony
        self.encodedValue = chr( 128 + self.index )
        PhonemeDetails.encodedIndex += 1
        PHONEME_DETAILS__by_text[ text ] = self
        PHONEME_DETAILS__by_encoded[ self.encodedValue ] = self
    def isVowelSound( self ):
        return self.isVowel
    def encoded( self ):
        return self.encodedValue
    def decoded( self ):
        return self.text
    def isEuphonious( self ):
        return self.euphony == PhonemeDetails.EUPHONIOUS

PhonemeDetails( "AA", True,  "o in odd",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "AE", True,  "a in at",       PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "AH", True,  "u in hut",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "AO", True,  "ou in ought",   PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "AW", True,  "ow in cow",     PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "AY", True,  "i in hide",     PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "B",  False, "b in bee",      PhonemeDetails.CACOPHONIOUS )
PhonemeDetails( "CH", False, "ch in cheese",  PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "D",  False, "d in dog",      PhonemeDetails.CACOPHONIOUS )
PhonemeDetails( "DH", False, "th in thee",    PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "EH", True,  "e in red",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "ER", True,  "ur in hurt",    PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "EY", True,  "a in ate",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "F",  False, "f in fee",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "G",  False, "g in green",    PhonemeDetails.CACOPHONIOUS )
PhonemeDetails( "HH", False, "h in he",       PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "IH", True,  "i in it",       PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "IY", True,  "ee in feet",    PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "JH", False, "j in jay",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "K",  False, "k in key",      PhonemeDetails.CACOPHONIOUS )
PhonemeDetails( "L",  False, "l in law",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "M",  False, "m in me",       PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "N",  False, "n in now",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "NG", False, "ng in ring",    PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "OW", True,  "o in wrote",    PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "OY", True,  "oy in toy",     PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "P",  False, "p in press",    PhonemeDetails.CACOPHONIOUS )
PhonemeDetails( "R",  False, "r in rat",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "S",  False, "s in sea",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "SH", False, "sh in shell",   PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "T",  False, "t in tea",      PhonemeDetails.CACOPHONIOUS )
PhonemeDetails( "TH", False, "th wrath",      PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "UH", True,  "oo in hood",    PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "UW", True,  "oo in toot",    PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "V",  False, "v in victory",  PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "W",  False, "w in what",     PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "Y",  False, "y in year",     PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "Z",  False, "z in zero",     PhonemeDetails.EUPHONIOUS   )
PhonemeDetails( "ZH", False, "z in seizure",  PhonemeDetails.EUPHONIOUS    )

VOWEL_LETTERS     = [ "a", "e", "i", "o", "u" ]
CONSONANT_LETTERS = [ chr( i ) for i in range( ord( 'a' ), ord( 'z' ) + 1 ) if chr( i ) not in VOWEL_LETTERS ]

CONSONANT_LETTER_REGEX = "|".join( CONSONANT_LETTERS )
vOWEL_LETTER_REGEX = "|".join( VOWEL_LETTERS )

def dictListAdd( d, k, v ):
    """
    Maintain a dictionary whose values are lists of values.
    """
    if k not in d:
        d[ k ] = [ v ]
    else:
        d[ k ].append( v )

def isVowelSound( phonemeString ):
    """
    Is this a vowel phoneme?
    """
    return PHONEME_DETAILS__by_text[ phonemeString ].isVowelSound()

def sanitizePhonemeString( phonemeString ):
    """
    Strip emphasis and normalize.
    """
    return phonemeString.translate( None, string.digits ).upper()

def encodePhonemeString( phonemeString ):
    """
    Encode to some character value above 127. This is to keep our encoded values
    outside of the typical ASCII range, and hopefully avoid anyone getting cute with
    the built-in character classes. It's probably a bad, broken, idea, but it seems
    to work fine.
    """
    return PHONEME_DETAILS__by_text[ sanitizePhonemeString( phonemeString ) ].encoded()

def decodePhonemeByte( phonemeByte ):
    """
    Returns the string for this byte.
    """
    return PHONEME_DETAILS__by_encoded[ phonemeByte ].decoded()

def encodePronunciation( pronunciationTokens ):
    """
    Return the encoded version of a pronunciation.
    """
    return "".join( [ encodePhonemeString( p ) for p in pronunciationTokens ] )

def decodePronunciation( pronunciationBuffer ):
    """
    Return the decoded list corresponding to this encoded buffer.
    """
    return [ decodePhonemeByte( x ) for x in pronunciationBuffer ]

DUPLICATE_STRIPPING_REGEX = re.compile( r"(.*)(?:\(\d\))+$" )

def sanitizeWord( word ):
    """
    Remove markup and place in a common case.
    """
    needStrip = DUPLICATE_STRIPPING_REGEX.match( word )
    if needStrip:
        word = needStrip.group( 1 )
    return word.capitalize()

ANY_VOWEL_SOUND_REGEX_TEXT     = "(?:" + "|".join( [ x.encoded() for x in PHONEME_DETAILS__by_text.values() if x.isVowelSound() ] ) + ")"
ANY_CONSONANT_SOUND_REGEX_TEXT = "(?:" + "|".join( [ x.encoded() for x in PHONEME_DETAILS__by_text.values() if not x.isVowelSound() ] ) + ")"
ANY_SYLLABLE_REGEX_TEXT        = "(?:" + ANY_CONSONANT_SOUND_REGEX_TEXT + "*" + ANY_VOWEL_SOUND_REGEX_TEXT + ANY_CONSONANT_SOUND_REGEX_TEXT + "*)"

def preprocessPhoneticRegex( regexTextUnpreprocessed ):
    """
    Perform proper substitutions and fomatting to convert user
    input for regex into one which is Python-compliant, and will
    function on our encoded pronunciations.
    """
    encodedTokens = []
    for token in re.split( "(%|#|@|(?:[^a-zA-Z#@%]+))", regexTextUnpreprocessed ):
        if token == "#":
            encodedTokens.append( ANY_CONSONANT_SOUND_REGEX_TEXT )
            continue
        if token == "@":
            encodedTokens.append( ANY_VOWEL_SOUND_REGEX_TEXT )
            continue
        if token == "%":
            encodedTokens.append( ANY_SYLLABLE_REGEX_TEXT )
            continue
        tryPhoneme = sanitizePhonemeString( token )
        if tryPhoneme in PHONEME_DETAILS__by_text.keys():
            encodedTokens.append( encodePhonemeString( tryPhoneme ) )
            continue
        encodedTokens.append( token.replace( " ", "" ) )
    return "".join( encodedTokens )

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

class PhoneticDictionary( object ):
    """
    Software API for reading and working with dictionary files
    """

    def __init__( self, textFile=None, binFile=None, wordPopFile=None ):
        """
        Read input file
        """
        if textFile is not None and wordPopFile is not None:
            self.load__text( textFile, wordPopFile )
        elif binFile is not None:
            self.load__bin( binFile )
        else:
            #
            # Need either a text phonetic dict and a text popularity map, OR a single bin file
            #
            assert( False )

    def load__text( self, finPhonetic, finPop ):
        """
        Read text format dictionary into memory
        """
        wsre = re.compile( r"\s+" )

        self.entries = {}
        self.popularities = {}

        #
        # Get pronunciations. May be multiple per word
        #
        for line in finPhonetic:
            if line[0:3] == ";;;":
                continue
            parts         = [ x for x in wsre.split( line ) if len( x ) > 0 ]
            word          = sanitizeWord( parts[0] )
            pronunciation = encodePronunciation( parts[1:] )
            dictListAdd( self.entries, word, pronunciation )

        #
        # Get popularities. One for each unique word.
        #
        for line in finPop:
            parts = [ x for x in wsre.split( line ) if len( x ) > 0 ]
            word = sanitizeWord( parts[0] )
            self.popularities[ word ] = int( parts[ 1 ] )

    def load__bin( self, fin ):
        """
        Load binary format dictionary into memory
        """
        self.entries = {}
        self.popularities = {}
        buf = fin.read()
        lines = buf.split( "\n" )
        for line in lines:
            if len( line ) == 0:
                continue
            word, popularity, pronunciation = line.split( " " )
            self.popularities[ word ] = int( popularity )
            dictListAdd( self.entries, word, pronunciation )

    def _inferPronunciationPartial( self, word, startChar, endChar ):
        """
        Infer the pronunciation for this portion of the word.
        """
        if len( word ) == 0:
            return []
        if len( word ) >= 2 and word[-1] == 's' and word[-2] != 's':
            return self._inferPronunciationPartial( word[:-1], 0, len( word ) - 1 ) + [ "Z" if word[-2] is not 't' else "S" ]

        pi = PronunciationInferencer()

        #
        # Single letter defaults ensure we always have
        # Some guess at a pronunciation
        #
        pi.addRule( PronunciationRule( sequence="y", phonemes=[ "IY" ], alignEnd=True ) )
        singleLetterDefaults = { 'a': 'AE', 'b': 'B', 'c': 'K', 'd': 'D', 'e': 'EH', 'f': 'F', 'g': 'G', 'h': 'HH', 'i': 'IH', 'j': 'JH', 'k': 'K',
                                 'l': 'L', 'm': 'M', 'n': 'N', 'o': 'AA', 'p': 'P', 'q': 'K', 'r': 'R', 's': 'S', 't': 'T', 'u': 'AH', 'v': 'V',
                                 'w': 'W', 'x': [ 'K', 'S' ], 'y': 'Y', 'z': 'Z' }
        for l, p in singleLetterDefaults.iteritems():
            if p.__class__ != list:
                p = [ p ]
            pi.addRule( PronunciationRule( sequence=l, phonemes=p, priority=0 ) )

        pi.addRule( PronunciationRule( sequence="ed", phonemes=[ "D" ], alignEnd=True ) )

        #
        # Double vowel sounds
        #
        doubleVowels = { 'a' : 'AE', 'e' : "IY", 'o' : 'UW' }
        for l, p in doubleVowels.iteritems():
            if p.__class__ != list:
                p = [ p ]
            pi.addRule( PronunciationRule( sequence=l+l, phonemes=p, priority=1 ) )

        #
        # Other high priority sequences
        #
        pi.addRule( PronunciationRule( sequence="que", phonemes=[ "K" ], alignEnd=True ) )
        highPrioritySequences = { 'ck' : "K", 'er' : "ER", 'sh' : "SH", 'ai' : "EY", 'au' : "AO",
                                  'oi' : "OY", 'oy' : "OY", 'ng' : "NG", 'ie': "IY", 'ay' : "EY",
                                  'ea' : "IY", 'ch' : "CH", "or" : [ "AO", "R" ], "ur" : "ER", "ou" : "AO",
                                  'ign' : [ "AY", "N" ], 'igm' : [ "AY", "M" ], 'qu' : [ "K", "W" ],
                                  'oa' : "OW" }
        for l, p in highPrioritySequences.iteritems():
            if p.__class__ != list:
                p = [ p ]
            pi.addRule( PronunciationRule( sequence=l, phonemes=p, priority=3 ) )

        #
        # Double consonant sounds
        #
        doubleConsonants = { 'b' : 'B', 'c' : 'S', 'd' : 'D', 'f' : 'F', 'g' : 'G', 'j' : 'JH', 'k' : 'K',
                             'l' : 'L', 'm' : 'M', 'm' : 'N', 'p' : 'P', 'r' : 'R', 's' : 'S', 't' : 'T',
                             'v' : 'V', 'w' : 'W', 'x' : [ 'K', 'S' ], 'z' : 'ZH' }
        for l, p in doubleConsonants.iteritems():
            if p.__class__ != list:
                p = [ p ]
            pi.addRule( PronunciationRule( sequence=l+l, phonemes=p, priority=1 ) )

        #
        #
        #
        pi.addRule( PronunciationRule( sequence="le", phonemes=[ "AH", "L" ], alignEnd=True ) )


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
                pi.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'e', phonemes=flatten_list( [ vowelSound, consonantSound ] ), alignEnd=True ) )
            for linkingConsonant, consonantSound in silentELinkingNonDefaultConsonants.iteritems():
                pi.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'e', phonemes=flatten_list( [ vowelSound, consonantSound ] ), alignEnd=True ) )

        #
        # ing patterns
        #
        for leadingVowel, vowelSound in silentELeadingVowels.iteritems():
            for linkingConsonant, consonantSound in singleLetterDefaults.iteritems():
                if linkingConsonant in VOWEL_LETTERS:
                    continue
                if linkingConsonant in silentELinkingNonDefaultConsonants.keys():
                    continue
                pi.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'ing', phonemes=flatten_list( [ vowelSound, consonantSound, 'IH', 'NG' ] ), alignEnd=True ) )
            for linkingConsonant, consonantSound in silentELinkingNonDefaultConsonants.iteritems():
                pi.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'ing', phonemes=flatten_list( [ vowelSound, consonantSound, 'IH', 'NG' ] ), alignEnd=True ) )

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
                pi.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'y', phonemes=flatten_list( [ vowelSound, consonantSound, 'IY' ] ), alignEnd=True ) )
            for linkingConsonant, consonantSound in silentELinkingNonDefaultConsonants.iteritems():
                pi.addRule( PronunciationRule( sequence=leadingVowel + linkingConsonant + 'y', phonemes=flatten_list( [ vowelSound, consonantSound, 'IY' ] ), alignEnd=True ) )

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
        pi.addRule( PronunciationRule( sequence="gh", phonemes=[ "F" ] ) )
        pi.addRule( PronunciationRule( sequence="igh", phonemes=[ "AY" ] ) )
        pi.addRule( PronunciationRule( sequence="eigh", phonemes=[ "EY" ] ) )

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
        pi.addRule( PronunciationRule( sequence="ew", phonemes=[ "UW" ], alignEnd=True ) )

        #
        # AI + ( T or D ) becomes EY, but AI + ( r ) becomes EH
        #

        #
        # Phoneme sound type cases bags -- Z vs IH Z
        #

        return pi.pronounce( word )

    def getEntries( self ):
        """
        Get a list of all the words in the dictionary.
        """
        return self.entries.keys()

    def sortWordsByPopularity( self, words ):
        """
        Return a closure which sorts words based on their popularity
        as the key function to sorted()
        """
        return sorted( words, key=lambda x: -self.findPopularity( x ) )

    def saveBin( self, outPath ):
        """
        Dump compiled version of dictionary to disk.
        """
        with open( outPath, "wb" ) as fout:
            for word, encodedPronunciations in self.entries.iteritems():
                for encodedPronunciation in encodedPronunciations:
                    # TODO: We actially shouldn't save popularity per-pronunciation, since it's keyed on text. Waste of space.
                    fout.write( word + " " + str( self.findPopularity( word ) ) + " " + encodedPronunciation + "\n" )
        fout.close()

    def regexSearch( self, regexTextUnpreprocessed ):
        """
        Apply phonetic regex to each entry in the dict, returning
        a list of words.
        """
        matchingWords = []
        regex = re.compile( preprocessPhoneticRegex( regexTextUnpreprocessed )  + "$" )
        for word, encodedPronunciations in self.entries.iteritems():
            for encodedPronunciation in encodedPronunciations:
                if regex.match( encodedPronunciation ):
                    matchingWords.append( word )
        return self.sortWordsByPopularity( list( set( matchingWords ) ) )

    def findPronunciations( self, word ):
        """
        Return a list of pronunciations for word in dictionary
        """
        return [ decodePronunciation( p ) for p in self.entries.get( sanitizeWord( word ), [] ) ]

    def findPopularity( self, word ):
        """
        Spit out the popularity for given word.
        """
        return self.popularities.get( sanitizeWord( word ), -1 )

    def getRhymes( self, word, near=False ):
        """
        Return list of words which rhyme with this one.
        """
        ret = []
        for pronunciation in self.findPronunciations( word ):
            mustEndWith = pronunciation[ [ isVowelSound( x ) for x in pronunciation ].index( True ) : ]
            if near:
                ret += self.regexSearch( ".* " + " #*".join( mustEndWith ) + "#*" )
            else:
                ret += self.regexSearch( ".* " + " ".join( mustEndWith ) )
        word = sanitizeWord( word )
        return self.sortWordsByPopularity( [ x for x in set( ret ) if x != word ] )

    def getVowelMatches( self, word ):
        """
        Returns a list of words which have a similar vowel pattern.
        """
        ret = []
        for pronunciation in self.findPronunciations( word ):
            vowels = [ p for p in pronunciation if isVowelSound( p ) ]
            ret += self.regexSearch( ".*" + "#*".join( vowels ) + ".*" )
        word = sanitizeWord( word )
        return self.sortWordsByPopularity( [ x for x in set( ret ) if x != word ] )

    def inferPronunciation( self, word, method="ruleset" ):
        """
        Generate a guess at the pronunciation for this word.
        Can be used as a stopgap for words not in the dictioanry.
        """
        if method == "ruleset":
            return self._inferPronunciationPartial( sanitizeWord( word ).lower(), 0, len( word ) )
        elif method == "ml":
            # TODO
            assert( False )
        return []

class PronunciationRule( object ):
    def __init__( self, *args, **kwargs ):
        self.kwargs = kwargs
        pass
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

    def addRule( self, rule, priorityOver=[] ):
        self.rules = [ rule ] + self.rules

    def dumpModel( self, path ):
        """
        Save model to a file
        """
        pass

    def _pronouncePartial( self, word, startIdx, endIdx ):
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

class Poem( object ):
    """
    Wraps and analyzes plain text.
    """

    def __init__( self, dictionary, sourceText ):
        """
        Create a new Poem from a string.
        """
        self.sourceText = sourceText
        self.pd = dictionary

    def phonaestheticMap( self ):
        """
        EXPERIMENTAL
        Prints X for cacophonious sounds, ~ for euphonous sounds, and all
        other whitespace or symbols are retained in-place.
        """
        tokensOut = []
        for token in re.split( "([^a-zA-Z'])", self.sourceText ):
            pronunciations = self.pd.findPronunciations( token )
            if len( pronunciations ) > 0:
                # TODO: Using first for now
                pronunciation = pronunciations[0]
                for phoneme in pronunciation:
                    if PHONEME_DETAILS__by_text[ phoneme ].isEuphonious():
                        tokensOut.append( "~" )
                    else:
                        tokensOut.append( "X" )
            else:
                tokensOut.append( token )
        return "".join( tokensOut )
