# import _mypath
from bripipetools import util

import pytest
import mock

# test utility functions in the strings submodule

def test_to_camel_case_oneword():
    assert (util.to_camel_case('oneword') == 'oneword')

def test_to_camel_case_two_words():
    assert (util.to_camel_case('two_words') == 'twoWords')

def test_to_snake_case_oneword():
    assert (util.to_snake_case('oneword') == 'oneword')

def test_to_snake_case_twowords():
    assert (util.to_snake_case('twoWords') == 'two_words')

# test utility functions in the files submodule

def test_locate_root_folder():
    assert (util.locate_root_folder('null') == '/dev/')

def test_swap_root_default():
    assert (util.swap_root('/foo/bar/baz', 'bar') == '/~/bar/baz')

# test objects & methods in the files submodule

def test_file_repr():
    assert (type(util.SystemFile('test.txt').__repr__()) is str)

def test_file_get_file_ext_file_only():
    assert(util.SystemFile('test.txt').get_file_ext() == 'txt')

def test_file_get_file_ext_full_path():
    assert(util.SystemFile('/path_to_file/folder/test.txt')
           .get_file_ext() == 'txt')

def test_file_get_file_compression_zip():
    assert(util.SystemFile('test.txt.zip')
           .get_file_compression('txt.zip') == 'zip')

# test objects & methods in the ui submodule

def test_input_to_int_0():
    assert(util.input_to_int(lambda: "0") == 0)

def test_input_to_int_empty():
    assert(util.input_to_int(lambda: "") is None)

def test_list_options_a_b(capsys):
    util.list_options(["a", "b"])
    out, err = capsys.readouterr()
    assert(out == "  0 : a\n  1 : b\n")

def test_prompt_raw_foo(capsys):
    with mock.patch('__builtin__.raw_input', return_value=""):
        util.prompt_raw("foo")
        out, err = capsys.readouterr()
        assert(err == ("foo\n"))

def test_input_to_int_list_1_2():
    assert(util.input_to_int_list(lambda: "1,2") == [1, 2])
