import logging
import datetime
import os

import pytest
import mongomock
from mock import Mock

from bripipetools import model as docs
from bripipetools import genlims

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_genlims_connection():
    # TODO: come up with a better way to test this
    assert('tg3' in genlims.db.name)
    if os.environ.get('DB_PARAM_FILE') != 'default.ini':
        assert(genlims.db.collection_names())


@pytest.fixture(scope='function')
def mock_db():
    # GIVEN a mocked version of the TG3 Mongo database
    logger.debug(("[setup] mock database, connect "
                  "to mock Mongo database"))

    yield mongomock.MongoClient().db
    logger.debug(("[teardown] mock database, disconnect "
                  "from mock Mongo database"))


@pytest.fixture(scope='function')
def mock_dbobject():
    # GIVEN the definition of a single database object object
    logger.debug("[setup] mock database object")

    yield {'_id': 'mockobject',
           'updateField': 'value',
           'arrayField': ['foo', 'baz']}
    logger.debug("[teardown] mock database object")


@pytest.mark.usefixtures('mock_db')
class TestGenLIMSOperations:
    """
    Tests methods in the ``genlims.operations`` module for interacting
    with the GenLIMS database.
    """
    @pytest.mark.parametrize(
        'dbobject_exists', [False, True]
    )
    def test_find_objects(self, mock_db, mock_dbobject, dbobject_exists):
        # AND the mock database is either empty or contains a mocked
        # collection with a single pre-defined object
        if dbobject_exists:
            mock_db['mockcollection'].insert(mock_dbobject)

        # WHEN the wrapper function `find_objects()` is used to query for
        # objects in a collection
        mock_fn = Mock(name='mock_fn',
                       return_value=(mock_db,
                                     {'_id': mock_dbobject['_id']}))
        mock_fn.__name__ = 'mock_fn'
        wrapped_fn = genlims.find_objects('mockcollection')(mock_fn)
        dbobjects = wrapped_fn()

        # THEN should return a list of objects equal in length to the matching
        # number of objects in the database; if any objects were retrieved,
        # they should include the expected fields and values
        test_query = {'_id': mock_dbobject['_id']}
        assert (type(dbobjects) == list)
        assert (len(dbobjects)
                == mock_db['mockcollection'].find(test_query).count())
        if dbobject_exists:
            assert (dbobjects[0] == mock_dbobject)

    @pytest.mark.parametrize(
        'dbobject_exists', [False, True]
    )
    def test_insert_objects(self, mock_db, mock_dbobject, dbobject_exists):
        # AND the mock database is either empty or contains a mocked
        # collection with a single pre-defined object
        if dbobject_exists:
            mock_db['mockcollection'].insert(mock_dbobject)

        # WHEN an object is inserted into the database (in the mock
        # collection) using the wrapper function `insert_objects()`
        mock_fn = Mock(name='mock_fn',
                       return_value=(mock_db, mock_dbobject))
        mock_fn.__name__ = 'mock_fn'
        wrapped_fn = genlims.insert_objects('mockcollection')(mock_fn)
        wrapped_fn()

        # THEN only the single object be in the database in the mock collection
        # and should match the mock object definition
        test_query = {'_id': mock_dbobject['_id']}
        assert (mock_db['mockcollection'].find(test_query).count() == 1)
        assert (mock_db['mockcollection'].find_one(test_query)
                == mock_dbobject)

    @pytest.mark.parametrize(
        'update_field',
        [
            {'newField': 'value'},
            {'updateField': 'newvalue'},
            {'skipField': None}
        ]
    )
    def test_insert_objects_with_update(self, mock_db, mock_dbobject,
                                        update_field):
        # AND the mock database is contains a mocked collection with
        # a single pre-defined object
        mock_db['mockcollection'].insert(mock_dbobject)

        # AND the local copy of the mock object is updated with either
        # a new field or an updated value of an existing field
        mock_dbobject.update(update_field)

        # WHEN an object with the same ID as the existing object, but with
        # different fields, is inserted into the database (in the mock
        # collection) using the wrapper function `insert_objects()`
        mock_fn = Mock(name='mock_fn',
                       return_value=(mock_db, mock_dbobject))
        mock_fn.__name__ = 'mock_fn'
        wrapped_fn = genlims.insert_objects('mockcollection')(mock_fn)
        wrapped_fn()

        # THEN only the single object should be in the database, all unchanged
        # fields should match the original mock object definition, and new or
        # updated fields should match the expected value; any fields provided
        # in the input object with a value of 'None' should be skipped
        test_query = {'_id': mock_dbobject['_id']}
        test_dbobject = mock_db['mockcollection'].find_one(test_query)
        assert (mock_db['mockcollection'].find(test_query).count() == 1)
        assert (all({test_dbobject[field] == mock_dbobject[field]
                     for field in mock_dbobject.keys()
                     if field not in update_field.keys()}))
        for field, value in update_field.items():
            if value is not None:
                assert(test_dbobject[field] == value)
        assert ('skipField' not in test_dbobject)

    def test_insert_objects_multiple(self, mock_db, mock_dbobject):
        # WHEN inserting the object
        new_dbobject = mock_dbobject.copy()
        new_dbobject['_id'] = 'newmockobject'

        mock_fn = Mock(name='mock_fn',
                       return_value=(mock_db, [mock_dbobject, new_dbobject]))
        mock_fn.__name__ = 'mock_fn'
        wrapped_fn = genlims.insert_objects('mockcollection')(mock_fn)
        wrapped_fn()

        # THEN new objects should be in database
        assert (mock_db['mockcollection'].find().count() == 2)

    @pytest.mark.parametrize(
        'test_collection, test_function',
        [
            ('samples', genlims.get_samples),
            ('runs', genlims.get_runs),
            ('workflowbatches', genlims.get_workflowbatches)
        ]
    )
    def test_wrapped_get_functions(self, mock_db, test_collection, test_function):
        # WHEN using a wrapped get function to query for objects in
        # the specified collection
        logger.debug("test `get_{}()`".format(test_collection))
        test_query = {'_id': 'mockobject'}
        dbobjects = test_function(mock_db, test_query)

        # THEN should return a list of objects equal in length to the matching
        # number of objects in the database for the specified collection
        assert (len(dbobjects)
                == mock_db[test_collection].find(test_query).count())

    @pytest.mark.parametrize(
        'test_collection, test_function',
        [
            ('samples', genlims.put_samples),
            ('runs', genlims.put_runs),
            ('workflowbatches', genlims.put_workflowbatches)
        ]
    )
    def test_wrapped_put_functions(self, mock_db, mock_dbobject,
                                   test_collection, test_function):
        # WHEN using a wrapped put function to insert object(s) into
        # the specified collection
        logger.debug("test `put_{}()`".format(test_collection))
        test_function(mock_db, mock_dbobject)

        # THEN only the single object be in the database in the
        # specified collection
        test_query = {'_id': mock_dbobject['_id']}
        assert (mock_db[test_collection].find(test_query).count() == 1)

    @pytest.mark.parametrize(
        'id_exists', [False, True]
    )
    def test_create_workflowbatch_id_new(self, mock_db, id_exists):
        # AND a prefix/date combination corresponding to the type and date
        # of the workflow batch is either new or already exists in the
        # 'workflowbatches' collection in the database
        if id_exists:
            mock_db.workflowbatches.insert(
                {'_id': 'mockprefix_2000-01-01_1',
                 'date': datetime.datetime(2000, 1, 1, 0, 0)})

        # WHEN creating new workflow batch ID based on a prefix (which
        # corresponds to the type of the workflow batch) and the date on
        # which the workflow batch was run
        wb_id = genlims.create_workflowbatch_id(
            db=mock_db,
            prefix='mockprefix',
            date=datetime.datetime(2000, 1, 1, 0, 0))

        # THEN the constructed workflow batch ID should end in the
        # expected number: 1 if new, or 2 if the same prefix/date combo
        # already existed in the 'workflowbatches' collection
        id_tag = 2 if id_exists else 1
        assert (wb_id == 'mockprefix_2000-01-01_{}'.format(id_tag))

    @pytest.mark.parametrize(
        'field_level', [-1, 0, 1, 2]
    )
    def test_search_ancestors_field(self, mock_db, field_level):
        # AND a hierarchy of objects in the 'samples' collection, with
        # parent relationship specified by the 'parentId' field
        mock_db.samples.insert(
            {'_id': 'sample0', 'parentId': 'sample1'})
        mock_db.samples.insert(
            {'_id': 'sample1', 'parentId': 'sample2'})
        mock_db.samples.update_one(
            {'_id': 'sample{}'.format(field_level)},
            {'$set': {'mockfield': 'mockvalue'}},
            upsert=True)

        # WHEN searching for the field among all sample ancestors in
        # the hierarchy
        value = genlims.search_ancestors(mock_db, 'sample0', 'mockfield')

        # THEN should return the value of the field from whichever level
        # above or equal to the input sample that the field was found; if
        # the field does not exist in any samples in the hierarchy, should
        # return 'None'
        expected_result = 'mockvalue' if field_level >= 0 else None
        assert (value == expected_result)

    def test_search_ancestors_no_parent(self, mock_db):
        # AND a hierarchy of objects in the 'samples' collection, but
        # parent relationship indicator is missing
        mock_db.samples.insert(
            {'_id': 'sample0'})
        mock_db.samples.insert(
            {'_id': 'sample1', 'mockfield': 'mockvalue'})

        # WHEN searching for the field among all sample ancestors in
        # the hierarchy
        value = genlims.search_ancestors(mock_db, 'sample0', 'mockfield')

        # THEN should return None
        assert (value is None)


class TestMapping:
    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            ({'aB': None}, {'a_b': None}),
            ({'aB': [{'bC': None}]}, {'a_b': [{'b_c': None}]}),
            ({'_id': None}, {'_id': None}),
        ]
    )
    def test_map_keys(self, test_input, expected_result):
        # GIVEN any state

        # WHEN camelCase keys/fields in an object are converted to snake_case

        # THEN keys at all nested levels should be converted to snake case
        # (with the exception of '_id', which should be unchangedj)
        assert (genlims.map_keys(test_input) == expected_result)

    def test_get_model_class(self):
        # GIVEN any state

        # WHEN searching for matched model class based on object type

        # THEN should return expected class name
        assert (genlims.get_model_class({'type': 'sequenced library'})
                == 'SequencedLibrary')
        assert (genlims.get_model_class({'type': 'library'})
                == 'Library')

    def test_map_to_object(self):
        # GIVEN any state

        # WHEN mapping a database object to a model class instance
        doc = {'_id': 'lib7293_C6VG0ANXX',
               'parentId': 'lib7293',
               'type': 'sequenced library',
               'rawData': [{'path': None,
                            'laneId': 'L001',
                            'sampleNumber': 1}]}
        obj = genlims.map_to_object(doc)

        # THEN the model class instance should be the correct type and
        # include the appropriately formatted fields/attributes
        # TODO: try to remove dependency on model/docs module when testing,
        # if possible (and maybe even in the method itself)
        assert (type(obj) is docs.SequencedLibrary)
        assert (all([hasattr(obj, field)
                     for field in ['_id', 'parent_id', 'type', 'raw_data',
                                   'date_created', 'last_updated']]))
        assert (all([field in obj.raw_data]
                    for field in ['path', 'lane_id', 'sample_number']))
        assert (obj.last_updated == obj.date_created)
