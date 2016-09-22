import logging
import os
import re

import pytest
from mock import Mock

from bripipetools import model as docs
from bripipetools import genlims

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# def test_genlims_connection():
#     # TODO: come up with a better way to test this
#     assert('samples' in genlims.db.collection_names())

@pytest.mark.usefixtures('mock_db')
class TestGenLIMSGMethodsWithMockDB:

    # GIVEN a mocked version of the TG3 Mongo database with example documents

    def test_find_objects_exist(self, mock_db):
        logger.info("test `find_objects()` when objects exist")

        # WHEN querying for an object that exists in the database
        mock_fn = Mock(name='mock_fn',
                       return_value=(mock_db, {'_id': 'lib7293'}))
        mock_fn.__name__ = 'mock_fn'
        wrapped_fn = genlims.find_objects('samples')(mock_fn)
        objects = wrapped_fn()

        # THEN should return a non-empty list
        assert(len(objects))

    def test_find_objects_new(self, mock_db):
        logger.info("test `find_objects()` when objects do not exist")

        # WHEN querying for an object that does not exist in the database
        mock_fn = Mock(name='mock_fn',
                       return_value=(mock_db, {'_id': 'foo'}))
        mock_fn.__name__ = 'mock_fn'
        wrapped_fn = genlims.find_objects('samples')(mock_fn)
        objects = wrapped_fn()

        # THEN should return an empty list
        assert(len(objects) == 0)

    # TODO: test insert objects

    def test_get_samples(self, mock_db):
        logger.info("test `get_samples()`")

        # WHEN querying with a known sample ID
        query = {'_id': 'lib7293'}

        # THEN ...
        assert(genlims.get_samples(mock_db, query)[0]['_id'] == 'lib7293')

    def test_get_runs(self, mock_db):
        logger.info("test `get_runs()`")

        # WHEN querying with a known run ID
        query = {'_id': '150615_D00565_0087_AC6VG0ANXX'}

        # THEN ...
        assert(genlims.get_runs(mock_db, query)[0]['_id'] ==
            '150615_D00565_0087_AC6VG0ANXX')

    def test_get_workflowbatches(self, mock_db):
        logger.info("test `get_workflowbatches()`")

        # WHEN querying with a known workflow batch ID
        query = {'_id': 'globusgalaxy_2016-04-12_1'}

        # THEN ...
        assert(genlims.get_workflowbatches(mock_db, query)[0]['_id'] ==
            'globusgalaxy_2016-04-12_1')

    def test_get_workflowbatches_regex(self, mock_db):
        logger.info("test `get_workflowbatches()`, regex")

        # WHEN querying with a workflow batch ID regular expression
        query = {'_id': {'$regex': 'globusgalaxy_2016-04-12_'}}

        # THEN ...
        assert(genlims.get_workflowbatches(mock_db, query)[0]['_id'] ==
            'globusgalaxy_2016-04-12_1')

    def test_put_samples_one_sample(self, mock_db):
        logger.info("test `put_samples()`, one sample")

        # WHEN inserting one new sample
        samples = {'_id': 'lib0000', 'type': 'library'}
        genlims.put_samples(mock_db, samples)

        # THEN new sample should be in database
        assert(mock_db.samples.find_one({'_id': 'lib0000'}))

    def test_put_samples_multiple_samples(self, mock_db):
        logger.info("test `put_samples()`, multiple samples")

        # WHEN inserting three new samples
        samples = [{'_id': 't000{}'.format(i), 'type': 'test lib'}
                   for i in range(3)]
        genlims.put_samples(mock_db, samples)

        # THEN the 3 new samples should be in database
        assert(mock_db.samples.find_one({'_id': 't0000'}))
        assert(len(list(mock_db.samples.find({'type': 'test lib'}))) == 3)

    def test_put_runs_multiple_runs(self, mock_db):
        logger.info("test `put_runs()`, multiple runs")

        # WHEN inserting three new runs
        runs = [{'_id': 'r000{}'.format(i), 'type': 'test run'}
                for i in range(3)]
        genlims.put_runs(mock_db, runs)

        # THEN the 3 new runs should be in database
        assert(mock_db.runs.find_one({'_id': 'r0000'}))
        assert(len(list(mock_db.runs.find({'type': 'test run'}))) == 3)

    def test_put_workflowbatches_multiple_workflowbatches(self, mock_db):
        logger.info("test `put_workflowbatches()`, multiple workflow batches")

        # WHEN inserting three new workflow batches
        workflowbatches = [{'_id': 'wb000{}'.format(i),
                            'type': 'test workflow batch'}
                for i in range(3)]
        genlims.put_workflowbatches(mock_db, workflowbatches)

        # THEN the 3 new workflowbatches should be in database
        assert(mock_db.workflowbatches.find_one({'_id': 'wb0000'}))
        assert(len(list(mock_db.workflowbatches.find(
            {'type': 'test workflow batch'}
            ))) == 3)

    def test_create_workflowbatch_id_existing_date(self, mock_db):
        logger.info("test `create_workflowbatch_id()`, existing date")

        # WHEN creating new workflow batch ID with prefix 'globus' and
        # date '2016-04-12' - an existing prefix/date combination
        wb_id = genlims.create_workflowbatch_id(
            mock_db, 'globusgalaxy', '2016-04-12'
        )

        # THEN constructed workflow batch ID should end in number 2
        assert(wb_id == 'globusgalaxy_2016-04-12_2')

    def test_create_workflowbatch_id_new_date(self, mock_db):
        logger.info("test `create_workflowbatch_id()`, new date")

        # WHEN creating new workflow batch ID with prefix 'globus' and
        # date '2016-04-12' - an new prefix/date combination
        mock_db.workflowbatches.delete_one(
            {'_id': 'globusgalaxy_2016-04-12_1'}
        )
        wb_id = genlims.create_workflowbatch_id(
            mock_db, 'globusgalaxy', '2016-04-12'
        )

        # THEN constructed workflow batch ID should end in number 1
        assert(wb_id == 'globusgalaxy_2016-04-12_1')

class TestMapping:
    # GIVEN any state

    def test_map_keys(self):
        logger.info("test `map_keys()`")

        assert(genlims.map_keys({'aB': None}) == {'a_b': None})
        assert(genlims.map_keys({'aB': [{'bC': None}]}) ==
            {'a_b': [{'b_c': None}]})
        assert(genlims.map_keys({'_id': None}) == {'_id': None})

    def test_get_class(self):

        assert(genlims.get_class({'type': 'sequenced library'}) ==
            'SequencedLibrary')

    def test_map_to_object(self):
        doc = {'_id': 'lib7293_C6VG0ANXX',
               'parentId': 'lib7293',
               'type': 'sequenced library',
               'rawData': [{'path': None,
                            'laneId': 'L001',
                            'sampleNumber': 1}]}
        obj = genlims.map_to_object(doc)
        assert(type(obj) is docs.SequencedLibrary)
        assert(hasattr(obj, '_id'))
        assert(obj._id == 'lib7293_C6VG0ANXX')
        assert(obj.parent_id == 'lib7293')
        assert(obj.type == 'sequenced library')
        assert(obj.raw_data == [{'path': None,
                                 'lane_id': 'L001',
                                 'sample_number': 1}])
