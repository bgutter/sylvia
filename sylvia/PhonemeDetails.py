#
# PhonemeDetails.py
#
# Global details about our phoneme set
#

import string

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

ANY_VOWEL_SOUND_REGEX_TEXT     = "(?:" + "|".join( [ x.encoded() for x in PHONEME_DETAILS__by_text.values() if x.isVowelSound() ] ) + ")"
ANY_CONSONANT_SOUND_REGEX_TEXT = "(?:" + "|".join( [ x.encoded() for x in PHONEME_DETAILS__by_text.values() if not x.isVowelSound() ] ) + ")"
ANY_SYLLABLE_REGEX_TEXT        = "(?:" + ANY_CONSONANT_SOUND_REGEX_TEXT + "*" + ANY_VOWEL_SOUND_REGEX_TEXT + ANY_CONSONANT_SOUND_REGEX_TEXT + "*)"
