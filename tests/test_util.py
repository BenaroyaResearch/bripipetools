import _mypath
from bripipetools.util import strings
from bripipetools.util import files
from bripipetools.util import ui

import pytest
import mock

# test utility functions in the strings submodule

def test_to_camel_case_oneword():
    assert (strings.to_camel_case('oneword') == 'oneword')

def test_to_camel_case_two_words():
    assert (strings.to_camel_case('two_words') == 'twoWords')

def test_to_snake_case_oneword():
    assert (strings.to_snake_case('oneword') == 'oneword')

def test_to_snake_case_twowords():
    assert (strings.to_snake_case('twoWords') == 'two_words')

# test utility functions in the files submodule

def test_locate_root_folder():
    assert (files.locate_root_folder('null') == '/dev/')

def test_swap_root_default():
    assert (files.swap_root('/foo/bar/baz', 'bar') == '/~/bar/baz')

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

# test objects & methods in the ui submodule

def test_input_to_int_0():
    assert(ui.input_to_int(lambda: "0") == 0)

def test_input_to_int_empty():
    assert(ui.input_to_int(lambda: "") is None)

def test_list_options_a_b(capsys):
    ui.list_options(["a", "b"])
    out, err = capsys.readouterr()
    assert(out == "  0 : a\n  1 : b\n")

def test_prompt_raw_foo(capsys):
    with mock.patch('__builtin__.raw_input', return_value=""):
        ui.prompt_raw("foo")
        out, err = capsys.readouterr()
        assert(err == ("foo\n"))

def test_input_to_int_list_1_2():
    assert(ui.input_to_int_list(lambda: "1,2") == [1, 2])
