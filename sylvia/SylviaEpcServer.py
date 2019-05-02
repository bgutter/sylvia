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
    poem = Poem( pd, pi, "" )

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
    def rhyme_levels():
        return pd.getRhymeLevels()

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
        results = pd.regexSearch( pd.getRhymeRegex( query, level ) )
        return [ r for r in results if r.lower() != word.lower() ]

    @server.register_function
    def regex( phoneme_regex ):
        return pd.regexSearch( as_ascii( phoneme_regex ) )

    @server.register_function
    def update_poem( poem_text ):
        poem.setText( as_ascii( poem_text ) )

    @server.register_function
    def poem_syllable_counts():
        return poem.syllableCounts()

    @server.register_function
    def poem_phonemes_in_region( begin, end ):
        return poem.phonemesInRegion( begin, end )

    server.print_port()
    server.serve_forever()
