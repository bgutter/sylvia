#
# Poem.py
#
# Wrap and interface an English text.
#

from PhonemeDetails import *
from LetterDetails import *

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
