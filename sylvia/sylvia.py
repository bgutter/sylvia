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

PHONEME_TABLE = [ "AA", "AE", "AH", "AO", "AW", "AY", "B", "CH", "D", "DH", "EH", "ER", "EY", "F", "G",
                  "HH", "IH", "IY", "JH", "K", "L", "M", "N", "NG", "OW", "OY", "P", "R", "S", "SH", "T",
                  "TH", "UH", "UW", "V", "W", "Y", "Z", "ZH" ]

VOWELS = [ "AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW" ]

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
    return phonemeString in VOWELS

def sanitizePhonemeString( phonemeString ):
    """
    Strip emphasis and normalize.
    """
    return phonemeString.translate( None, string.digits ).upper()

def encodePhonemeString( phonemeString ):
    """
    Encode to some character value above 127. This is to keep out encoded values
    outside of the typical ASCII range, and hopefully avoid anyone getting cute with
    the built-in character classes. It's probably a bad, broken, idea, but it seems
    to work fine.
    """
    return chr( 128 + PHONEME_TABLE.index( sanitizePhonemeString( phonemeString ) ) )

def decodePhonemeByte( phonemeByte ):
    """
    Returns the string for this byte.
    """
    return sanitizePhonemeString( PHONEME_TABLE[ ord( phonemeByte ) - 128 ] )

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

ANY_VOWEL_SOUND_REGEX_TEXT     = "(?:" + "|".join( [ encodePhonemeString( x ) for x in VOWELS ] ) + ")"
ANY_CONSONANT_SOUND_REGEX_TEXT = "(?:" + "|".join( [ encodePhonemeString( x ) for x in PHONEME_TABLE if x not in VOWELS ] ) + ")"
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
        if tryPhoneme in PHONEME_TABLE:
            encodedTokens.append( encodePhonemeString( tryPhoneme ) )
            continue
        encodedTokens.append( token.replace( " ", "" ) )
    return "".join( encodedTokens )

class PhoneticDictionary( object ):
    """
    Software API for reading and working with dictionary files
    """

    def __init__( self, textPath=None, binPath=None ):
        """
        Set up out backend.
        """
        if textPath == binPath:
            assert( False )
        elif textPath is not None:
            self.path = textPath
            self.load__text( textPath )
        else:
            self.path = binPath
            self.load__bin( binPath )

    def load__text( self, path ):
        """
        Read text format dictionary into memory
        """
        self.entries = {}
        with open( path, "r" ) as fin:
            for line in fin:
                if line[0:3] == ";;;":
                    continue
                parts         = [ x for x in re.split( r"\s+", line ) if len( x ) > 0 ]
                word          = sanitizeWord( parts[0] )
                pronunciation = encodePronunciation( parts[1:] )
                dictListAdd( self.entries, word, pronunciation )

    def load__bin( self, path ):
        """
        Load binary format dictionary into memory
        """
        self.entries = {}
        with open( path, "rb" ) as fin:
            buf = fin.read()
            lines = buf.split( "\n" )
            for line in lines:
                if len( line ) == 0:
                    continue
                word, pronunciation = line.split( " " )
                dictListAdd( self.entries, word, pronunciation )

    def saveBin( self ):
        """
        Dump compiled version of dictionary to disk.
        """
        outPath = self.path + ".sylvia"
        with open( outPath, "wb" ) as fout:
            for word, encodedPronunciations in self.entries.iteritems():
                for encodedPronunciation in encodedPronunciations:
                    fout.write( word + " " + encodedPronunciation + "\n" )
        fout.close()
        return outPath

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

def openDictionary( path ):
    """
    Determine whether this is a text of binary dictionary, open, and
    return it.
    """
    if os.path.splitext( path )[1].upper() == ".TXT":
        return PhoneticDictionary( textPath=path )
    else:
        return PhoneticDictionary( binPath=path )

def lookupPronunciation( dictPath, word ):
    """
    Return a list of phonemes for a word. None if not found.
    """
    return openDictionary( dictPath ).findPronunciations( word )
