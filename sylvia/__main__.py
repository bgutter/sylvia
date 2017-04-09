import argparse

from __init__ import *

if __name__ == "__main__":

    #
    # parse args
    #
    parser = argparse.ArgumentParser()
    parser.add_argument( "-o", "--optimize_dictionary", help="Compile the dictionary to speed up later queries.")
    parser.add_argument( "-d", "--dictionary_path", help="Point to an alternate dictionary file.")
    parser.add_argument( "-w", "--popularity_path", help="Point to an alternate popularity file.")
    parser.add_argument( "-c", "--command", help="Run a one-off command." )
    args = parser.parse_args()

    #
    # Open dictionary
    #
    if args.dictionary_path:
        if os.path.splitext( args.dictionary_path )[1].upper() == ".TXT":
            # Also look for popularity file
            if not args.popularity_path:
                print "If using a text dictionary file, a popularity file is also needed."
                exit()
            with open( args.dictionary_path, "r" ) as f1:
                with open( args.popularity_path, "r" ) as f2:
                    pd = PhoneticDictionary( textFile=f1, wordPopFile=f2 )
        else:
            with open( args.dictionary_path, "rb" ) as f:
                pd = PhoneticDictionary( binFile=f )
    else:
        pd = loadDefaultPhoneticDictionary()

    console = SylviaConsole()
    console.setPhoneticDictionary( pd )

    if args.command:
        #
        # Run a single command
        #
        console.onecmd( args.command )
    else:
        #
        # Interactive console
        #
        console.run()
