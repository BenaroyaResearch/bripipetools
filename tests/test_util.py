import _mypath
from bripipetools.util import strings
from bripipetools.util import files

# test utility functions in the strings submodule

def test_to_camel_case_oneword_is_lower():
    assert (strings.to_camel_case('oneword') ==
            strings.to_camel_case('oneword').lower())

def test_to_camel_case_oneword_no_underscore():
    assert ('_' not in strings.to_camel_case('oneword'))

def test_to_camel_case_two_words_no_underscore():
    assert ('_' not in strings.to_camel_case('two_words'))

def test_to_camel_case_two_words_not_lower():
    assert (strings.to_camel_case('two_words') !=
            strings.to_camel_case('two_words').lower())

# test utility functions in the files submodule

def test_locate_root_folder():
    assert (files.locate_root_folder('null') == '/dev/')

def test_swap_root_local_globus():
    assert (files.swap_root('/Volumes/genomics/folder', 'genomics') ==
            '/~/genomics/folder')

def test_swap_root_server_globus():
    assert (files.swap_root('/mnt/genomics/folder', 'genomics') ==
            '/~/genomics/folder')

def test_swap_root_local_server():
    assert (files.swap_root('/Volumes/genomics/folder', 'genomics',
                            '/mnt/') ==
            '/mnt/genomics/folder')

def test_swap_root_server_local():
    assert (files.swap_root('/mnt/genomics/folder', 'genomics',
                            '/Volumes/') ==
            '/Volumes/genomics/folder')

# test objects & methods in the files submodule

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
