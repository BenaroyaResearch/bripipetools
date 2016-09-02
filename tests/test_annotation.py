import logging
logging.basicConfig(level=logging.INFO)

import pytest
import os
import re

from bripipetools.annotation import illuminaseq

def test_flowcellrunannotator_creation_set_root():
    fcrunannotator = illuminaseq.FlowcellRunAnnotator(
        '150615_D00565_0087_AC6VG0ANXX',
        genomics_root='./tests/test-data/'
    )
    assert(fcrunannotator.flowcellrun._id == '150615_D00565_0087_AC6VG0ANXX')
    assert(re.search('/.*/genomics', fcrunannotator.genomics_path))

def test_flowcellrunannotator_creation_locate_root():
    if os.path.exists('/Volumes/genomics'):
        fcrunannotator = illuminaseq.FlowcellRunAnnotator(
            '150101_D00000_0000_AC00000XX'
        )
        assert(fcrunannotator.flowcellrun._id ==
            '150101_D00000_0000_AC00000XX')
        assert(re.search('/Volumes/genomics', fcrunannotator.genomics_path))
    elif os.path.exists('/mnt/genomics'):
        fcrunannotator = illuminaseq.FlowcellRunAnnotator(
            '150101_D00000_0000_AC00000XX'
        )
        assert(fcrunannotator.flowcellrun._id ==
            '150101_D00000_0000_AC00000XX')
        assert(re.search('/Volumes/genomics', fcrunannotator.genomics_path))
    else: # missing root
        with pytest.raises(AttributeError):
            fcrunannotator = illuminaseq.FlowcellRunAnnotator(
                '150101_D00000_0000_AC00000XX'
            )
            assert(fcrunannotator.flowcellrun._id ==
                '150101_D00000_0000_AC00000XX')
            assert(re.search('/.*/genomics', fcrunannotator.genomics_path))

def test_flowcellrunannotator_get_flowcell_path_test_root():
    fcrunannotator = illuminaseq.FlowcellRunAnnotator(
        '150615_D00565_0087_AC6VG0ANXX',
        genomics_root='./tests/test-data/'
    )
    assert(fcrunannotator._get_flowcell_path() ==
        './tests/test-data/genomics/Illumina/150615_D00565_0087_AC6VG0ANXX')

def test_flowcellrunannotator_get_flowcell_path_invalid_root():
    fcrunannotator = illuminaseq.FlowcellRunAnnotator(
        '150615_D00565_0087_AC6VG0ANXX',
        genomics_root='/mnt'
    )
    with pytest.raises(OSError):
        assert(fcrunannotator._get_flowcell_path())

def test_flowcellrunannotator_get_unaligned_path():
    fcrunannotator = illuminaseq.FlowcellRunAnnotator(
        '150615_D00565_0087_AC6VG0ANXX',
        genomics_root='./tests/test-data/'
    )
    assert(fcrunannotator._get_unaligned_path() ==
        ('./tests/test-data/genomics/Illumina/150615_D00565_0087_AC6VG0ANXX/'
         'Unaligned'))

def test_flowcellrunannotator_get_projects():
    fcrunannotator = illuminaseq.FlowcellRunAnnotator(
        '150615_D00565_0087_AC6VG0ANXX',
        genomics_root='./tests/test-data/'
    )
    assert(len(fcrunannotator.get_projects()) == 8)
    assert('P14-12-23221204' in fcrunannotator.get_projects())
    assert('P109-1-21113094' in fcrunannotator.get_projects())

def test_flowcellrunannotator_get_libraries_set_project():
    fcrunannotator = illuminaseq.FlowcellRunAnnotator(
        '150615_D00565_0087_AC6VG0ANXX',
        genomics_root='./tests/test-data/'
    )
    assert(len(fcrunannotator.get_libraries('P14-12')) == 5)
    assert('lib7293-25920016' in fcrunannotator.get_libraries('P14-12'))

def test_flowcellrunannotator_get_libraries_all_projects():
    fcrunannotator = illuminaseq.FlowcellRunAnnotator(
        '150615_D00565_0087_AC6VG0ANXX',
        genomics_root='./tests/test-data/'
    )
    assert(len(fcrunannotator.get_libraries()) == 36)

def test_sequencedlibraryannotator_creation():
    seqlibannotator = illuminaseq.SequencedLibraryAnnotator(
        ('./tests/test-data/genomics/Illumina/150615_D00565_0087_AC6VG0ANXX/'
         'P14-12-23221204/lib7293-25920016')
    )
    assert(seqlibannotator.path)
