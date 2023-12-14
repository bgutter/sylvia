"""
quick tests yet to be refactored
"""

from sylvia.PhonemeDetails import sanitizePhonemeString
from sylvia.PhoneticDictionary import loadDefaultPhoneticDictionary


def test_sanitaize():
    "py3 updated: 1 param translate, need maketrans"
    assert sanitizePhonemeString("1hello2") == "HELLO"


def test_pronunciation():
    "py3 update: use chr() for key"
    pd = loadDefaultPhoneticDictionary()
    assert pd.findPronunciations("hello") == [
        ["HH", "AH", "L", "OW"],
        ["HH", "EH", "L", "OW"],
    ]
