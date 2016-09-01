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
