import pytest

from bripipetools import parsing

def test_get_library_id():
    assert(parsing.get_library_id('lib1234-1234') == 'lib1234')
    assert(parsing.get_library_id('Sample_lib1234') == 'lib1234')
    assert(parsing.get_library_id('Sample1234') == '')

def test_get_project_label_no_subproject():
    assert(parsing.get_project_label('P00Processed') == 'P00')

def test_get_project_label_with_subproject():
    assert(parsing.get_project_label('P00-00Processed') == 'P00-00')

def test_get_project_label_with_basespace_tag():
    assert(parsing.get_project_label('P00-00-0000') == 'P00-00')

# GIVEN any state
def test_parse_project_label():
    # WHEN parsing a project label of format 'P<number>-<number>'
    project_items = parsing.parse_project_label('P1-2')

    # THEN the dictionary should have the first number with key 'project_id'
    # and the second number with key 'subproject_id'
    assert(project_items['project_id'] == 1)
    assert(project_items['subproject_id'] == 2)

# GIVEN any state
def test_parse_flowcell_run_id_standard():
    # WHEN parsing standard Illumina flowcell run ID
    run_id = '150615_D00565_0087_AC6VG0ANXX'
    run_items = parsing.parse_flowcell_run_id(run_id)

    # THEN components should be correctly parsed and assigned to appropriate
    # field in dictionary
    assert(run_items['date'] == '2015-06-15')
    assert(run_items['instrument_id'] == 'D00565')
    assert(run_items['run_number'] == 87)
    assert(run_items['flowcell_id'] == 'C6VG0ANXX')
    assert(run_items['flowcell_position'] == 'A')

# GIVEN any state
def test_parse_fastq_filename():
    # WHEN parsing standard Illumina FASTQ filename
    path = ('tests/test-data/genomics/Illumina/'
            '150615_D00565_0087_AC6VG0ANXX/Unaligned/'
            'P14-12-23221204/lib7293-25920016/'
            'MXU01-CO072_S1_L001_R1_001.fastq.gz')
    fastq_items = parsing.parse_fastq_filename(path)

    # THEN components should be correctly parsed and assigned to appropriate
    # field in dictionary
    assert(fastq_items['path'] == ('/genomics/Illumina/'
                                   '150615_D00565_0087_AC6VG0ANXX/Unaligned/'
                                   'P14-12-23221204/lib7293-25920016/'
                                   'MXU01-CO072_S1_L001_R1_001.fastq.gz'))
    assert(fastq_items['lane_id'] == 'L001')
    assert(fastq_items['read_id'] == 'R1')
    assert(fastq_items['sample_number'] == 1)
