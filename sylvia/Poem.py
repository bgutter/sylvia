#
# Poem.py
#
# Wrap and interface an English text.
#

import re

from PhonemeDetails import *
from LetterDetails import *

WORD_SPLIT_RE = re.compile( "([^a-zA-Z'])" )

class Poem( object ):
    """
    Wraps and analyzes plain text.
    """

    def __init__( self, dictionary, sourceText ):
        """
        Create a new Poem from a string.
        """
        # TODO: We really shouldn't need a pd
        self.sourceText = sourceText
        self.pd = dictionary

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
        for line in self.sourceText.splitlines():
            count = 0
            for word in WORD_SPLIT_RE.split( line ):
                pronunciations = self.pd.findPronunciations( word )
                if len( pronunciations ) > 0:
                    # TODO: Using first for now
                    pronunciation = pronunciations[0]
                    for phoneme in pronunciation:
                        if PHONEME_DETAILS__by_text[ phoneme ].isVowelSound():
                            count += 1
            counts.append( count )
        return counts
