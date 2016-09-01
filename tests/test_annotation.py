
import re

from bripipetools.annotation import flowcell

def test_flowcellrunannotator_creation():
    fcrunannotator = flowcell.FlowcellRunAnnotator(
        '150101_D00000_0000_AC00000XX'
    )
    assert(fcrunannotator.flowcellrun._id == '150101_D00000_0000_AC00000XX')
    assert(re.search('/.*/genomics', fcrunannotator.genomics_root))

def test_flowcellrunannotator_get_flowcell_path():
    fcrunannotator = flowcell.FlowcellRunAnnotator(
        '150615_D00565_0087_AC6VG0ANXX'
    )
    assert(fcrunannotator._get_flowcell_path() ==
        '/Volumes/genomics/Illumina/150615_D00565_0087_AC6VG0ANXX')
