import _mypath
import bripipetools.model as docs

import pytest
import mock

def test_tg3object_creation():
    tg3object = docs.TG3Object(_id='tg3-0000')
    assert(tg3object._id == 'tg3-0000')

def test_sample_creation():
    sample = docs.GenericSample(_id='S0000')
    assert(sample._id == 'S0000')
    assert(sample.parent_id is None)
#
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
