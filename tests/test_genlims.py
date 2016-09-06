import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import os
import re
import pytest
import mongomock

from bripipetools import genlims

def test_genlims_connection():
    # TODO: come up with a better way to test this
    assert('samples' in genlims.db.collection_names())

@pytest.fixture(scope='function')
def mock_db(request):
    logger.info(("[setup] mock 'tg3' database, connect "
                 "to mock 'tg3' Mongo database"))
    db = mongomock.MongoClient().db
    db.samples.insert(
        {"_id": "lib7293",
    	"projectId": 14,
    	"projectName": "U01-Mexico 2011",
    	"sampleId": "S2733",
    	"libraryId": "lib7293",
    	"parentId": "grRNA5942",
    	"type": "library"}
    )
    db.runs.insert(
        {"_id": "150615_D00565_0087_AC6VG0ANXX",
        "date": "2015-06-15",
    	"instrumentId": "D00565",
    	"runNumber": 87,
    	"flowcellId": "C6VG0ANXX",
    	"flowcellPosition": "A",
    	"type": "flowcell"}
    )
    def fin():
        logger.info(("[teardown] mock 'tg3' database, disconnect "
                     "from mock 'tg3' Mongo database"))
    request.addfinalizer(fin)
    return db

@pytest.mark.usefixtures('mock_db')
class TestGenLIMSGMethodsWithMockDB:

    # GIVEN a mocked version of the TG3 Mongo database with example documents

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

    def test_put_samples_one_sample(self, mock_db):
        logger.info("test `put_samples()`, one sample")

        # WHEN inserting one new sample
        samples = [{'_id': 'lib0000', 'type': 'library'}]
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
        logger.info("test `put_samples()`, multiple runs")

        # WHEN inserting three new runs
        runs = [{'_id': 'r000{}'.format(i), 'type': 'test run'}
                for i in range(3)]
        genlims.put_runs(mock_db, runs)

        # THEN the 3 new runs should be in database
        assert(mock_db.runs.find_one({'_id': 'r0000'}))
        assert(len(list(mock_db.runs.find({'type': 'test run'}))) == 3)
