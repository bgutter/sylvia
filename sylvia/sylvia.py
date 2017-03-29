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

class PhoneticDictionary( object ):
    """
    Software API for reading and working with dictionary files
    """

    def __init__( self, textFile=None, binFile=None ):
        """
        Read input file
        """
        if textFile is not None:
            self.load__text( textFile )
        elif binFile is not None:
            self.load__bin( binFile )

    def load__text( self, fin ):
        """
        Read text format dictionary into memory
        """
        self.entries = {}
        for line in fin:
            if line[0:3] == ";;;":
                continue
            parts         = [ x for x in re.split( r"\s+", line ) if len( x ) > 0 ]
            word          = sanitizeWord( parts[0] )
            pronunciation = encodePronunciation( parts[1:] )
            dictListAdd( self.entries, word, pronunciation )

    def load__bin( self, fin ):
        """
        Load binary format dictionary into memory
        """
        self.entries = {}
        buf = fin.read()
        lines = buf.split( "\n" )
        for line in lines:
            if len( line ) == 0:
                continue
            word, pronunciation = line.split( " " )
            dictListAdd( self.entries, word, pronunciation )

    def saveBin( self, outPath ):
        """
        Dump compiled version of dictionary to disk.
        """
        with open( outPath, "wb" ) as fout:
            for word, encodedPronunciations in self.entries.iteritems():
                for encodedPronunciation in encodedPronunciations:
                    fout.write( word + " " + encodedPronunciation + "\n" )
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
        return sorted( list( set( matchingWords ) ) )

    def findPronunciations( self, word ):
        """
        Return a list of pronunciations for word in dictionary
        """
        return [ decodePronunciation( p ) for p in self.entries.get( sanitizeWord( word ), [] ) ]

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
        return sorted( [ x for x in set( ret ) if x != word ] )

    def getVowelMatches( self, word ):
        """
        Returns a list of words which have a similar vowel pattern.
        """
        ret = []
        for pronunciation in self.findPronunciations( word ):
            vowels = [ p for p in pronunciation if isVowelSound( p ) ]
            ret += self.regexSearch( ".*" + "#*".join( vowels ) + ".*" )
        word = sanitizeWord( word )
        return sorted( [ x for x in set( ret ) if x != word ] )

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
