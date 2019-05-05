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
        """
        Create the Sylvia object.
        """
        self.sylvia = Sylvia()

    def test_getPronunciationKnown( self ):
        """
        Test Sylvia.getPronunciation() for words in the dictionary.
        """
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
            retd = self.sylvia.getPronunciation( word, findAll=True )
            self.assertIsInstance( retd, tuple )
            self.assertTrue( len( retd ) == 2 )
            lookups, pronounced = retd
            self.verifyPronunciation( pronounced )
            self.assertIsInstance( lookups, list )
            self.assertEqual( len( lookups ), len( expectedValues ) )
            for p in lookups:
                self.verifyPronunciation( p )
                self.assertIn( p, expectedValues )

    def test_getPronunciationUnknown( self ):
        """
        Test Sylvia.getPronunciation() for words not in the dictionary.
        """
        unknown_words = [ "rafloy", "she'sd", "fihlbart" ]

        for word in unknown_words:
            #
            # Test simple case
            #
            simplePronunciation = self.sylvia.getPronunciation( word )
            self.verifyPronunciation( simplePronunciation )

            #
            # Test findAll case
            #
            retd = self.sylvia.getPronunciation( word, findAll=True )
            self.assertIsInstance( retd, tuple )
            self.assertTrue( len( retd ) == 2 )
            lookups, pronounced = retd
            self.verifyPronunciation( pronounced )
            self.assertIsInstance( lookups, list )
            self.assertEqual( len( lookups ), 0 )
            for p in lookups:
                self.verifyPronunciation( p )

    def test_getPhoneticRegex_word( self ):
        """
        Test Sylvia.getPhoneticRegex() with words as input
        """
        words = [ "cat", "Saturday", "she'sd" ]

        for word in words:
            for pattern in self.sylvia.phoneticPatterns:
                regex = self.sylvia.generatePhoneticRegex( word, pattern )
                self.assertIsInstance( regex, list )
                # TODO check contents once we have linting

    def test_getPhoneticRegex_pronunciation( self ):
        """
        Test Sylvia.getPhoneticRegex() with pronunciations as input
        """
        words = [ [ "K", "AE", "T" ], [ "SH", "EH", "S", "D" ] ]

        for word in words:
            for pattern in self.sylvia.phoneticPatterns:
                regex = self.sylvia.generatePhoneticRegex( word, pattern )
                self.assertIsInstance( regex, basestring )
                # TODO check contents once we have linting

if __name__ == '__main__':
    unittest.main()
