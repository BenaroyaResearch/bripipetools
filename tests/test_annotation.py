import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import re
import pytest
import mongomock

from bripipetools.annotation import illuminaseq, globusgalaxy
from bripipetools import model

@pytest.fixture(scope="class")
def mock_genomics_server(request):
    logger.info(("[setup] mock 'genomics' server, connect "
                 "to mock 'genomics' server"))
    run_id = '150615_D00565_0087_AC6VG0ANXX'
    mock_genomics_root = './tests/test-data/'
    mock_genomics_path = os.path.join(mock_genomics_root, 'genomics')
    mock_flowcell_path = os.path.join(mock_genomics_path, 'Illumina', run_id)
    mock_unaligned_path = os.path.join(mock_flowcell_path, 'Unaligned')
    # mock_batch_submit_path = os.path.join(mock_flowcell_path,
    #                                       'globus_batch_submission')
    mock_workflow_batch_file = os.path.join(
        mock_flowcell_path, 'globus_batch_submission',
        ("160412_P109-1_P14-12_C6VG0ANXX_"
         "optimized_truseq_unstrand_sr_grch38_v0.1_complete.txt")
    )

    data = {'run_id': run_id,
            'genomics_root': mock_genomics_root,
            'genomics_path': mock_genomics_path,
            'flowcell_path': mock_flowcell_path,
            'unaligned_path': mock_unaligned_path,
            'project_p14_12': 'P14-12-23221204',
            'project_p109_1': 'P109-1-21113094',
            'lib7293': 'lib7293-25920016',
            'lib7293_fastq': 'MXU01-CO072_S1_L001_R1_001.fastq.gz',
            'workflowbatch_file': mock_workflow_batch_file,
            'batch_name': '160412_P109-1_P14-12_C6VG0ANXX'}
    def fin():
        logger.info(("[teardown] mock 'genomics' server, disconnect "
                     "from mock 'genomics' server"))
    request.addfinalizer(fin)
    return data

@pytest.fixture(scope="class")
def prod_genomics_server(request):
    logger.info(("[setup] production 'genomics' server, connect "
                 "to production 'genomics' server"))
    run_id = '150615_D00565_0087_AC6VG0ANXX'
    prod_genomics_root = '/mnt/' if os.path.exists('/mnt/') else '/Volumes/'
    prod_genomics_path = os.path.join(prod_genomics_root, 'genomics')
    prod_flowcell_path = os.path.join(prod_genomics_path, 'Illumina', run_id)
    data = {'run_id': run_id,
            'genomics_root': prod_genomics_root,
            'genomics_path': prod_genomics_path,
            'flowcell_path': prod_flowcell_path}
    def fin():
        logger.info(("[teardown] production 'genomics' server, disconnect "
                     "from 'genomics' server"))
    request.addfinalizer(fin)
    return data

@pytest.fixture(scope='class')
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
    db.workflowbatches.insert(
        {"_id": "globusgalaxy_2016-04-12_1",
        "workflowbatchFile": ("/genomics/Illumina/"
                              "150615_D00565_0087_AC6VG0ANXX/"
                              "globus_batch_submission/"
                              "160412_P109-1_P14-12_C6VG0ANXX_"
                              "optimized_truseq_unstrand_sr_grch38_"
                              "v0.1_complete.txt"),
        "date": "2016-04-12",
    	"workflowId": "optimized_truseq_unstrand_sr_grch38_v0.1_complete.txt",
    	"projects": ["P109-1", "P14-12"],
    	"flowcellId": "C6VG0ANXX"}
    )
    def fin():
        logger.info(("[teardown] mock 'tg3' database, disconnect "
                     "from mock 'tg3' Mongo database"))
    request.addfinalizer(fin)
    return db

@pytest.mark.usefixtures('prod_genomics_server')
class TestFlowcellRunAnnotatorWithProdGenomicsServer:
    @pytest.fixture(scope="class")
    def annotator(self, request, prod_genomics_server):
        logger.info("[setup] FlowcellRunAnnotator production instance")

        # GIVEN a FlowcellRunAnnotator with production 'genomics' server path
        # (i.e., either under /mnt/ or /Volumes/), valid run ID, and existing
        # 'Unaligned' folder
        fcrunannotator = illuminaseq.FlowcellRunAnnotator(
            prod_genomics_server['run_id'],
            prod_genomics_server['genomics_root']
        )
        def fin():
            logger.info("[teardown] FlowcellRunAnnotator instance")
        request.addfinalizer(fin)
        return fcrunannotator

    def test_has_valid_flowcellrun(self, annotator):
        logger.info("test if has FlowcellRun object")

        # WHEN checking whether FlowcellRun object was automatically
        # initialized for annotator instance
        flowcellrun = annotator.flowcellrun

        # THEN object should be of type FlowcellRun
        assert(type(flowcellrun) is model.FlowcellRun)

    def test_get_flowcell_path(self, annotator, prod_genomics_server):
        logger.info("test `get_flowcell_path()`")

        # WHEN searching for flowcell run ID in 'genomics' path
        flowcell_path = annotator._get_flowcell_path()

        # THEN correct flowcell folder should be found in 'genomics/Illumina/'
        assert(flowcell_path == prod_genomics_server['flowcell_path'])

@pytest.mark.usefixtures('mock_genomics_server')
class TestFlowcellRunAnnotatorWithMockGenomicsServer:
    @pytest.fixture(scope="class")
    def annotator(self, request, mock_genomics_server):
        logger.info("[setup] FlowcellRunAnnotator test instance")

        # GIVEN a FlowcellRunAnnotator with mock 'genomics' server path,
        # valid run ID, and existing 'Unaligned' folder (i.e., where data
        # and organization is known)
        fcrunannotator = illuminaseq.FlowcellRunAnnotator(
            mock_genomics_server['run_id'],
            mock_genomics_server['genomics_root']
        )
        def fin():
            logger.info("[teardown] FlowcellRunAnnotator mock instance")
        request.addfinalizer(fin)
        return fcrunannotator

    def test_has_valid_flowcellrun(self, annotator):
        logger.info("test if has FlowcellRun object")

        # WHEN checking whether FlowcellRun object was automatically
        # initialized for annotator instance
        flowcellrun = annotator.flowcellrun

        # THEN object should be of type FlowcellRun
        assert(type(flowcellrun) is model.FlowcellRun)

    def test_get_flowcell_path(self, annotator, mock_genomics_server):
        logger.info("test `_get_flowcell_path()`")

        # WHEN searching for flowcell run ID in 'genomics' path
        flowcell_path = annotator._get_flowcell_path()

        # THEN correct flowcell folder should be found in 'genomics/Illumina/'
        assert(flowcell_path == mock_genomics_server['flowcell_path'])

    def test_get_unaligned_path(self, annotator, mock_genomics_server):
        logger.info("test `_get_unaligned_path()`")

        # WHEN searching for 'Unaligned' folder
        unaligned_path = annotator._get_unaligned_path()

        # THEN path returned should be 'genomics/Illumina/<run_id>/Unaligned'
        assert(unaligned_path == mock_genomics_server['unaligned_path'])

    def test_get_projects(self, annotator, mock_genomics_server):
        logger.info("test `_get_projects()`")

        # WHEN listing unaligned projects
        projects = annotator.get_projects()

        # THEN should find 8 total projects, including P14-12 and P109-1
        assert(len(projects) == 8)
        assert(mock_genomics_server['project_p14_12'] in projects)
        assert(mock_genomics_server['project_p109_1'] in projects)

    def test_get_libraries_P14_12(self, annotator, mock_genomics_server):
        logger.info("test `_get_libraries()`, single project")

        # WHEN listing libraries for project P14-12
        libraries = annotator.get_libraries('P14-12')

        # THEN should find 5 total libraries, including lib7293
        assert(len(libraries) == 5)
        assert(mock_genomics_server['lib7293'] in libraries)

    def test_get_libraries_all_projects(self, annotator, mock_genomics_server):
        logger.info("test `_get_libraries()`, all projects")

        # WHEN listing libraries for all projects
        libraries = annotator.get_libraries()

        # THEN should find 36 total projects
        assert(len(libraries) == 36)

    def test_get_sequenced_libraries_P14_12(self, annotator, mock_genomics_server):
        logger.info("test `get_sequenced_libraries()`, single project")

        # WHEN collecting sequenced libraries for project P14-12
        sequencedlibraries = annotator.get_sequenced_libraries('P14-12')

        # THEN should find 5 total libraries, including lib7293
        assert(len(sequencedlibraries) == 5)
        # assert(mock_genomics_server['lib7293'] in libraries)

@pytest.mark.usefixtures('mock_genomics_server')
class TestSequencedLibraryAnnotatorWithMockGenomicsServer:
    @pytest.fixture(scope="class")
    def annotator(self, request, mock_genomics_server):
        logger.info("[setup] SequencedLibraryAnnotator mock instance")

        # GIVEN a SequencedLibraryAnnotator with mock 'genomics' server path,
        # and path to library folder (i.e., where data/organization is known),
        # with specified library, project, and run ID
        seqlibannotator = illuminaseq.SequencedLibraryAnnotator(
            os.path.join(mock_genomics_server['unaligned_path'],
                         mock_genomics_server['project_p14_12'],
                         mock_genomics_server['lib7293']),
            mock_genomics_server['lib7293'],
            mock_genomics_server['project_p14_12'],
            mock_genomics_server['run_id']
        )
        def fin():
            logger.info("[teardown] SequencedLibraryAnnotator mock instance")
        request.addfinalizer(fin)
        return seqlibannotator

    def test_init_attribute_munging(self, annotator):
        logger.info("test `__init__()` for proper attribute munging")

        # WHEN checking whether input arguments were automatically munged
        # when setting annotator attributes
        seqlib_id = annotator.seqlib_id

        # THEN the sequenced library ID should be properly constructed as the
        # library ID and flowcell ID
        assert(seqlib_id == 'lib7293_C6VG0ANXX')

    def test_has_valid_sequencedlibrary(self, annotator):
        logger.info("test if has SequencedLibrary object")

        # WHEN checking whether SequencedLibrary object was automatically
        # initialized for annotator instance
        sequencedlibrary = annotator.sequencedlibrary

        # THEN object should be of type SequencedLibrary
        assert(type(sequencedlibrary) is model.SequencedLibrary)

    def test_get_raw_data(self, annotator, mock_genomics_server):
        logger.info("test `_get_raw_data()`")

        # WHEN collecting raw data for a sequenced library
        raw_data = annotator._get_raw_data()

        # THEN should be a list of dicts, with the correct details for each
        # FASTQ file identified
        assert(isinstance(raw_data, list))
        assert(re.search(mock_genomics_server['lib7293_fastq'],
                         raw_data[0]['path']))

    def test_update_sequenced_library(self, annotator):
        logger.info("test `_update_sequenced_library()`")

        # WHEN sequenced library object is updated
        annotator._update_sequenced_library()

        # THEN the object should have at least the 'run_id', 'project_id',
        # 'subproject_id', 'parent_id' and 'raw_data' attributes
        assert(hasattr(annotator.sequencedlibrary, 'run_id'))
        assert(hasattr(annotator.sequencedlibrary, 'project_id'))
        assert(hasattr(annotator.sequencedlibrary, 'subproject_id'))
        assert(hasattr(annotator.sequencedlibrary, 'parent_id'))
        assert(hasattr(annotator.sequencedlibrary, 'raw_data'))

    def test_get_sequenced_library(self, annotator):
        logger.info("test `get_sequenced_library()`")

        # WHEN sequenced library object is returned
        sequencedlibrary = annotator.get_sequenced_library()

        # THEN the object should be of type SequencedLibrary and have
        # at least the 'run_id', 'project_id', 'subproject_id', 'parent_id',
        # and 'raw_data' attributes
        assert(type(sequencedlibrary) is model.SequencedLibrary)
        assert(hasattr(sequencedlibrary, 'run_id'))
        assert(hasattr(sequencedlibrary, 'project_id'))
        assert(hasattr(sequencedlibrary, 'subproject_id'))
        assert(hasattr(sequencedlibrary, 'parent_id'))
        assert(hasattr(sequencedlibrary, 'raw_data'))


@pytest.mark.usefixtures('mock_genomics_server', 'mock_db')
class TestWorkflowBatchAnnotatorWithMockGenomicsServer:
    @pytest.fixture(scope='function')
    def annotator(self, request, mock_genomics_server, mock_db):
        logger.info("[setup] WorkflowBatchAnnotator mock instance")

        # GIVEN a WorkflowBatchAnnotator with mock 'genomics' server path,
        # and path to workflow batch file with specified genomics root
        wflowbatchannotator = globusgalaxy.WorkflowBatchAnnotator(
            workflowbatch_file=mock_genomics_server['workflowbatch_file'],
            db=mock_db,
            genomics_root=mock_genomics_server['genomics_root']
        )
        def fin():
            logger.info("[teardown] WorkflowBatchAnnotator mock instance")
        request.addfinalizer(fin)
        return wflowbatchannotator

    def test_init_file_parsing(self, annotator):
        logger.info("test `__init__()` for proper file parsing")

        # WHEN checking whether input arguments were automatically munged
        # when setting annotator attributes
        workflowbatch_data = annotator.workflowbatch_data

        # THEN the workflow batch data should be a dictionary with fields for
        # workflow name, parameters, and samples
        assert(workflowbatch_data['workflow_name'] ==
            ("optimized_truseq_unstrand_sr_grch38_v0.1_complete"))
        assert(len(workflowbatch_data['parameters']) == 35)
        assert(len(workflowbatch_data['samples']) == 2)

    def test_parse_batch_name(self, annotator, mock_genomics_server):
        logger.info("test `_parse_batch_name()`")

        # WHEN parsing batch name from workflow batch file
        batch_items = annotator._parse_batch_name(
            mock_genomics_server['batch_name']
            )

        # THEN items should be in a dict with fields for date (string),
        # project labels (list of strings), and flowcell ID (string)
        assert(batch_items['date'] == '2016-04-12')
        assert(batch_items['projects'] == ['P109-1', 'P14-12'])
        assert(batch_items['flowcell_id'] == 'C6VG0ANXX')
    #
    # def test_init_file_parsing(self, annotator):
    #     logger.info("test `__init__()` for proper file parsing")
    #
    #     # WHEN checking whether batch name was automatically munged
    #     # when setting annotator attributes
    #     date = annotator.date
    #     projects = annotator.projects
    #     flowcell_id = annotator.flowcell_id
    #
    #     # THEN the date, projects, and flowcell ID attributes should be
    #     # set as expected
    #     assert(date == '2016-04-12')
    #     assert(projects == ['P109-1', 'P14-12'])
    #     assert(flowcell_id == 'C6VG0ANXX')

    def test_init_workflowbatch_existing_batch(self, annotator):
        logger.info("test `_init_workflowbatch()` with existing batch")

        # WHEN workflow batch exists in 'workflowbatches' collection
        workflowbatch = annotator._init_workflowbatch()

        # THEN existing workflow batch should be returned
        assert(workflowbatch['_id'] == 'globusgalaxy_2016-04-12_1')

    def test_init_workflowbatch_new_batch(self, annotator):
        logger.info("test `_init_workflowbatch()` with existing batch")

        # WHEN workflow batch exists in 'workflowbatches' collection
        annotator.db.workflowbatches.delete_one(
            {'_id': 'globusgalaxy_2016-04-12_1'}
        )
        workflowbatch = annotator._init_workflowbatch()

        # THEN existing workflow batch should be returned
        assert(workflowbatch._id == 'globusgalaxy_2016-04-12_1')

    def test_has_valid_workflowbatch(self, annotator):
        logger.info("test if has WorkflowBatch object")

        # WHEN checking whether WorkflowBatch object was automatically
        # initialized for annotator instance
        workflowbatch = annotator.workflowbatch

        # THEN object should be of type SequencedLibrary
        assert(type(workflowbatch) is model.GalaxyWorkflowBatch)
