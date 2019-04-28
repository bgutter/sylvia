#
# SylviaEpcServer.py
#
# RPC Server for Emacs-Lisp
#

from Poem import *

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
        return pd.findPronunciations( word )

    @server.register_function
    def infer( word ):
        return pi.pronounce( word )

    @server.register_function
    def rhyme(word, level):
        if level == []:
            level = "default"
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
    def update_poem( poem_text ):
        poem.setText( poem_text )

    @server.register_function
    def poem_syllable_counts():
        return poem.syllableCounts()

    server.print_port()
    server.serve_forever()
