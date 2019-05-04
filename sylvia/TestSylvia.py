#
# TestSylvia.py
#
# Unit tests for the Sylvia class
#

import unittest
from SylviaApiWrapper import Sylvia

class TestSylvia( unittest.TestCase ):
    """
    Unit testing for the Sylvia class.
    """

    def verifyPronunciation( self, pronunciation ):
        """
        Complain if this isn't a valid pronunciation.
        """
        self.assertIsInstance( pronunciation, list )
        self.assertTrue( len( pronunciation ) > 0 )
        for phoneme in pronunciation:
            self.assertIsInstance( phoneme, basestring )

    def setUp( self ):
        self.sylvia = Sylvia()

    def test_getPronunciation( self ):
        known_words = {
            "cats":                               [ [ "K", "AE", "T", "S" ] ],
            "dogs":                               [ [ "D", "AA", "G", "Z", ], [ "D", "AO", "G", "Z", ] ],
            "rabbits":                            [ [ "R",  "AE",  "B",  "AH",  "T",  "S" ] ],
            "she's":                              [ [ "SH", "IY", "Z" ] ],
            "supercalifragilisticexpialidocious": [ [ "S", "UW", "P", "ER", "K", "AE", "L", "AH", "F", "R", "AE", "JH", "AH", "L", "IH", "S", "T", "IH", "K", "EH", "K", "S", "P", "IY", "AE", "L", "AH", "D", "OW", "SH", "AH", "S" ] ],
            }

        for word, expectedValues in known_words.items():
            #
            # Test simple case.
            #
            simplePronunciation = self.sylvia.getPronunciation( word )
            self.verifyPronunciation( simplePronunciation )
            self.assertIn( simplePronunciation, expectedValues )

            #
            # Test findAll case
            #
            #retd = self.sylvia.getPronunciation( word, findAll=True )
            #self.assertIsInstance( retd, tuple )
            #self.assertTrue( len( retd ) == 2 )
            #self.

if __name__ == '__main__':
    unittest.main()
