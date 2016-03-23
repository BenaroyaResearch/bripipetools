import _mypath
from bripipetools.util import string_ops
from bripipetools.util import files

def test_to_camel_case_oneword_is_lower():
    assert (string_ops.to_camel_case('oneword') ==
            string_ops.to_camel_case('oneword').lower())

def test_to_camel_case_oneword_no_underscore():
    assert ('_' not in string_ops.to_camel_case('oneword'))

def test_to_camel_case_two_words_no_underscore():
    assert ('_' not in string_ops.to_camel_case('two_words'))

def test_to_camel_case_two_words_not_lower():
    assert (string_ops.to_camel_case('two_words') !=
            string_ops.to_camel_case('two_words').lower())

def test_locate_root_folder():
    assert (files.locate_root_folder('usr') == '/usr')

def test_file_repr():
    assert (type(files.SystemFile('test.txt').__repr__()) is str)

def test_file_get_file_ext_file_only():
    assert(files.SystemFile('test.txt').get_file_ext() == 'txt')

def test_file_get_file_ext_full_path():
    assert(files.SystemFile('/path_to_file/folder/test.txt')
           .get_file_ext() == 'txt')

def test_file_get_file_compression_zip():
    assert(files.SystemFile('test.txt.zip')
           .get_file_compression('txt.zip') == 'zip')
