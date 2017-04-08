#
# LetterDetails.py
#
# Global details about english letters
#

import re

DUPLICATE_STRIPPING_REGEX = re.compile( r"(.*)(?:\(\d\))+$" )

VOWEL_LETTERS     = [ "a", "e", "i", "o", "u" ]
CONSONANT_LETTERS = [ chr( i ) for i in range( ord( 'a' ), ord( 'z' ) + 1 ) if chr( i ) not in VOWEL_LETTERS ]

CONSONANT_LETTER_REGEX = "|".join( CONSONANT_LETTERS )
vOWEL_LETTER_REGEX = "|".join( VOWEL_LETTERS )

def sanitizeWord( word ):
    """
    Remove markup and place in a common case.
    """
    needStrip = DUPLICATE_STRIPPING_REGEX.match( word )
    if needStrip:
        word = needStrip.group( 1 )
    return word.capitalize()
