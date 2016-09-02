import _mypath
import bripipetools.model as docs

import pytest
import mock

def test_convert_keys():
    assert(docs.convert_keys({'a_b': None}) == {'aB': None})
    assert(docs.convert_keys({'a_b': [{'b_c': None}]}) ==
        {'aB': [{'bC': None}]})
    assert(docs.convert_keys({'_id': None}) == {'_id': None})

def test_tg3object_creation():
    tg3object = docs.TG3Object(_id='tg3-0000')
    assert(tg3object._id == 'tg3-0000')
    assert(tg3object.type is None)
    assert(tg3object.date_created is None)

def test_tg3object_to_json():
    tg3object = docs.TG3Object(_id='tg3-0000')
    assert(tg3object.to_json() ==
        {'_id': 'tg3-0000',
         'type': None,
         'dateCreated': None})

def test_genericsample_creation():
    sample = docs.GenericSample(_id='S0000')
    assert(sample._id == 'S0000')
    assert(sample.project_id is None)
    assert(sample.subproject_id is None)
    assert(sample.protocol_id is None)
    assert(sample.parent_id is None)

def test_genericsample_to_json():
    sample = docs.GenericSample(_id='S0000')
    assert(sample.to_json() ==
        {'_id': 'S0000',
         'type': None,
         'dateCreated': None,
         'projectId': None,
         'subprojectId': None,
         'protocolId': None,
         'parentId': None})

def test_library_creation():
    library = docs.Library(_id='lib0000', parent_id='S0000')
    assert(library._id == 'lib0000')
    assert(library.type == 'library')
    assert(library.parent_id == 'S0000')

def test_sequencedlibrary_creation():
    seqlibrary = docs.SequencedLibrary(_id='lib0000_C000000XX',
                                       parent_id='lib0000')
    assert(seqlibrary._id == 'lib0000_C000000XX')
    assert(seqlibrary.type == 'sequenced library')
    assert(seqlibrary.parent_id == 'lib0000')
    assert(seqlibrary.run_id is None)
    assert(seqlibrary.raw_data == [])

def test_sequencedlibrary_set_raw_data():
    seqlibrary = docs.SequencedLibrary(_id='lib0000_C000000XX',
                                       parent_id='lib0000')
    seqlibrary.raw_data = [{'path': None}]
    assert(len(seqlibrary.raw_data))

def test_sequencedlibrary_to_json():
    seqlibrary = docs.SequencedLibrary(_id='lib0000_C000000XX',
                                       parent_id='lib0000')
    seqlibrary_json = seqlibrary.to_json()
    assert('rawData' in seqlibrary_json)

def test_genericrun_creation():
    run = docs.GenericRun(_id='0000')
    assert(run._id == '0000')
    assert(run.date is None)

def test_flowcellrun_creation():
    flowcellrun = docs.FlowcellRun(_id='150101_D00000_0000_AC00000XX')
    assert(flowcellrun._id == '150101_D00000_0000_AC00000XX')
    assert(flowcellrun.date == '2015-01-01')
    assert(flowcellrun.instrument_id == 'D00000')
    assert(flowcellrun.run_number == 0)
    assert(flowcellrun.flowcell_id == 'C00000XX')
    assert(flowcellrun.flowcell_position == 'A')

def test_flowcellrun_set_flowcell_path():
    flowcellrun = docs.FlowcellRun(_id='150101_D00000_0000_AC00000XX')
    flowcellrun.flowcell_path = ('/~/genomics/Illumina/'
                                 '150101_D00000_0000_AC00000XX')
    assert(flowcellrun.flowcell_path == ('/~/genomics/Illumina/'
                                         '150101_D00000_0000_AC00000XX'))
