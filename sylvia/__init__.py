import sys
if sys.version_info[0] > 2:
    raise Exception( "Sorry, we're still on Python 2. Version 1.0 of Sylvia will finally move to Python 3." )

from PhonemeDetails import *
from LetterDetails import *
from PronunciationInferencer import *
from PhoneticDictionary import *
from Poem import *
from SylviaConsole import *
from SylviaEpcServer import *
