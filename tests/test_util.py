import _mypath
from bripipetools.util import string_ops

def test_to_camel_case_oneword_is_lower():
    assert (string_ops.to_camel_case('oneword') ==
            string_ops.to_camel_case('oneword').lower())

def test_to_camel_case_oneword_no_underscore():
    assert ('_' not in string_ops.to_camel_case('oneword'))

def test_to_camel_case_two_words_no_underscore():
    assert ('_' not in string_ops.to_camel_case('two_words'))

def test_to_camel_case_two_words_is_lower():
    assert (string_ops.to_camel_case('two_words') ==
            string_ops.to_camel_case('two_words').lower())
