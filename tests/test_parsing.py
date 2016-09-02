
import pytest

from bripipetools.parsing import illumina

def test_get_lib_id():
    assert(illumina.get_lib_id('lib1234-1234') == 'lib1234')
    assert(illumina.get_lib_id('Sample_lib1234') == 'lib1234')
    assert(illumina.get_lib_id('Sample1234') == '')

def test_get_project_label_no_subproject():
    assert(illumina.get_project_label('P00Processed') == 'P00')

def test_get_project_label_with_subproject():
    assert(illumina.get_project_label('P00-00Processed') == 'P00-00')

def test_get_project_label_with_basespace_tag():
    assert(illumina.get_project_label('P00-00-0000') == 'P00-00')
