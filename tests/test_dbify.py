import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import os

import pytest
import mongomock

from bripipetools import model as docs
from bripipetools import dbify

@pytest.fixture(scope='class')
def mock_db(request):
    logger.info(("[setup] mock database, connect "
                 "to mock Mongo database"))
    db = mongomock.MongoClient().db

    def fin():
        logger.info(("[teardown] mock database, disconnect "
                     "from mock Mongo database"))
    request.addfinalizer(fin)
    return db


@pytest.mark.usefixtures('mock_genomics_server', 'mock_db')
class TestSequencingImporter:
    @pytest.fixture(scope='class', params=[{'runnum': r} for r in range(1)])
    def importerdata(self, request, mock_genomics_server, mock_db):
        # GIVEN a SequencingImporter with mock 'genomics' server path to
        # flowcell run directory and mock database connection
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param['runnum']]
        # projects = rundata['processed']['projects']
        # projectdata = projects[request.param[1]['projectnum']]
        # sourcedata = projectdata['qc']['sources'][request.param[0]]
        # samplefile = sourcedata[request.param[1]['samplenum']]

        logger.info("[setup] SequencingImporter test instance "
                    "for run {}".format(rundata['run_id']))

        sequencingimporter = dbify.SequencingImporter(
            path=rundata['path'],
            db=mock_db)

        def fin():
            logger.info("[teardown] SequencingImporter mock instance")
        request.addfinalizer(fin)
        return (sequencingimporter, rundata)

    def test_parse_flowcell_path(self, importerdata, mock_genomics_server):
        # (GIVEN)
        importer, rundata = importerdata

        logger.info("test `_get_genomics_root()`")

        # WHEN the path argument is parsed to find the 'genomics' root
        # and flowcell run ID
        path_items = importer._parse_flowcell_path()

        # THEN the 'genomics' root and run ID should match the mock server
        assert(path_items['genomics_root']
               == mock_genomics_server['root']['path'])
        assert(path_items['run_id'] == rundata['run_id'])

    def test_collect_flowcellrun(self, importerdata):
        # (GIVEN)
        importer, _ = importerdata

        logger.info("test `_collect_flowcellrun()`")

        # WHEN collecting FlowcellRun object for flowcell run
        flowcellrun = importer._collect_flowcellrun()

        # THEN should return object of correct type
        assert(type(flowcellrun) == docs.FlowcellRun)

    def test_collect_sequencedlibraries(self, importerdata):
        # (GIVEN)
        importer, rundata = importerdata

        logger.info("test `_collect_sequencedlibraries()`")

        # WHEN collecting list of SequencedLibrary objects for flowcell run
        sequencedlibraries = importer._collect_sequencedlibraries()

        # THEN should return 31 total objects of correct type
        assert(len(sequencedlibraries)
               == sum(map(lambda x: len(x['samples']),
                      rundata['unaligned']['projects'])))
        assert(all([type(sl) == docs.SequencedLibrary
                    for sl in sequencedlibraries]))

    def test_insert_flowcellrun(self, importerdata, mock_db):
        # (GIVEN)
        importer, rundata = importerdata

        logger.info("test `_insert_flowcellrun()`")

        # WHEN flowcell run is inserted into database
        importer._insert_flowcellrun()

        # THEN documents should be present in the runs collection
        assert(len(list(mock_db.runs.find({'type': 'flowcell'})))
               == 1)
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.runs.drop()

    def test_insert_sequencedlibraries(self, importerdata, mock_db):
        # (GIVEN)
        importer, rundata = importerdata

        logger.info("test `_insert_sequencedlibraries()`")

        # WHEN sequenced libraries are inserted into database
        importer._insert_sequencedlibraries()

        # THEN documents should be present in the samples collection
        assert(len(list(mock_db.samples.find({'type': 'sequenced library'})))
               == sum(map(lambda x: len(x['samples']),
                      rundata['unaligned']['projects'])))
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.samples.drop()

    def test_insert_all(self, importerdata, mock_db):
        # (GIVEN)
        importer, rundata = importerdata

        logger.info("test `_insert()` for all collections")

        # WHEN inserting with collection argument set to 'all' (default)
        importer.insert()

        # THEN documents should be present in both runs and samples collections
        assert(len(list(mock_db.runs.find({'type': 'flowcell'})))
               == 1)
        assert(len(list(mock_db.samples.find({'type': 'sequenced library'})))
               == sum(map(lambda x: len(x['samples']),
                      rundata['unaligned']['projects'])))
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.runs.drop()
        mock_db.samples.drop()

    def test_insert_runs(self, importerdata, mock_db):
        # (GIVEN)
        importer, rundata = importerdata

        logger.info("test `_insert()` for runs only")

        # WHEN inserting with collection argument set to 'runs'
        importer.insert(collection='runs')

        # THEN documents should be present in only runs collections
        assert(len(list(mock_db.runs.find({'type': 'flowcell'})))
               == 1)
        assert(len(list(mock_db.samples.find({'type': 'sequenced library'})))
               == 0)
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.runs.drop()
        mock_db.samples.drop()

    def test_insert_samples(self, importerdata, mock_db):
        # (GIVEN)
        importer, rundata = importerdata

        logger.info("test `_insert()` for samples only")

        # WHEN inserting with collection argument set to 'samples'
        importer.insert(collection='samples')

        # THEN new documents should be present in only runs collections
        assert(len(list(mock_db.runs.find({'type': 'flowcell'})))
               == 0)
        assert(len(list(mock_db.samples.find({'type': 'sequenced library'})))
               == sum(map(lambda x: len(x['samples']),
                      rundata['unaligned']['projects'])))
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.runs.drop()
        mock_db.samples.drop()


@pytest.mark.usefixtures('mock_genomics_server', 'mock_db')
class TestProcessingImporter:
    @pytest.fixture(
        scope='class',
        params=[{'runnum': r, 'batchnum': b}
                for r in range(1)
                for b in range(2)])
    def importerdata(self, request, mock_genomics_server, mock_db):
        # GIVEN a ProcessingImporter with mock 'genomics' server path to
        # workflow batch file and mock database connection
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param['runnum']]
        batches = rundata['submitted']['batches']
        batchdata = batches[request.param['batchnum']]

        logger.info("[setup] ProcessingImporter test instance "
                    "for run {} with workflow batch {}"
                    .format(rundata['run_id'], batchdata['path']))

        processingimporter = dbify.ProcessingImporter(
            path=batchdata['path'],
            db=mock_db)

        def fin():
            logger.info("[teardown] ProcessingImporter mock instance")
        request.addfinalizer(fin)
        return (processingimporter, batchdata)

    def test_parse_batch_file_path(self, importerdata, mock_genomics_server):
        # (GIVEN)
        importer, batchdata = importerdata

        logger.info("test `_get_genomics_root()`")

        # WHEN the path argument is parsed to find the 'genomics' root
        # and workflow batch file name
        path_items = importer._parse_batch_file_path()

        # THEN the 'genomics' root and run ID should match the mock server
        assert(path_items['genomics_root']
               == mock_genomics_server['root']['path'])
        assert(path_items['workflowbatch_filename']
               == os.path.basename(batchdata['path']))

    def test_collect_workflowbatch(self, importerdata):
        # (GIVEN)
        importer, batchdata = importerdata

        logger.info("test `_collect_workflowbatch()`")

        # WHEN collecting WorkflowBatch object for processing batch
        workflowbatch = importer._collect_workflowbatch()

        # THEN should return object of correct type
        assert(type(workflowbatch) == docs.GalaxyWorkflowBatch)

    def test_collect_processedlibraries(self, importerdata):
        # (GIVEN)
        importer, batchdata = importerdata

        logger.info("test `_collect_processedlibraries()`")

        # WHEN collecting list of ProcessedLibrary objects for workflow batch
        processedlibraries = importer._collect_processedlibraries()

        # THEN should return expected number of objects of correct type
        assert(len(processedlibraries) == batchdata['num_samples'])
        assert(all([type(pl) == docs.ProcessedLibrary
                    for pl in processedlibraries]))

    def test_insert_workflowbatch(self, importerdata, mock_db):
        # (GIVEN)
        importer, batchdata = importerdata

        logger.info("test `_insert_workflowbatch()`")

        # WHEN workflow batch is inserted into database
        importer._insert_workflowbatch()

        # THEN documents should be present in the workflowbatches collection
        assert(len(list(mock_db.workflowbatches.find(
               {'type': 'Galaxy workflow batch'})))
               == 1)
        logger.info(("[semi-teardown] mock 'tg3' database, "
                     "drop workflowbatches collection from mock database"))
        mock_db.workflowbatches.drop()

    def test_insert_processedlibraries(self, importerdata, mock_db):
        # (GIVEN)
        importer, batchdata = importerdata

        logger.info("test `_insert_processedlibraries()`")

        # WHEN processed libraries are inserted into database
        importer._insert_processedlibraries()

        # THEN documents should be present in the samples collection
        assert(len(list(mock_db.samples.find({'type': 'processed library'})))
               == batchdata['num_samples'])
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.samples.drop()

    def test_insert_all(self, importerdata, mock_db):
        # (GIVEN)
        importer, batchdata = importerdata

        logger.info("test `_insert()` for all collections")

        # WHEN inserting with collection argument set to 'all' (default)
        importer.insert()

        # THEN documents should be present in both workflowbatches and
        # samples collections
        assert(len(list(mock_db.workflowbatches.find(
               {'type': 'Galaxy workflow batch'})))
               == 1)
        assert(len(list(mock_db.samples.find({'type': 'processed library'})))
               == batchdata['num_samples'])
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.workflowbatches.drop()
        mock_db.samples.drop()

    def test_insert_workflowbatches(self, importerdata, mock_db):
        # (GIVEN)
        importer, batchdata = importerdata

        logger.info("test `_insert()` for workflowbatches only")

        # WHEN inserting with collection argument set to 'workflowbatches'
        importer.insert(collection='workflowbatches')

        # THEN documents should be present in only workflowbatches collections
        assert(len(list(mock_db.workflowbatches.find(
               {'type': 'Galaxy workflow batch'})))
               == 1)
        assert(len(list(mock_db.samples.find({'type': 'processed library'})))
               == 0)
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.workflowbatches.drop()
        mock_db.samples.drop()

    def test_insert_samples(self, importerdata, mock_db):
        # (GIVEN)
        importer, batchdata = importerdata

        logger.info("test `_insert()` for samples only")

        # WHEN inserting with collection argument set to 'samples'
        importer.insert(collection='samples')

        # THEN documents should be present in only runs collections
        assert(len(list(mock_db.workflowbatches.find(
               {'type': 'Galaxy workflow batch'})))
               == 0)
        assert(len(list(mock_db.samples.find({'type': 'processed library'})))
               == batchdata['num_samples'])
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.workflowbatches.drop()
        mock_db.samples.drop()


@pytest.mark.usefixtures('mock_genomics_server', 'mock_db')
class TestImportManagerWithFlowcellPath:
    @pytest.fixture(
        scope='class',
        params=[{'runnum': r, 'batchnum': b}
                for r in range(1)
                for b in range(2)])
    def managerdata(self, request, mock_genomics_server, mock_db):
        # GIVEN a ImportManager with mock database connection and path
        # to a flowcell directory
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param['runnum']]
        batches = rundata['submitted']['batches']
        batchdata = batches[request.param['batchnum']]

        logger.info("[setup] ImportManager test instance "
                    "for run {} and/or workflow batch {}"
                    .format(rundata['run_id'], batchdata['path']))

        importmanager = dbify.ImportManager(
            path=rundata['path'],
            db=mock_db)

        def fin():
            logger.info("[teardown] ImportManager mock instance")
        request.addfinalizer(fin)
        return (importmanager, rundata, batchdata)

    def test_sniff_path_flowcell_path(self, managerdata, mock_genomics_server):
        # (GIVEN)
        manager, rundata, _ = managerdata

        logger.info("test `_sniff_path()` for flowcell path")

        # WHEN a flowcell path is checked to determine type
        path_type = manager._sniff_path(rundata['path'])

        # THEN path type should be 'flowcell_path'
        assert(path_type == 'flowcell_path')

    def test_sniff_path_workflowbatch_file(self, managerdata,
                                           mock_genomics_server):
        # (GIVEN)
        manager, _, batchdata = managerdata

        logger.info("test `_sniff_path()` for workflow batch file")

        # WHEN a flowcell path is checked to determine type
        path_type = manager._sniff_path(batchdata['path'])

        # THEN path type should be 'flowcell_path'
        assert(path_type == 'workflowbatch_file')

    def test_init_importer(self, managerdata):
        # (GIVEN)
        manager, _, _ = managerdata

        logger.info("test `_init_importer()`")

        # WHEN importer is selected
        manager._init_importer()
        importer = manager.importer

        # THEN should be of type SequencingImporter
        assert(type(importer) == dbify.SequencingImporter)

    def test_run(self, managerdata, mock_db):
        # (GIVEN)
        manager, rundata, _ = managerdata

        logger.info("test `run()`")

        # WHEN using run to execute the importer insert method
        manager.run()

        # THEN documents should be present in both runs and samples collections
        assert(len(list(mock_db.runs.find({'type': 'flowcell'})))
               == 1)
        assert(len(list(mock_db.samples.find({'type': 'sequenced library'})))
               == sum(map(lambda x: len(x['samples']),
                      rundata['unaligned']['projects'])))

        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.workflowbatches.drop()
        mock_db.samples.drop()


@pytest.mark.usefixtures('mock_genomics_server', 'mock_db')
class TestImportManagerWithWorkflowBatchFile:
    @pytest.fixture(
        scope='class',
        params=[{'runnum': r, 'batchnum': b}
                for r in range(1)
                for b in range(2)])
    def managerdata(self, request, mock_genomics_server, mock_db):
        # GIVEN a ImportManager with mock database connection and path
        # to a flowcell directory
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param['runnum']]
        batches = rundata['submitted']['batches']
        batchdata = batches[request.param['batchnum']]

        logger.info("[setup] ImportManager test instance "
                    "for run {} and/or workflow batch {}"
                    .format(rundata['run_id'], batchdata['path']))

        importmanager = dbify.ImportManager(
            path=batchdata['path'],
            db=mock_db)

        def fin():
            logger.info("[teardown] ImportManager mock instance")
        request.addfinalizer(fin)
        return (importmanager, rundata, batchdata)

    def test_sniff_path_flowcell_path(self, managerdata, mock_genomics_server):
        # (GIVEN)
        manager, rundata, _ = managerdata

        logger.info("test `_sniff_path()` for flowcell path")

        # WHEN a flowcell path is checked to determine type
        path_type = manager._sniff_path(rundata['path'])

        # THEN path type should be 'flowcell_path'
        assert(path_type == 'flowcell_path')

    def test_sniff_path_workflowbatch_file(self, managerdata,
                                           mock_genomics_server):
        # (GIVEN)
        manager, _, batchdata = managerdata

        logger.info("test `_sniff_path()` for workflow batch file")

        # WHEN a flowcell path is checked to determine type
        path_type = manager._sniff_path(batchdata['path'])

        # THEN path type should be 'flowcell_path'
        assert(path_type == 'workflowbatch_file')

    def test_init_importer(self, managerdata):
        # (GIVEN)
        manager, _, _ = managerdata

        logger.info("test `_init_importer()`")

        # WHEN importer is selected
        manager._init_importer()
        importer = manager.importer

        # THEN should be of type SequencingImporter
        assert(type(importer) == dbify.ProcessingImporter)

    def test_run(self, managerdata, mock_db):
        # (GIVEN)
        manager, _, batchdata = managerdata

        logger.info("test `run()`")

        # WHEN using run to execute the importer insert method
        manager.run()

        # THEN documents should be present in both workflowbatches and
        # samples collections
        assert(len(list(mock_db.workflowbatches.find(
               {'type': 'Galaxy workflow batch'})))
               == 1)
        assert(len(list(mock_db.samples.find({'type': 'processed library'})))
               == batchdata['num_samples'])

        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.workflowbatches.drop()
        mock_db.samples.drop()
