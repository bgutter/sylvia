#
# Poem.py
#
# Wrap and interface an English text.
#

import re

from PhonemeDetails import *
from LetterDetails import *

WORD_SPLIT_RE = re.compile( "([^a-zA-Z'])" )
WORD_RE       = re.compile( "[a-zA-Z']+" )
NEWLINE_RE    = re.compile( "\n" )

def lookupOrInfer( pd, pi, word ):
    """
    Lookup a word, take the first pronunciation. If not known,
    infer a pronunciation and return that.
    """
    pronunciations = pd.findPronunciations( word )
    if len( pronunciations ) <= 0:
        pronunciation = pi.pronounce( word )
    else:
        pronunciation = pronunciations[ 0 ]
    return pronunciation

class Poem( object ):
    """
    Wraps and analyzes plain text.
    """

    def __init__( self, dictionary, inferencer, sourceText ):
        """
        Create a new Poem from a string.
        """
        self.sourceText = sourceText
        self.pd = dictionary
        self.pi = inferencer
        self.__updateAtlas()

    def getText( self ):
        """
        Return the plain text.
        """
        return self.sourceText

    def setText( self, text ):
        """
        Set the poem text.
        """
        self.sourceText = text
        self.__updateAtlas()

    def phonaestheticMap( self ):
        """
        EXPERIMENTAL
        Prints X for cacophonious sounds, ~ for euphonous sounds, and all
        other whitespace or symbols are retained in-place.
        """
        tokensOut = []
        for token in WORD_SPLIT_RE.split( self.sourceText ):
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

    def syllableCounts( self ):
        """
        Get the number of syllables on each line.
        """
        counts = []
        line_endings = [ m.start() for m in re.finditer( NEWLINE_RE, self.sourceText ) ] + [ len( self.sourceText ) ]
        last_idx = 0
        for nl_idx in line_endings:
            if nl_idx - last_idx == 0:
                counts.append( 0 )
            else:
                phonemes = self.phonemesInRegion( last_idx, nl_idx )
                counts.append( len( [ x for x in phonemes if isVowelSound( x ) ] ) )
            last_idx = nl_idx
        return counts

    def phonemesInRegion( self, begin, end ):
        """
        Get the phonemes associated with the text from character
        index begin to end.
        """
        assert( begin >= 0 and begin <= len( self.sourceText ) )
        assert( end >= 0 and end <= len( self.sourceText ) )
        assert( begin <= end )
        if end > begin:
            pbegin = self.__charToPhonemeIndexMap[ begin ][0]
            pend   = self.__charToPhonemeIndexMap[ max( begin, end - 1 ) ][1]
            return self.__phonemes[ pbegin : pend ]
        return []

    def __updateAtlas( self ):
        """
        Called whenever the buffer is modified.
        Updates the phoneme <-> char mappings.
        """
        #
        # * Naive implementation for now
        #
        # - Each word character maps to the entire phoneme range for
        #   that word.
        #
        # - Each non-word character maps to a zero-length region
        #   between the preceding and following words.
        #
        # - Each phoneme maps to the entire word from which it was
        #   generated
        #
        # TEXT INDEX:     0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28
        # TEXT:          [I     L  I  K  E     C  A  T  S  .  .  .  T  H  E  Y  '  R  E     P  R  E  T  T  Y  !]
        #
        # PHONEME INDEX:   0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
        # PHONEMES:      [AY   L  AY   K   K  AE   T   S  DH  EH   R   P   R  IH   T  IY]
        #
        # ** Text Index (character) to Phoneme Range Map
        # |------------+---------------+--------------+--------------------------|
        # | Text Index | Phoneme Start | Phoneme Stop | Comment                  |
        # |------------+---------------+--------------+--------------------------|
        # |          0 |             0 |            1 | I        --> AY          |
        # |          1 |             1 |            1 | <space>  --> <gap>       |
        # |          2 |             1 |            4 | L        --> L AY K      |
        # |          3 |             1 |            4 | I        --> L AY K      |
        # |          4 |             1 |            4 | K        --> L AY K      |
        # |          5 |             1 |            4 | E        --> L AY K      |
        # |          6 |             4 |            4 | <space>  --> <gap>       |
        # |          7 |             4 |            8 | C        --> K AE T S    |
        # |          8 |             4 |            8 | A        --> K AE T S    |
        # |          9 |             4 |            8 | T        --> K AE T S    |
        # |         10 |             4 |            8 | S        --> K AE T S    |
        # |         11 |             8 |            8 | .        --> <gap>       |
        # |         12 |             8 |            8 | .        --> <gap>       |
        # |         13 |             8 |            8 | .        --> <gap>       |
        # |         14 |             8 |           11 | T        --> DH EH R     |
        # |         15 |             8 |           11 | H        --> DH EH R     |
        # |        ... |           ... |          ... | ...                      |
        # |         27 |            11 |           16 | Y        --> P R IH T IY |
        # |         28 |            16 |           16 | !        --> <gap>       |
        #
        # ** Phoneme Index (single phoneme) to Text Range (substring) Map
        # You get the idea, right?

        # Create the basic mapping objects
        self.__charToPhonemeIndexMap = [ None ] * len( self.sourceText )
        self.__phonemes = []

        # For each word we find, get the phonemes and append them to the list.
        # Set the map index for each of those word characters
        for match in re.finditer( WORD_RE, self.sourceText ):
            print "Found word \"{}\" from {} to {}.".format( match.group(), match.start(), match.end() )
            phonemesForWord = lookupOrInfer( self.pd, self.pi, match.group() )
            phonemeStart = len( self.__phonemes )
            self.__phonemes.extend( phonemesForWord )
            phonemeStop = len( self.__phonemes )
            for i in range( match.start(), match.end() ):
                self.__charToPhonemeIndexMap[ i ] = ( phonemeStart, phonemeStop )

        # Now we need to get rid of the remaining Nones (corresponding to non-word chars)
        # by assigning each to a phoneme gap. We do this by back-filling values.
        backfillVal = len( self.__phonemes )
        for i in range( len( self.__charToPhonemeIndexMap ) - 1, -1, -1 ):
            if self.__charToPhonemeIndexMap[ i ] is None:
                self.__charToPhonemeIndexMap[ i ] = ( backfillVal, backfillVal )
            else:
                backfillVal = self.__charToPhonemeIndexMap[ i ][ 0 ]
