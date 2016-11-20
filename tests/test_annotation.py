import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
import re
import datetime

import pytest
import mongomock

from bripipetools import model as docs
from bripipetools import io
from bripipetools import annotation

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
class TestFlowcellRunAnnotator:
    """
    Tests methods for the `FlowcellRunAnnotator` class in the
    `bripipetools.annotation.illuminaseq` module.
    """
    @pytest.fixture(scope='class', params=[{'runnum': r} for r in range(1)])
    def annotatordata(self, request, mock_genomics_server, mock_db):
        # GIVEN a FlowcellRunAnnotator with mock 'genomics' server path,
        # valid run ID, and existing 'Unaligned' folder (i.e., where data
        # and organization is known), as well as a mock db connection
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param['runnum']]

        logger.info("[setup] FlowcellRunAnnotator test instance "
                    "for run {}".format(rundata['run_id']))

        fcrunannotator = annotation.FlowcellRunAnnotator(
            run_id=rundata['run_id'],
            db=mock_db,
            genomics_root=mock_genomics_server['root']['path'])

        def fin():
            logger.info("[teardown] FlowcellRunAnnotator mock instance")
        request.addfinalizer(fin)
        return (fcrunannotator, rundata)

    def test_init_flowcellrun_existing_run(self, annotatordata, mock_db):
        # (GIVEN)
        (annotator, rundata) = annotatordata

        logger.info("test `_init_flowcellrun()` with existing run")

        # WHEN flowcell run already exists in 'runs' collection
        mock_db.runs.insert_one(
            {'_id': rundata['run_id'],
             'type': 'flowcell',
             'isMock': True})
        flowcellrun = annotator._init_flowcellrun()

        # THEN the flowcell run object should be returned and
        # should be correctly mapped from the database object
        assert(type(flowcellrun) == docs.FlowcellRun)
        assert(flowcellrun._id == rundata['run_id'])
        assert(hasattr(flowcellrun, 'is_mock'))

        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.runs.drop()

    def test_init_flowcellrun_new_run(self, annotatordata):
        # (GIVEN)
        annotator, rundata = annotatordata

        logger.info("test `_init_flowcellrun()` with new run")

        # WHEN flowcell run run does not already exist in
        # 'runs' collection
        flowcellrun = annotator._init_flowcellrun()

        # THEN a new flowcell run object should be returned
        assert(type(flowcellrun) == docs.FlowcellRun)
        assert(flowcellrun._id == rundata['run_id'])
        assert(not hasattr(flowcellrun, 'is_mock'))
#
    def test_get_flowcell_path(self, annotatordata, mock_genomics_server):
        # (GIVEN)
        annotator, rundata = annotatordata

        logger.info("test `_get_flowcell_path()`")

        # WHEN searching for flowcell run ID in 'genomics' path

        # THEN correct flowcell folder should be found in 'genomics/Illumina/'
        assert(annotator._get_flowcell_path() == rundata['path'])

    def test_get_unaligned_path(self, annotatordata, mock_genomics_server):
        # (GIVEN)
        annotator, rundata = annotatordata

        logger.info("test `_get_unaligned_path()`")

        # WHEN searching for 'Unaligned' folder

        # THEN path returned should be 'genomics/Illumina/<run_id>/Unaligned'
        assert(annotator._get_unaligned_path() == rundata['unaligned']['path'])

    def test_get_projects(self, annotatordata, mock_genomics_server):
        # (GIVEN)
        annotator, rundata = annotatordata

        logger.info("test `_get_projects()`")

        # WHEN listing unaligned projects
        projects = annotator.get_projects()

        # THEN should find expected number of projects
        assert(len(projects) == len(rundata['unaligned']['projects']))

    @pytest.mark.parametrize("projectnum", [0, 1, 2])
    def test_get_libraries_single_project(self, annotatordata,
                                          mock_genomics_server, projectnum):
        # (GIVEN)
        annotator, rundata = annotatordata

        # AND unaligned samples for a single project
        projectdata = rundata['unaligned']['projects'][projectnum]

        logger.info("test `_get_libraries()`, single project ({})"
                    .format(projectdata['name']))

        # WHEN listing libraries for the project
        libraries = annotator.get_libraries(projectdata['name'])

        # THEN should find the expected number of libaries (samples)
        assert(len(libraries) == len(projectdata['samples']))

    def test_get_libraries_all_projects(self, annotatordata,
                                        mock_genomics_server):
        # (GIVEN)
        annotator, rundata = annotatordata

        # AND list of unaligned projects
        projects = rundata['unaligned']['projects']

        logger.info("test `_get_libraries()`, all projects")

        # WHEN listing libraries for all projects
        libraries = annotator.get_libraries()

        # THEN should find expected number of libraries
        assert(len(libraries)
                == sum(map(lambda x: len(x['samples']), projects)))

    @pytest.mark.parametrize("projectnum", [0, 1, 2])
    def test_get_sequenced_libraries_single_project(self, annotatordata,
                                                    mock_genomics_server,
                                                    projectnum):
        # (GIVEN)
        annotator, rundata = annotatordata

        # AND unaligned samples for a single project
        projectdata = rundata['unaligned']['projects'][projectnum]

        logger.info("test `get_sequenced_libraries()`, single project ({})"
                    .format(projectdata['name']))

        # WHEN collecting sequenced libraries for project
        sequencedlibraries = annotator.get_sequenced_libraries(
            projectdata['name'])

        # THEN should find excpeted number of sequenced libraries
        assert(len(sequencedlibraries) == len(projectdata['samples']))

    def test_get_sequenced_libraries_all_projects(self, annotatordata,
                                                  mock_genomics_server):
        # (GIVEN)
        annotator, rundata = annotatordata

        # AND list of unaligned projects
        projects = rundata['unaligned']['projects']

        logger.info("test `get_sequenced_libraries()`, all projects")

        # WHEN collecting sequenced libraries for all projects
        sequencedlibraries = annotator.get_sequenced_libraries()

        # THEN should find 31 total libraries
        assert(len(sequencedlibraries)
               == sum(map(lambda x: len(x['samples']), projects)))


@pytest.mark.usefixtures('mock_genomics_server', 'mock_db')
class TestSequencedLibraryAnnotator:
    """
    Tests methods for the `SequencedLibraryAnnotator` class in the
    `bripipetools.annotation.illuminaseq` module.
    """
    @pytest.fixture(
        scope='class',
        params=[{'runnum': r, 'projectnum': p, 'samplenum': s}
                for r in range(1)
                for p in range(3)
                for s in range(3)])
    def annotatordata(self, request, mock_genomics_server, mock_db):
        # GIVEN a SequencedLibraryAnnotator with mock 'genomics' server path,
        # and path to library folder (i.e., where data/organization is known),
        # with specified library, project, and run ID, as well as a mock
        # db connection
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param['runnum']]
        projects = rundata['unaligned']['projects']
        projectdata = projects[request.param['projectnum']]
        samples = projectdata['samples']
        sampledata = samples[request.param['samplenum']]

        logger.info("[setup] SequencedLibraryAnnotator mock instance "
                    " for sample {} in project {} from run {}"
                    .format(sampledata['name'], projectdata['name'],
                            rundata['flowcell_id']))

        seqlibannotator = annotation.SequencedLibraryAnnotator(
            path=sampledata['path'],
            library=os.path.basename(sampledata['path']),
            project=os.path.basename(projectdata['path']),
            run_id=rundata['run_id'],
            db=mock_db)

        def fin():
            logger.info("[teardown] SequencedLibraryAnnotator mock instance")
        request.addfinalizer(fin)
        return (seqlibannotator, rundata, sampledata)

    def test_init_attribute_munging(self, annotatordata):
        # (GIVEN)
        annotator, rundata, sampledata = annotatordata
        seqlib_id = '{}_{}'.format(sampledata['name'], rundata['flowcell_id'])

        logger.info("test `__init__()` for proper attribute munging")

        # WHEN checking whether input arguments were automatically munged
        # when setting annotator attributes

        # THEN the sequenced library ID should be properly constructed as the
        # library ID and flowcell ID
        assert(annotator.seqlib_id == seqlib_id)

    def test_init_sequencedlibrary_existing_sample(self, annotatordata,
                                                   mock_db):
        # (GIVEN)
        annotator, rundata, sampledata = annotatordata
        seqlib_id = '{}_{}'.format(sampledata['name'], rundata['flowcell_id'])

        logger.info("test `_init_sequencedlibrary()` with existing sample {}"
                    .format(seqlib_id))

        # WHEN sequenced library already exists in 'samples' collection
        mock_db.samples.insert_one(
            {'_id': seqlib_id,
             'type': 'sequenced library',
             'isMock': True})
        sequencedlibrary = annotator._init_sequencedlibrary()

        # THEN the sequenced library object should be returned and
        # should be correctly mapped from the database object
        assert(type(sequencedlibrary) == docs.SequencedLibrary)
        assert(sequencedlibrary._id == seqlib_id)
        assert(hasattr(sequencedlibrary, 'is_mock'))

        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.samples.drop()

    def test_init_sequencedlibrary_new_sample(self, annotatordata):
        # (GIVEN)
        annotator, rundata, sampledata = annotatordata
        seqlib_id = '{}_{}'.format(sampledata['name'], rundata['flowcell_id'])

        logger.info("test `_init_sequencedlibrary()` with new sample {}"
                    .format(seqlib_id))

        # WHEN sequenced library sample does not already exist in
        # 'samples' collection
        sequencedlibrary = annotator._init_sequencedlibrary()

        # THEN a new sequenced library object should be returned
        assert(type(sequencedlibrary) == docs.SequencedLibrary)
        assert(sequencedlibrary._id == seqlib_id)
        assert(not hasattr(sequencedlibrary, 'is_mock'))

    def test_get_raw_data(self, annotatordata, mock_genomics_server):
        # (GIVEN)
        annotator, _, sampledata = annotatordata

        logger.info("test `_get_raw_data()` for sample {}"
                    .format(sampledata['name']))

        # WHEN collecting raw data for a sequenced library
        raw_data = annotator._get_raw_data()

        # THEN should be a list of dicts, with the correct details for each
        # FASTQ file identified
        assert(set(f['path'] for f in raw_data)
                == set(f for f in os.listdir(sampledata['path'])
                       if not re.search('empty', f)))

    def test_update_sequencedlibrary(self, annotatordata):
        # (GIVEN)
        annotator, _, sampledata = annotatordata

        logger.info("test `_update_sequencedlibrary()` for sample {}"
                    .format(sampledata['name']))

        # WHEN sequenced library object is updated
        annotator._update_sequencedlibrary()

        # THEN the object should have at least the 'run_id', 'project_id',
        # 'subproject_id', 'parent_id' and 'raw_data' attributes
        assert(all([hasattr(annotator.sequencedlibrary, field)
                    for field in ['run_id', 'project_id', 'subproject_id',
                                  'parent_id', 'raw_data', 'date_created',
                                  'last_updated']]))
        assert(annotator.sequencedlibrary.last_updated
               > annotator.sequencedlibrary.date_created)

    def test_get_sequenced_library(self, annotatordata):
        # (GIVEN)
        annotator, _, sampledata = annotatordata

        logger.info("test `get_sequenced_library()` for sample {}"
                    .format(sampledata['name']))

        # WHEN sequenced library object is returned
        sequencedlibrary = annotator.get_sequenced_library()

        # THEN the object should be of type SequencedLibrary and have
        # at least the 'run_id', 'project_id', 'subproject_id', 'parent_id',
        # and 'raw_data' attributes
        assert(type(sequencedlibrary) is docs.SequencedLibrary)
        assert(all([hasattr(sequencedlibrary, field)
                    for field in ['run_id', 'project_id', 'subproject_id',
                                  'parent_id', 'raw_data']]))


@pytest.mark.usefixtures('mock_genomics_server', 'mock_db')
class TestWorkflowBatchAnnotator:
    """
    Tests methods for the `WorkflowBatchAnnotator` class in the
    `bripipetools.annotation.globusgalaxy` module.
    """
    @pytest.fixture(
        scope='class',
        params=[{'runnum': r, 'batchnum': b}
                for r in range(1)
                for b in range(2)])
    @pytest.fixture(scope='class')
    def annotatordata(self, request, mock_genomics_server, mock_db):
        # GIVEN a WorkflowBatchAnnotator with mock 'genomics' server path,
        # and path to workflow batch file with specified genomics root,
        # as well as a mock db connection
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param['runnum']]
        batches = rundata['submitted']['batches']
        batchdata = batches[request.param['batchnum']]

        logger.info("[setup] WorkflowBatchAnnotator mock instance "
                    "for batch {}".format(os.path.basename(batchdata['path'])))

        wflowbatchannotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=batchdata['path'],
            db=mock_db,
            genomics_root=mock_genomics_server['root']['path'])

        def fin():
            logger.info("[teardown] WorkflowBatchAnnotator mock instance")
        request.addfinalizer(fin)
        return (wflowbatchannotator, batchdata)

    def test_init_file_parsing(self, annotatordata):
        # (GIVEN)
        annotator, batchdata = annotatordata

        logger.info("test `__init__()` for proper file parsing "
                    "with batch {}"
                    .format(os.path.basename(batchdata['path'])))

        # WHEN checking whether input arguments were automatically munged
        # when setting annotator attributes
        workflowbatch_data = annotator.workflowbatch_data

        # THEN the workflow batch data should be a dictionary with fields for
        # workflow name, parameters, and samples
        assert(workflowbatch_data['workflow_name'] == batchdata['workflow'])
        assert(len(workflowbatch_data['parameters']) == batchdata['num_params'])
        assert(len(workflowbatch_data['samples']) == batchdata['num_samples'])
#
    def test_parse_batch_name(self, annotatordata, mock_genomics_server):
        # (GIVEN)
        annotator, batchdata = annotatordata

        logger.info("test `_parse_batch_name()` with batch name {}"
                    .format(batchdata['name']))

        # WHEN parsing batch name from workflow batch file
        batch_items = annotator._parse_batch_name(batchdata['name'])

        # THEN items should be in a dict with fields for date (string),
        # project labels (list of strings), and flowcell ID (string)
        assert(batch_items['date'] == batchdata['date'])
        assert(batch_items['projects'] == batchdata['projects'])
        assert(batch_items['flowcell_id'] == batchdata['flowcell_id'])
#
    def test_init_workflowbatch_existing_batch(self, annotatordata,
                                               mock_genomics_server, mock_db):
        # (GIVEN)
        annotator, batchdata = annotatordata

        logger.info("test `_init_workflowbatch()` with existing batch {}"
                    .format(batchdata['id']))

        # WHEN workflow batch exists in 'workflowbatches' collection
        mock_db.workflowbatches.insert_one(
            {'_id': batchdata['id'],
             'workflowbatchFile': re.sub('.*(?=genomics)', '/',
                                         batchdata['path']),
             'date': batchdata['date'],
             'type': 'Galaxy workflow batch',
             'isMock': True})
        workflowbatch = annotator._init_workflowbatch()

        # THEN existing workflow batch should be returned, and it
        # should be mapped from the database object
        assert(workflowbatch._id == batchdata['id'])
        assert(hasattr(workflowbatch, 'is_mock'))
        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.workflowbatches.drop()

    def test_init_workflowbatch_new_batch(self, annotatordata):
        # (GIVEN)
        annotator, batchdata = annotatordata

        logger.info("test `_init_workflowbatch()` with new batch {}"
                    .format(batchdata['id']))

        # WHEN workflow batch does not exist in 'workflowbatches' collection
        workflowbatch = annotator._init_workflowbatch()

        # THEN a new workflow batch should be returned
        assert(workflowbatch._id == batchdata['id'])
        assert(not hasattr(workflowbatch, 'is_mock'))

    def test_init_workflowbatch_existing_date(self, annotatordata, mock_db):
        # (GIVEN)
        annotator, batchdata = annotatordata

        logger.info("test `_init_workflowbatch()` existing prefix/date")

        # WHEN workflow batch does not exist in 'workflowbatches' collection,
        # but another batch with the same prefix and date does exist
        mock_db.workflowbatches.insert_one(
            {'_id': batchdata['id'],
             'workflowbatchFile': 'someotherfile',
             'date': batchdata['date'],
             'type': 'Galaxy workflow batch',
             'isMock': True})
        workflowbatch = annotator._init_workflowbatch()

        # THEN a new workflow batch should be returned with an incremented
        # ID number
        assert(workflowbatch._id == re.sub('\d$',
                                           lambda x: str(int(x.group(0)) + 1),
                                           batchdata['id']))
        assert(not hasattr(workflowbatch, 'is_mock'))

        logger.info("[rollback] remove most recently inserted "
        "from mock database")
        mock_db.workflowbatches.drop()

    def test_update_workflowbatch(self, annotatordata):
        # (GIVEN)
        annotator, batchdata = annotatordata

        logger.info("test `_update_workflowbatch()`")

        # WHEN workflow batch object is updated
        annotator._update_workflowbatch()

        # THEN the object should have at least the 'workflow_id', 'date',
        # 'projects', 'flowcell_id' attributes
        assert(all([hasattr(annotator.workflowbatch, field)
                    for field in ['workflow_id', 'date', 'projects',
                                  'flowcell_id', 'date_created',
                                  'last_updated']]))
        assert(annotator.workflowbatch.last_updated
               > annotator.workflowbatch.date_created)

    def test_get_workflow_batch(self, annotatordata):
        # (GIVEN)
        annotator, batchdata = annotatordata

        logger.info("test `get_workflow_batch()`")

        # WHEN workflow batch object is returned
        workflowbatch = annotator.get_workflow_batch()

        # THEN the object should be of type GalaxyWorkflowBatch and have
        # at least the at least the 'workflow_id', 'date',
        # 'projects', 'flowcell_id' attributes
        assert(type(workflowbatch) is docs.GalaxyWorkflowBatch)
        assert(all([hasattr(workflowbatch, field)
                    for field in ['workflow_id', 'date', 'projects',
                                  'flowcell_id']]))

    def test_get_sequenced_libraries(self, annotatordata):
        # (GIVEN)
        annotator, batchdata = annotatordata

        logger.info("test `get_sequenced_libraries()`")

        # WHEN collecting list of sequenced libraries for batch
        seqlibraries = annotator.get_sequenced_libraries()

        # THEN should be a list with expected number of sequenced libraries
        assert(len(seqlibraries) == batchdata['num_samples'])

    def test_get_processed_libraries(self, annotatordata):
        # (GIVEN)
        annotator, batchdata = annotatordata

        logger.info("test `get_processed_libraries()`")

        # WHEN collecting processed libraries for current workflow batch
        processedlibraries = annotator.get_processed_libraries()

        # THEN should return expected number of processed libraries,
        # each of which is a valid ProcessedLibrary object
        assert(len(processedlibraries) == batchdata['num_samples'])
        assert(all([type(pl) == docs.ProcessedLibrary
                    for pl in processedlibraries]))

    def test_check_sex(self, annotatordata, mock_db):
        # (GIVEN)
        annotator, batchdata = annotatordata

        # AND a processed library object
        # TODO: not independent, fix...
        processedlibrary = annotator.get_processed_libraries()[0]

        mock_db.samples.insert({
            '_id': processedlibrary.parent_id,
            'reportedSex': 'female'})

        # WHEN sex of processed library is verified
        processedlibrary = annotator._check_sex(processedlibrary)
        validationdata = processedlibrary.processed_data[0]['validation']

        assert(validationdata['sex_check']['sex_check'] is not None)

    def test_get_processed_libraries_w_qc(self, annotatordata):
        # (GIVEN)
        annotator, batchdata = annotatordata

        # WHEN collecting processed libraries for current workflow batch,
        # and QC flag is set to True
        processedlibraries = annotator.get_processed_libraries(qc=True)

        # THEN should return 2 total processed libraries, each of which
        # is a valid ProcessedLibrary object
        assert(len(processedlibraries) == batchdata['num_samples'])
        assert(all([type(pl) == docs.ProcessedLibrary
                    for pl in processedlibraries]))
        assert('validation' in processedlibraries[0].processed_data[0])


@pytest.mark.usefixtures('mock_genomics_server', 'mock_db')
class TestProcessedLibraryAnnotator:
    """
    Tests methods for the `ProcessedLibraryAnnotator` class in the
    `bripipetools.annotation.globusgalaxy` module.
    """
    @pytest.fixture(
        scope='class',
        params=[{'runnum': r, 'batchnum': b, 'samplenum': s}
                for r in range(1)
                for b in range(2)
                for s in range(6)
                if not (b == 1 and s > 2)])
    @pytest.fixture(scope='class')
    def annotatordata(self, request, mock_genomics_server, mock_db):
        # GIVEN a ProcessedLibraryAnnotator with mock 'genomics' server path,
        # and path to library folder (i.e., where data/organization is known),
        # with specified library, project, and run ID,
        # as well as a mock db connection
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param['runnum']]
        batches = rundata['submitted']['batches']
        batchdata = batches[request.param['batchnum']]
        samples = batchdata['samples']
        samplename = samples[request.param['samplenum']]
        proclib_id = ('{}_{}_processed'
                      .format(samplename, rundata['flowcell_id']))

        logger.info("[setup] ProcessedLibraryAnnotator mock instance "
                    "for sample {}".format(samplename))

        workflowbatch_id = batchdata['id']
        # TODO: try to remove the test dependency on the io module here
        workflowbatch_data = io.WorkflowBatchFile(
            path=batchdata['path'],
            state='submit').parse()

        proclibannotator = annotation.ProcessedLibraryAnnotator(
            workflowbatch_id=workflowbatch_id,
            params=workflowbatch_data['samples'][request.param['samplenum']],
            db=mock_db)

        def fin():
            logger.info("[teardown] ProcessedLibraryAnnotator mock instance")
        request.addfinalizer(fin)
        return (proclibannotator, batchdata, proclib_id)

    def test_init_attribute_munging(self, annotatordata):
        # (GIVEN)
        annotator, _, proclib_id = annotatordata

        logger.info("test `__init__()` for proper attribute munging "
                    " with sample {}".format(proclib_id))

        # WHEN checking whether input arguments were automatically munged
        # when setting annotator attributes

        # THEN the processed library ID should be properly constructed as the
        # library ID and flowcell ID, tagged as processed
        assert(annotator.proclib_id == proclib_id)

    def test_init_processedlibrary_existing_sample(self, annotatordata,
                                                   mock_db):
        # (GIVEN)
        annotator, _, proclib_id = annotatordata

        logger.info("test `_init_processedlibrary()` with existing sample {}"
                    .format(proclib_id))

        # WHEN processed library already exists in 'samples' collection
        mock_db.samples.insert_one(
            {'_id': proclib_id,
             'type': 'processed library',
             'isMock': True})
        processedlibrary = annotator._init_processedlibrary()

        # THEN the processed library object should be returned and
        # should be correctly mapped from the database object
        assert(type(processedlibrary) == docs.ProcessedLibrary)
        assert(processedlibrary._id == proclib_id)
        assert(hasattr(processedlibrary, 'is_mock'))

        logger.info("[rollback] remove most recently inserted "
                    "from mock database")
        mock_db.samples.drop()

    def test_init_processedlibrary_new_sample(self, annotatordata):
        # (GIVEN)
        annotator, _, proclib_id = annotatordata

        logger.info("test `_init_processedlibrary()` with new sample")

        # WHEN processed library sample does not already exist in
        # 'samples' collection
        processedlibrary = annotator._init_processedlibrary()

        # THEN a new processed library object should be returned
        assert(type(processedlibrary) == docs.ProcessedLibrary)
        assert(processedlibrary._id == proclib_id)
        assert(not hasattr(processedlibrary, 'is_mock'))

    def test_get_outputs(self, annotatordata):
        # (GIVEN)
        annotator, batchdata, proclib_id = annotatordata

        logger.info("test `_get_outputs()`")

        # WHEN collecting the list of outputs for a processed library

        # THEN the outputs should be stored in a dict with expected length
        assert(len(annotator._get_outputs()) == batchdata['num_outputs'])

    def test_parse_output_name_onepart_source(self, annotatordata):
        # (GIVEN)
        annotator, _, _ = annotatordata

        logger.info("test `_parse_output_name()`, one-part source")

        # WHEN parsing output name from workflow batch parameter, and the
        # source name has one parts (i.e., 'tophat')
        output_items = annotator._parse_output_name(
            'tophat_alignments_bam_out')

        # THEN output items should be a dictionary including fields for
        # name, type, and source
        assert(output_items['name'] == 'tophat_alignments_bam')
        assert(output_items['type'] == 'alignments')
        assert(output_items['source'] == 'tophat')

    def test_parse_output_name_twopart_source(self, annotatordata):
        # (GIVEN)
        annotator, _, _ = annotatordata

        logger.info("test `_parse_output_name()`, two-part source")

        # WHEN parsing output name from workflow batch parameter, and the
        # source name has two parts (i.e., 'picard_rnaseq')
        output_items = annotator._parse_output_name(
            'picard_rnaseq_metrics_html_out')

        # THEN output items should be a dictionary including fields for
        # name, type, and source
        assert(output_items['name'] == 'picard_rnaseq_metrics_html')
        assert(output_items['type'] == 'metrics')
        assert(output_items['source'] == 'picard_rnaseq')

    def test_group_outputs(self, annotatordata, mock_genomics_server):
        # (GIVEN)
        annotator, _, _ = annotatordata

        logger.info("test `_group_outputs()`")

        # WHEN collecting the organized dictionary of outputs
        outputs = annotator._group_outputs()

        # THEN the outputs should be correctly grouped according to type
        # and source (tool)
        assert(set(outputs.keys())
               == set(mock_genomics_server['out_types']))
        assert(set([k['source'] for k in outputs['metrics']])
               == set(['picard_align', 'tophat_stats', 'picard_markdups',
                       'picard_rnaseq', 'htseq']))

    def test_append_processed_data(self, annotatordata):
        # (GIVEN)
        annotator, _, _ = annotatordata

        logger.info("test `_append_processed_data()`")

        # WHEN batch information and outputs are added to processed data
        # field for processed library object
        annotator._append_processed_data()

        # THEN the length of the processed data field should be 1, containing
        # a dictionary with workflow batch ID and outputs
        assert(len(annotator.processedlibrary.processed_data) == 1)
        assert(set(annotator.processedlibrary.processed_data[0].keys())
               == set(['workflowbatch_id', 'outputs']))
        annotator.processedlibrary.processed_data = []

    def test_append_processed_data_exists(self, annotatordata):
        # (GIVEN)
        annotator, batchdata, _ = annotatordata

        logger.info("test `_append_processed_data()`")

        # AND outputs for the workflow batch are already present
        annotator.processedlibrary.processed_data.append(
            {'workflowbatch_id': batchdata['id'],
             'outputs': []})

        # WHEN batch information and outputs are added to processed data
        # field for processed library object
        annotator._append_processed_data()

        # THEN the length of the processed data field should be 1, containing
        # a dictionary with workflow batch ID and outputs
        assert(len(annotator.processedlibrary.processed_data) == 1)
        assert(set(annotator.processedlibrary.processed_data[0].keys())
               == set(['workflowbatch_id', 'outputs']))
        annotator.processedlibrary.processed_data = []

    def test_append_processed_data_new(self, annotatordata):
        # (GIVEN)
        annotator, batchdata, _ = annotatordata

        logger.info("test `_append_processed_data()`")

        # AND outputs from a different workflow batch are already present
        annotator.processedlibrary.processed_data.append(
            {'workflowbatch_id': re.sub('\d$',
                                        lambda x: str(int(x.group(0)) + 1),
                                        batchdata['id']),
             'outputs': []})

        # WHEN batch information and outputs are added to processed data
        # field for processed library object
        annotator._append_processed_data()

        # THEN the length of the processed data field should be 2, containing
        # a dictionary with workflow batch ID and outputs
        assert(len(annotator.processedlibrary.processed_data) == 2)
        assert(set(annotator.processedlibrary.processed_data[1].keys())
               == set(['workflowbatch_id', 'outputs']))
        annotator.processedlibrary.processed_data = []

    def test_update_processedlibrary(self, annotatordata):
        # (GIVEN)
        annotator, _, _ = annotatordata

        logger.info("test `_update_processedlibrary()`")

        # WHEN processed library object is updated
        annotator._update_processedlibrary()

        # THEN the object should have at least the 'parent_id' and
        # 'processed_data', and 'processed_data' should be length 1
        assert(all([hasattr(annotator.processedlibrary, field)
                    for field in ['parent_id', 'processed_data',
                                  'date_created', 'last_updated']]))
        assert(len(annotator.processedlibrary.processed_data) == 1)
        assert(annotator.processedlibrary.last_updated
               > annotator.processedlibrary.date_created)
