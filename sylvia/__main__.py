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
    parser.add_argument( "-c", "--optimize_dictionary", action='store_true', help="Compile the dictionary to speed up later queries.")
    parser.add_argument( "-d", "--dictionary_path", help="Point to an alternate dictionary file.")
    args = parser.parse_args()

    #
    # User doesn't know what he/she is doing
    #
    if args.lookup and args.regex and args.rhyme:
        print "Choose only one action: regex, lookup, or rhyme."
        exit()

    #
    # Find the dictionary path
    #
    if args.dictionary_path:
        dictPath = args.dictionary_path
    else:
        if os.path.exists( "./cmudict.txt.sylvia" ):
            dictPath = "./cmudict.txt.sylvia"
        elif os.path.exists( "./cmudict.txt" ):
            dictPath = "./cmudict.txt"
        else:
            print "No dictionary path given, cmudict not found in working directory."
            exit()

    if args.optimize_dictionary:
        #
        # Compile the text dictionary to out binary format
        #
        dictPath = PhoneticDictionary( dictPath ).saveBin()

    if args.regex:
        #
        # User wants to lookup words whose pronunciations match the given regex
        #
        for word in openDictionary( dictPath ).regexSearch( args.regex ):
            print word

    elif args.lookup:
        #
        # User wants a list of pronunciations for the given word
        #
        for p in lookupPronunciation( dictPath, args.lookup ):
            print " ".join( p )

    elif args.rhyme:
        #
        # User wants words which rhyme with input word
        #
        for word in openDictionary( dictPath ).getRhymes( args.rhyme, near=False ):
            print word

    elif args.near_rhyme:
        #
        # User wants words which rhyme with input word
        #
        for word in openDictionary( dictPath ).getRhymes( args.near_rhyme, near=True ):
            print word

    elif args.vowel_match:
        #
        # Find words with the same vowel pattern
        #
        for word in openDictionary( dictPath ).getVowelMatches( args.vowel_match ):
            print word
