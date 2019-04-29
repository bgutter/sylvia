#
# SylviaEpcServer.py
#
# RPC Server for Emacs-Lisp
#

from Poem import *

def as_ascii( maybeAscii ):
    """
    Until the Python3 conversion, just make it happen.
    """
    if maybeAscii.__class__ == unicode:
        maybeAscii = maybeAscii.encode( "ASCII", "ignore" )
    return maybeAscii

def startEpcServer( pd, pi ):
    """
    Start the Emacs RPC Server.
    """
    from epc.server import EPCServer

    server = EPCServer(('localhost', 0))
    poem = Poem( pd, "" )

    # TODO!!!
    # Merge all of this with SylviaConsole in a
    # SylviaApis class (or something like that)

    @server.register_function
    def lookup( word ):
        return pd.findPronunciations( as_ascii( word ) )

    @server.register_function
    def infer( word ):
        return pi.pronounce( as_ascii( word ) )

    @server.register_function
    def rhyme(word, level):
        if level == []:
            level = "default"
        level = as_ascii( level )
        word = as_ascii( word )
        query = word
        results = None
        if len( pd.findPronunciations( word ) ) == 0:
            pronunciation = pi.pronounce( word )
            query = pronunciation
        if level == "loose":
            results = pd.getVowelMatches( query )
        elif level == "default":
            results = pd.getRhymes( query, near=True )
        elif level == "perfect":
            results = pd.getRhymes( query, near=False )
        else:
            raise ValueError( "Unknown rhyme level {}".format( level ) )
        return results

    @server.register_function
    def regex( phoneme_regex ):
        return pd.regexSearch( as_ascii( phoneme_regex ) )

    @server.register_function
    def update_poem( poem_text ):
        poem.setText( as_ascii( poem_text ) )

    @server.register_function
    def poem_syllable_counts():
        return poem.syllableCounts()

    server.print_port()
    server.serve_forever()
