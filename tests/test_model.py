import logging
import operator

import pytest

from bripipetools import model as docs

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestDocumentsMethods:
    """
    Tests standalone methods related to the base data model used in
    GenLIMS and bioinformatics pipelines.
    """
    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            ({'a_b': None}, {'aB': None}),
            ({'a_b': [{'b_c': None}]}, {'aB': [{'bC': None}]}),
            ({'_id': None}, {'_id': None}),
        ]
    )
    def test_convert_keys(self, test_input, expected_result):
        # GIVEN any state

        # WHEN field names in a list or dict object are 'converted' from
        # snake_case to camelCase to match GenLIMS conventions

        # THEN keys at all nested levels of the object should be correctly
        # formatted with the exception of '_id', which should be the same
        assert (docs.convert_keys(test_input) == expected_result)


class TestTG3Object:
    """
    Tests behavior of the base data model class, ``TG3Object``.
    """
    @pytest.fixture(scope='function')
    def tg3object(self):
        logger.debug("[setup] TG3Object test instance")

        # GIVEN a ``TG3Object`` with arbitrary ID
        yield docs.TG3Object(_id='tg3-0000')

        logger.debug("[teardown] TG3Object test instance")

    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            ({'_id': 'tg3-0000'},
             {'time_check': operator.eq, 'type': None, 'has_newfield': False}),
            ({'_id': 'tg3-0000', 'type': 'new'},
             {'time_check': operator.gt, 'type': 'new', 'has_newfield': False}),
            ({'new_field': 'foo'},
             {'time_check': operator.gt, 'type': None, 'has_newfield': True}),
        ]
    )
    def test_update_attrs_no_overwrite(self, tg3object,
                                       test_input, expected_result):
        # WHEN `update_attrs()` is called for a dict with key-value pairs
        # specifying the attributes to update, and no fields in the object
        # should be overwritten (non-None values replaced by new values)
        tg3object.update_attrs(test_input)

        # THEN the the updated object should have the expected value for all
        # existing fields that were previously 'None' and any new fields,
        # and the expected relationship between last update and date created
        # attributes (equal, if no updates made; greater than,
        # if any updates made)
        assert (tg3object.type == expected_result['type'])
        assert (expected_result['time_check'](tg3object.last_updated,
                                              tg3object.date_created))
        assert (hasattr(tg3object, 'new_field')
                == expected_result['has_newfield'])

    @pytest.mark.parametrize(
        'test_input, force_opt, expected_result',
        [
            ({'type': 'new'}, False,
             {'time_check': operator.eq, 'type': 'old'}),
            ({'type': 'new'}, True,
             {'time_check': operator.gt, 'type': 'new'}),
        ]
    )
    def test_update_attrs_overwrite(self, tg3object,
                                    test_input, force_opt, expected_result):
        # AND the object has a non-None value for the field to be updated
        tg3object.type = 'old'

        # WHEN `update_attrs()` is called for a dict with key-value pairs
        # specifying the attributes to update, and argument indicating whether
        # or not to 'force' update (when fields already exist and have a value
        # that isn't None) is set to 'True'
        tg3object.update_attrs(test_input, force=force_opt)

        # THEN the the updated object should have the expected value for all
        # existing fields, and the expected relationship between last update
        # and date created attributes (equal, if no updates made; greater than,
        # if any updates made)
        assert (tg3object.type == expected_result['type'])
        assert (expected_result['time_check'](tg3object.last_updated,
                                              tg3object.date_created))

    def test_to_json(self, tg3object):
        # WHEN object attributes are returned as a JSON-like dict

        # THEN the output dict should have expected, correctly formatted fields
        assert (all({field in tg3object.to_json()
                     for field in [
                         '_id', 'type', 'dateCreated', 'lastUpdated'
                     ]}))


class TestSample:
    """
    Tests behavior of objects mapping to the 'samples' collection.
    """
    @pytest.fixture(
        scope='function',
        params=[
            (docs.GenericSample, None),
            (docs.Library, 'library'),
            (docs.SequencedLibrary, 'sequenced library'),
            (docs.ProcessedLibrary, 'processed library'),
        ]
    )
    def sampleobjectdata(self, request):
        logger.debug("[setup] sample test instance")

        # GIVEN a sample object with arbitrary ID
        yield request.param[0](_id='test_sample'), request.param[1]

        logger.debug("[teardown] sample test instance")

    def test_init(self, sampleobjectdata):
        # (GIVEN)
        sampleobject, expected_result = sampleobjectdata

        # WHEN a new sample object type is initialized

        # THEN object should have the expected type attribute value and
        # expected fields for a sample
        assert (sampleobject.type == expected_result)
        assert (all({hasattr(sampleobject, field)
                     for field in ['_id', 'project_id', 'subproject_id',
                                   'protocol_id', 'parent_id']}))


class TestSequencedLibrary:
    """
    Tests methods and behavior for ``SequencedLibrary`` objects.
    """
    @pytest.fixture(scope='function')
    def seqlibobject(self):
        logger.debug("[setup] SequencedLibrary test instance")

        # GIVEN a ``SequencedLibrary`` with mock ID
        yield docs.SequencedLibrary(_id='lib0000_C000000XX')

        logger.debug("[teardown] SequencedLibrary test instance")

    def test_raw_data_property(self, seqlibobject):
        # WHEN the raw data property is used to access the object's
        # raw data attribute

        # THEN output should be an empty list
        assert (seqlibobject.raw_data == [])

    def test_raw_data_setter(self, seqlibobject):
        # WHEN the raw data setter is used to update the objects'
        # raw data attribute
        seqlibobject.raw_data = [{'path': None}]

        # THEN the output should be the updated raw data value
        assert (seqlibobject.raw_data == [{'path': None}])


class TestProcessedLibrary:
    """
    Tests methods and behavior for ``ProcessedLibrary`` objects.
    """
    @pytest.fixture(scope='function')
    def proclibobject(self):
        logger.debug("[setup] ProcessedLibrary test instance")

        # GIVEN a ``ProcessedLibrary`` with mock ID
        yield docs.ProcessedLibrary(_id='lib0000_C000000XX_processed')

        logger.debug("[teardown] ProcessedLibrary test instance")

    def test_processed_data_property(self, proclibobject):
        # WHEN the processed data property is used to access the object's
        # processed data attribute

        # THEN output should be an empty list
        assert (proclibobject.processed_data == [])

    def test_processed_data_setter(self, proclibobject):
        # WHEN the processed data setter is used to update the objects'
        # processed data attribute
        proclibobject.processed_data = [{'path': None}]

        # THEN the output should be the updated processed data value
        assert (proclibobject.processed_data == [{'path': None}])


class TestRun:
    """
    Tests behavior of objects mapping to the 'runs' collection.
    """
    @pytest.fixture(
        scope='function',
        params=[
            (docs.GenericRun, None),
            (docs.FlowcellRun, 'flowcell'),
        ]
    )
    def runobjectdata(self, request):
        logger.debug("[setup] run test instance")

        # GIVEN a run object with arbitrary ID
        yield request.param[0](_id='test_run'), request.param[1]

        logger.debug("[teardown] run test instance")

    def test_init(self, runobjectdata):
        # (GIVEN)
        runobject, expected_result = runobjectdata

        # WHEN a new run object type is initialized

        # THEN object should have the expected type attribute value and
        # expected fields for a run
        assert (runobject.type == expected_result)
        assert (all({hasattr(runobject, field)
                     for field in ['_id', 'protocol_id', 'date']}))


class TestFlowcellRun:
    """
    Tests methods and behavior for ``FlowcellRun`` objects.
    """
    @pytest.fixture(scope='function')
    def fcrunobject(self):
        logger.debug("[setup] FlowcellRun test instance")

        # GIVEN a ``FlowcellRun`` with mock ID
        yield docs.FlowcellRun(_id='150101_D00000_0000_AC00000XX')

        logger.debug("[teardown] FlowcellRun test instance")

    def test_flowcell_path_property(self, fcrunobject):
        # WHEN the flowcell path property is used to access the object's
        # flowcell path attribute

        # THEN output should be an empty list
        assert (fcrunobject.flowcell_path is None)

    def test_flowcell_path_setter(self, fcrunobject):
        # WHEN the flowcell path setter is used to update the objects'
        # flowcell path attribute
        fcrunobject.flowcell_path = '/~/path-to-flowcell'

        # THEN the output should be the updated processed data value
        assert (fcrunobject.flowcell_path == '/~/path-to-flowcell')


class TestWorkflow:
    """
    Tests behavior of objects mapping to the 'workflows' collection.
    """
    @pytest.fixture(
        scope='function',
        params=[
            (docs.GenericWorkflow, None),
            (docs.GlobusGalaxyWorkflow, 'Globus Galaxy workflow'),
        ]
    )
    def wkflowobjectdata(self, request):
        logger.debug("[setup] workflow test instance")

        # GIVEN a workflow object with arbitrary ID
        yield request.param[0](_id='test_workflow'), request.param[1]

        logger.debug("[teardown] workflow test instance")

    def test_init(self, wkflowobjectdata):
        # (GIVEN)
        wkflowobject, expected_result = wkflowobjectdata

        # WHEN a new workflow object type is initialized

        # THEN object should have the expected type attribute value and
        # expected fields for a workflow
        assert (wkflowobject.type == expected_result)
        assert (all({hasattr(wkflowobject, field)
                     for field in ['_id']}))


class TestWorkflowBatch:
    """
    Tests behavior of objects mapping to the 'workflowbatches'
    collection.
    """
    @pytest.fixture(
        scope='function',
        params=[
            (docs.GenericWorkflowBatch, None),
            (docs.GalaxyWorkflowBatch, 'Galaxy workflow batch'),
        ]
    )
    def wbatchobjectdata(self, request):
        logger.debug("[setup] workflow batch test instance")

        # GIVEN a workflow batch object with arbitrary ID
        yield request.param[0](_id='test_workflowbatch'), request.param[1]

        logger.debug("[teardown] workflow batch test instance")

    def test_init(self, wbatchobjectdata):
        # (GIVEN)
        wbatchobject, expected_result = wbatchobjectdata

        # WHEN a new workflow object type is initialized

        # THEN object should have the expected type attribute value and
        # expected fields for a workflow
        assert (wbatchobject.type == expected_result)
        assert (all({hasattr(wbatchobject, field)
                     for field in ['_id']}))

