import pkg_resources

from sylvia import *

if __name__ == "__main__":

    #
    # parse args
    #
    parser = argparse.ArgumentParser()
    parser.add_argument( "-r", "--regex", help="The phonetic regex to use." )
    parser.add_argument( "-l", "--lookup", help="Look up the pronunciation of a word." )
    parser.add_argument( "-y", "--rhyme", help="Find words which rhyme with input." )
    parser.add_argument( "-n", "--near_rhyme", help="Find words which nearly rhyme with input." )
    parser.add_argument( "-v", "--vowel_match", help="Find words with a matching vowel pattern." )
    parser.add_argument( "-e", "--phonaesthetic_map", help="Print a map of euphonious vs cacophonious sounds from a text file." )
    parser.add_argument( "-c", "--optimize_dictionary", help="Compile the dictionary to speed up later queries.")
    parser.add_argument( "-d", "--dictionary_path", help="Point to an alternate dictionary file.")
    args = parser.parse_args()

    #
    # User doesn't know what he/she is doing
    #
    if len( [ x for x in [ args.regex, args.lookup, args.rhyme, args.near_rhyme, args.vowel_match, args.phonaesthetic_map, args.optimize_dictionary ] if x is not None ] ) != 1:
        print "Choose only one action."
        exit()

    #
    # Open dictionary
    #
    if args.dictionary_path:
        if os.path.splitext( args.dictionary_path )[1].upper() == ".TXT":
            with open( args.dictionary_path, "r" ) as f:
                pd = PhoneticDictionary( textFile=f )
        else:
            with open( args.dictionary_path, "rb" ) as f:
                pd = PhoneticDictionary( binFile=f )
    else:
        pd = PhoneticDictionary( binFile=pkg_resources.resource_stream( "sylvia", "cmudict.sylviabin" ) )

    #
    # Act
    #
    if args.optimize_dictionary:
        #
        # Compile the text dictionary to out binary format
        #
        pd.saveBin( args.optimize_dictionary )

    elif args.regex:
        #
        # User wants to lookup words whose pronunciations match the given regex
        #
        for word in pd.regexSearch( args.regex ):
            print word

    elif args.lookup:
        #
        # User wants a list of pronunciations for the given word
        #
        for p in pd.findPronunciations( args.lookup ):
            print " ".join( p )

    elif args.rhyme:
        #
        # User wants words which rhyme with input word
        #
        for word in pd.getRhymes( args.rhyme, near=False ):
            print word

    elif args.near_rhyme:
        #
        # User wants words which rhyme with input word
        #
        for word in pd.getRhymes( args.near_rhyme, near=True ):
            print word

    elif args.vowel_match:
        #
        # Find words with the same vowel pattern
        #
        for word in pd.getVowelMatches( args.vowel_match ):
            print word

    elif args.phonaesthetic_map:
        #
        # Print a euphony/cacophony map
        #
        with open( args.phonaesthetic_map, "r" ) as fin:
            poem = Poem( pd, fin.read() )
            print poem.phonaestheticMap()
