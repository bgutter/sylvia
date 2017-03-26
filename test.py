import sylvia

d = sylvia.PhoneticDictionary( binPath="./cmudict.txt.sylvia" )

print "Words that rhyme with cats:"
print "d.getRhymes( \"cats\" ) = ", d.getRhymes( "cats" )
print

print "Words with the same vowel pattern as bonsai:"
print "d.getVowelMatches( \"bonsai\" ) = ", d.getVowelMatches( "bonsai" )
print

print "Words with 3 syllables, starting with a 'B' sound, and ending with an 'IY' sound followed by any consonant sound:"
print "d.regexSearch( \"B % % IY #\" ) = ", d.regexSearch( "B % % IY #" )
print

print "All pronunciations for orange:"
print "d.findPronunciations( \"orange\" ) = ", d.findPronunciations( "orange" )
