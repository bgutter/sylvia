#
# SylviaConsole.py
#
# Interactive console for Sylvia
#

import cmd
import shlex
import os
import shlex
import struct
import platform
import subprocess
import sys

from PhoneticDictionary import *
from PronunciationInferencer import *
from Poem import *

def _get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        print "default"
        tuple_xy = (80, 25)      # default value
    return tuple_xy

def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass

def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass

def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])

class SylviaConsole( cmd.Cmd ):
    """
    Simple REPL for using Sylvia.
    """

    #
    # External APIs
    #

    def setPhoneticDictionary( self, pd ):
        """
        Set a PhoneticDictionary externally
        """
        self.pd = pd

    def run( self ):
        """
        Launch
        """
        return self.cmdloop()

    def setConfig( self, *args, **kwargs ):
        """
        Settings for the console
        """
        interactive = kwargs.get( "interactive", False )
        if len( args ) == 0:
            if interactive:
                self.errorMessage( "No configuration option given. Type 'help config' for more information." )
            else:
                assert( False )
        else:
            config = args[0]

            if config == "charwidth":
                if len( args ) != 2:
                    if interactive:
                        self.errorMessage( "charwidth argument needs to be a single integer." )
                    else:
                        assert( False )
                else:
                    w = args[1]
                    if w.__class__ == str:
                        w = int( w )
                    self.settings[ "charwidth" ] = w

            elif config == "inferunknown":
                if len( args ) != 2:
                    if interactive:
                        self.errorMessage( "inferunknown argument needs to be 0/1 or True/False." )
                    else:
                        assert( False )
                else:
                    v = args[1]
                    if v.__class__ == str:
                        if v.lower() == "true" or v == "1":
                            v = True
                        elif v.lower() == "false" or v == "0":
                            v = False
                        else:
                            if interactive:
                                self.errorMessage( "inferunknown argument needs to be 0/1 or True/False." )
                            else:
                                assert( False )
                    elif v.__class__ == int:
                        v = False if int is 0 else True
                    else:
                        if interactive:
                            self.errorMessage( "inferunknown argument needs to be 0/1 or True/False." )
                        else:
                            assert( False )
                        v = None
                    if v is not None:
                        self.settings[ "inferunknown" ] = v

            else:
                self.errorMessage( "Unknown configuration option." )

    #
    # Internal APIs
    #

    def findDefaultCharWidth( self ):
        """
        Figure it out.
        """
        return _get_terminal_size()[0]

    def __init__( self ):
        cmd.Cmd.__init__( self )
        self.prompt = "\nsylvia> "
        self.intro = "\n    Type 'help' for options, press enter to quit."
        self.settings = {}
        self.settings[ "charwidth" ] = self.findDefaultCharWidth()
        self.settings[ "inferunknown" ] = True
        self.poems = {}

    def checkPd( self ):
        """
        Load the package default dictionary if one
        is not set.
        """
        if not hasattr( self, "pd" ):
            self.pd = loadDefaultPhoneticDictionary()

    def checkPi( self ):
        """
        Load the package default PronunciationInferencer
        if one is not set.
        """
        if not hasattr( self, "pi" ):
            self.pi = PronunciationInferencer()

    def tokenizeArgs( self, line ):
        """
        Split it up.
        """
        return shlex.split( line )

    def errorMessage( self, msg ):
        """
        Print an error message.
        """
        print "ERROR:", msg

    def printWords( self, wordList ):
        """
        Print a list of words, according to config.
        """
        if len( wordList ) == 0:
            return
        maxWordLen = max( [ len( w ) for w in wordList ] )
        paddedLen = maxWordLen + 5
        wordList = [ w + " " * ( paddedLen - len( w ) )for w in wordList ]
        charwidth = self.settings[ "charwidth" ]
        perLine = max( 1, int( charwidth ) / paddedLen )
        countThisLine = 0
        for word in wordList:
            sys.stdout.write( word )
            countThisLine += 1
            if countThisLine >= perLine:
                sys.stdout.write( "\n" )
                countThisLine = 0
        if len( wordList ) > 0 and len( wordList ) % perLine != 0:
            sys.stdout.write( "\n" )

    def printPronunciations( self, pronunciationList ):
        """
        Print a list of pronunciations.
        """
        self.printWords( [ " ".join( w ) for w in pronunciationList ] )

    def generateNextHandle( self ):
        """
        Get a unique and convenient name for a poem.
        """
        i = 0
        while True:
            name = "Poem" + str( i )
            if name not in self.poems.keys():
                break
        return name

    #
    # CMD APIs
    #

    def emptyline( self ):
        """
        What happens when no command is entered.
        """
        sys.stdout.write( "\n" )
        return True

    def default( self, arg ):
        """
        Called for unknown commands.
        """
        self.errorMessage( "Unknown command. Type 'help' for help." )

    def do_config( self, arg ):
        """
        Configure the console.

        charwidth    int  - The character width of the console.
        inferunknown bool - When asked to rhyme a word not in the dictionary, whether we
                            should infer a pronunciation.
        """
        args = self.tokenizeArgs( arg )
        self.setConfig( *args, interactive=True )

    def do_lregex( self, arg ):
        """
        Run a traditional character based regex on the words in the current
        PhoneticDictionary.
        """
        self.checkPd()
        args = self.tokenizeArgs( arg )
        if len( args ) != 1:
            self.errorMessage( "Need a single argument -- the regular expression for which to match." )
        else:
            self.printWords( self.pd.letterRegexSearch( args[0] ) )

    def do_regex( self, arg ):
        """
        Run a phonetic regex query on the current PhoneticDictionary.

        Assume a typical Python regular expression, with the following additions:

          * # matches any consonant phoneme
          * @ matches any vowel phoneme
          * % matches any syllable (equivalent to #*@#*)
          * Whitespace is irrelevant and will be removed, but must be used to separate
            consecutive phoneme literals.
          * See cmudict documentation for list of phoneme literals.
          * Full sequence matching is done by default. That is, we automatically add "^"
            to the start of the regex, and "$" at the end. Prepend or append ".*" to your
            regex to override this behavior.

        Try it out:
          regex S IH #*V#* % AH
        """
        self.checkPd()
        args = self.tokenizeArgs( arg )
        if len( args ) == 0:
            self.errorMessage( "Need an argument. Type 'help regex' to learn more." )
        else:
            self.printWords( self.pd.regexSearch( " ".join( args ) ) )

    def do_rhyme( self, arg ):
        """
        Find rhymes for a word. Either give a word, or a rhyme level followed by a
        word. Rhyme level can be one of "loose", "default", or "perfect".

        Try it out:
          rhyme loose lately
          rhyme lately
          rhyme perfect lately
        """
        # TODO inferunknown option
        self.checkPd()
        args = self.tokenizeArgs( arg )
        if not ( 0 < len( args ) < 3 ):
            self.errorMessage( "Bad number of arguments. Type 'help rhyme' for details." )
        else:
            level = "default"
            if len( args ) == 1:
                word = args[0]
            else:
                level, word = args
            results = None

            query = word
            if len( self.pd.findPronunciations( word ) ) == 0:
                if self.settings[ "inferunknown" ]:
                    self.checkPi()
                    pronunciation = self.pi.pronounce( word )
                    query = pronunciation

            results = self.pd.regexSearch( self.pd.getRhymeRegex( query, level ) )
            results = [ r for r in results if r.lower() != word.lower() ]
            if results:
                self.printWords( results )

    def do_popularity( self, arg ):
        """
        Get the popularity for a word.

        Try it out:
          popularity salmon
          popularity google
        """
        self.checkPd()
        args = self.tokenizeArgs( arg )
        if len( args ) != 1:
            self.errorMessage( "Bad number of arguments. Type 'help popularity' for details." )
        else:
            print self.pd.findPopularity( args[0] )

    def do_lookup( self, arg ):
        """
        Lookup the pronunciation of a word in the current PhoneticDictionary.

        Try it out:
          lookup cats
        """
        self.checkPd()
        args = self.tokenizeArgs( arg )
        if len( args ) != 1:
            self.errorMessage( "Bad number of arguments. Type 'help popularity' for details." )
        else:
            self.printPronunciations( self.pd.findPronunciations( args[0] ) )

    def do_infer( self, arg ):
        """
        Infer the pronunciation of a word using magic.

        Try it out:
          infer jabberwocky
        """
        self.checkPi()
        self.printPronunciations( [ self.pi.pronounce( arg ) ] )

    def do_compose( self, arg ):
        """
        Enter a block of multiline text, which will be saved as a Poem.

        Pass the unique handle of the poem, or nothing at all to
        generate one automatically.

        Press ctrl+d on a blank line to complete input.

        Try it out:
          compose poem12
        """
        self.checkPd()
        self.checkPi()
        args = self.tokenizeArgs( arg )
        if len( args ) > 1:
            self.errorMessage( "Bad number of arguments. Send the handle or nothing at all." )
        else:
            if len( args ) == 1:
                handle = args[0]
            else:
                handle = self.generateNextHandle()
            contents = []
            print "\nEnter text. Press ctrl+d on an empty line to save."
            while True:
                try:
                    line = raw_input( "> " )
                except EOFError:
                    break
                contents.append(line)
            contents = "\n".join( contents )
            self.poems[ handle ] = Poem( self.pd, self.pi, contents )
            print "\n\nSaved poem to", handle

    def do_load( self, arg ):
        """
        Load a text file as a Poem

        Pass the path to the text file, and optionally the handle to
        use for the new poem object.

        Try it out:
          load "~/my masterpiece.txt" masterpiece
        """
        self.checkPd()
        args = self.tokenizeArgs( arg )
        if not 0 < len( args ) < 3:
            self.errorMessage( "Bad number of arguments. Type 'help load' for more info." )
        else:
            if len( args ) == 2:
                handle = args[1]
            else:
                handle = self.generateNextHandle()
            with open( args[0], "r" ) as fin:
                self.poems[ handle ] = Poem( self.pd, self.pi, fin.read() )
                print "\nSaved poem to", handle

    def do_show( self, arg ):
        """
        Show a poem. Pass the handle of the poem.
        """
        args = self.tokenizeArgs( arg )
        if len( args ) != 1:
            self.errorMessage( "Need exactly one argument: the name of the poem to show." )
        else:
            handle = args[0]
            if handle not in self.poems:
                self.errorMessage( "Poem not found." )
            else:
                print "\n", self.poems[ handle ].getText()

    def do_euphony( self, arg ):
        """
        Show the phonaesthetic map for a poem. This whole feature is
        kinda stupid, and I'm just using it to test Poem class.
        """
        args = self.tokenizeArgs( arg )
        if len( args ) != 1:
            self.errorMessage( "Need the name of the poem to map." )
        else:
            handle = args[0]
            if handle not in self.poems:
                self.errorMessage( "Poem not found." )
            else:
                print "\n", self.poems[ handle ].phonaestheticMap()

    def do_syllable_counts( self, arg ):
        """
        Show the syllable counts for a poem.
        """
        args = self.tokenizeArgs( arg )
        if len( args ) != 1:
            self.errorMessage( "Need the name of the poem." )
        else:
            handle = args[0]
            if handle not in self.poems:
                self.errorMessage( "Poem not found." )
            else:
                print "\n", " ".join( [ str( x ) for x in self.poems[ handle ].syllableCounts() ] )

    def do_phonemes_in_region( self, arg ):
        """
        Show the phonemes for a region of a poem.
        """
        args = self.tokenizeArgs( arg )
        if len( args ) != 3:
            self.errorMessage( "Need the name of the poem and start and stop indexes." )
        else:
            handle = args[0]
            if handle not in self.poems:
                self.errorMessage( "Poem not found." )
            else:
                print self.poems[ handle ].phonemesInRegion( int( args[1] ), int( args[2] ) )

    def do_test_infer( self, arg ):
        """
        Check the output of our PronunciationInferencer against
        the most popular words in the dictionary.

        Either pass the number of words to test, or no arguments
        for the default of 1000.
        """
        self.checkPi()
        self.checkPd()
        args = self.tokenizeArgs( arg )
        if len( args ) > 1:
            self.errorMessage( "test_infer takes 0 or 1 args: the optional number of words to check." )
            return
        if len( args ) == 1:
            count = int( args[ 0 ] )
        else:
            count= 1000
        hits = 0
        for word in sorted( self.pd.entries.keys(), key=lambda x: -self.pd.findPopularity( x ) )[:count]:
            real = self.pd.findPronunciations( word )
            guess = self.pi.pronounce( word )
            if guess in real:
                hits += 1
            else:
                print "For", word, "we guessed", " ".join( guess ), ", but valid answers are", ",".join( [ " ".join( r ) for r in real ] )
        print hits, "/", count
