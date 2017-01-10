import pytest

from bripipetools import util


class TestStrings:
    """
    Tests basic/wrapper string operations in the
    ``util.strings`` module.
    """
    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            (('foobar', 'foo'), 'foo'),
            (('foobar', 'foo$'), ''),
            (('foobar', 'foo', 'foo'), 'foo'),
        ]
    )
    def test_matchdefault(self, test_input, expected_result):
        # GIVEN any state

        # WHEN a string is searched for a pattern (regular expression) with
        # a specified default return value, in case no match is found
        string = test_input[0]
        pattern = test_input[1]
        if len(test_input) > 2:
            default = test_input[2]
            substring = util.matchdefault(pattern, string, default)
        else:
            substring = util.matchdefault(pattern, string)

        # THEN the output string should match the expected result (i.e., the
        # matched substring, if found, or the default return string otherwise)
        assert (substring == expected_result)

    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            ('oneword', 'oneword'),
            ('two_words', 'twoWords'),
        ]
    )
    def test_to_camel_case(self, test_input, expected_result):
        # GIVEN any state

        # WHEN a string of any format (e.g., lower, snake_case, UPPER, etc.)
        # is converted to camelCase

        # THEN the output string match the expected result (i.e., a camelCase
        # formatted strings with no non-alphanumeric characters and capital
        # letters used to separate words)
        assert (util.to_camel_case(test_input) == expected_result)

    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            ('oneword', 'oneword'),
            ('twoWords', 'two_words'),
        ]
    )
    def test_to_snake_case(self, test_input, expected_result):
        # GIVEN any state

        # WHEN a string of any format (e.g., lower, camelCase, UPPER, etc.)
        # is converted to snake_case

        # THEN the output string match the expected result (i.e., a snake_case
        # formatted strings with all lower-case words separated by underscores)
        assert (util.to_snake_case(test_input) == expected_result)


class TestFiles:
    """
    Tests utility operations for handling files and file paths in the
    ``util.files`` module.
    """
    def test_locate_root_folder(self):
        # GIVEN any state
        # TODO: might actually depend on local system state...

        # WHEN the local filesystem is searched for the root folder
        # (i.e., '/<folder>') that contains a target top level folder
        # (e.g., '/<root folder>/<top level folder>'

        # THEN the output string should be the path to the expected root
        # folder (bounded by path separators)
        assert (util.locate_root_folder('null') == '/dev/')

    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            (('/foo/bar/baz', 'bar'), '/~/bar/baz'),
            (('/foo/bar/baz', 'bar', '/newroot/'), '/newroot/bar/baz'),
            (('bar/baz', 'bar', '/newroot/'), '/newroot/bar/baz'),
            (('/bar/baz', 'bar', '/newroot'), '/newroot/bar/baz'),
        ]
    )
    def test_swap_root(self, test_input, expected_result):
        # GIVEN any state

        # WHEN the root folder in a path is swapped for a specified
        # alternative/dummy string (or the default replacement string,
        # if no alternative is provided)
        path = test_input[0]
        top_level = test_input[1]
        if len(test_input) > 2:
            new_root = test_input[2]
            new_path = util.swap_root(path, top_level, new_root)
        else:
            new_path = util.swap_root(path, top_level)

        # THEN the output string should be the modified path with the
        # original root folder replaced by the alternative string
        assert (new_path == expected_result)


