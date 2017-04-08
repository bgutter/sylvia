#
# PhoneticDictionary.py
#
# Interface with the CMU Pronouncing Dictionary to find words
# based on their pronunciation.
#

from PhonemeDetails import *
from LetterDetails import *

import sys
import re
import os
import itertools
import code

def dictListAdd( d, k, v ):
    """
    Maintain a dictionary whose values are lists of values.
    """
    if k not in d:
        d[ k ] = [ v ]
    else:
        d[ k ].append( v )

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
