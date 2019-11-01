import logging

import pytest
import mongomock

from bripipetools import model as docs
from bripipetools import dbification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def mock_db():
    # GIVEN a mocked version of the TG3 Mongo database
    logger.info(("[setup] mock database, connect "
                 "to mock Mongo database"))

    yield mongomock.MongoClient().db
    logger.debug(("[teardown] mock database, disconnect "
                  "from mock Mongo database"))


class TestFlowcellRunImporter:
    """
    Tests methods for the `FlowcellRunImporter` class in the
    `bripipetools.dbification.flowcellrun` module.
    """
    def test_collect_flowcellrun(self, mock_db):
        # GIVEN a path to a flowcell run folder and a connection to a
        # database in which a document corresponding to the flowcell run
        # may or may not exist (note: behavior of of the associated
        # FlowcellRunAnnotator class when collecting data about a new or
        # previously imported flowcell run is assumed to be tested in the
        # `test_annotation` module)
        mock_root = '/mnt/'
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = '{}bioinformatics/pipeline/Illumina/{}'.format(mock_root, mock_id)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an importer object is created for the path
        importer = dbification.FlowcellRunImporter(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN collecting model object for flowcell run
        test_object = importer._collect_flowcellrun()

        # THEN should return object of correct type
        assert (type(test_object) == docs.FlowcellRun)

    def test_collect_sequenced_libraries(self, mock_db, tmpdir):
        # GIVEN a path to a flowcell run folder and a connection to a
        # database in which a document corresponding to the flowcell run
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id))

        # AND an unaligned folder, which includes multiple project folders,
        # each with multiple folders for sequenced libraries
        mock_projects = ['P1-1-11111111', 'P99-99-99999999']
        mock_libs = {0: ['lib1111-11111111', 'lib2222-22222222'],
                     1: ['lib3333-33333333', 'lib4444-44444444']}
        unalignedpath = mock_path.mkdir('Unaligned')
        for idx, p in enumerate(mock_projects):
            projpath = unalignedpath.mkdir(p)
            for l in mock_libs[idx]:
                projpath.mkdir(l)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an importer object is created for the path
        importer = dbification.FlowcellRunImporter(
            path=str(mock_path),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN collecting model objects for sequenced libraries
        test_objects = importer._collect_sequencedlibraries()

        # THEN should return object of correct type
        assert (all(type(sl) == docs.SequencedLibrary for sl in test_objects))

    def test_insert_flowcellrun(self, mock_db):
        # GIVEN a path to a flowcell run folder and a connection to a
        # database in which a document corresponding to the flowcell run
        # may or may not exist (note: behavior for inserting or updating
        # documents in the database is assumed to be tested in the
        # `test_genlims` module)
        mock_root = '/mnt/'
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = ('{}bioinformatics/pipeline/Illumina/{}'
                    .format(mock_root, mock_id))

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an importer object is created for the path
        importer = dbification.FlowcellRunImporter(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN flowcell run is inserted into database
        importer._insert_genomicsFlowcellRun()

        # THEN document should be present in the genomicsRuns collection
        assert (len(list(mock_db.genomicsRuns.find({'type': 'flowcell'}))) == 1)

    def test_insert_sequencedlibraries(self, mock_db, tmpdir):
        # GIVEN a path to a flowcell run folder and a connection to a
        # database in which a document corresponding to the flowcell run
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id))

        # AND an unaligned folder, which includes multiple project folders,
        # each with multiple folders for sequenced libraries
        mock_projects = ['P1-1-11111111', 'P99-99-99999999']
        mock_libs = {0: ['lib1111-11111111', 'lib2222-22222222'],
                     1: ['lib3333-33333333', 'lib4444-44444444']}
        unalignedpath = mock_path.mkdir('Unaligned')
        for idx, p in enumerate(mock_projects):
            projpath = unalignedpath.mkdir(p)
            for l in mock_libs[idx]:
                projpath.mkdir(l)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an importer object is created for the path
        importer = dbification.FlowcellRunImporter(
            path=str(mock_path),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN sequenced libraries are inserted into database
        importer._insert_genomicsSequencedlibraries()

        # THEN document should be present in the genomicsSamples collection
        assert (len(list(mock_db.genomicsSamples.find({'type': 'sequenced library'})))
                == 4)

    def test_insert(self, mock_db, tmpdir):
        # GIVEN a path to a flowcell run folder and a connection to a
        # database in which a document corresponding to the flowcell run
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id))
                    

        # AND an unaligned folder, which includes multiple project folders,
        # each with multiple folders for sequenced libraries
        mock_projects = ['P1-1-11111111', 'P99-99-99999999']
        mock_libs = {0: ['lib1111-11111111', 'lib2222-22222222'],
                     1: ['lib3333-33333333', 'lib4444-44444444']}
        unalignedpath = mock_path.mkdir('Unaligned')
        for idx, p in enumerate(mock_projects):
            projpath = unalignedpath.mkdir(p)
            for l in mock_libs[idx]:
                projpath.mkdir(l)
                
        # AND a batch submission directory in the run folder
        mock_path.mkdir("globus_batch_submission")

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an importer object is created for the path
        importer = dbification.FlowcellRunImporter(
            path=str(mock_path),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN all objects are inserted into database
        importer.insert()

        # THEN documents should be present in the runs and samples collections
        assert (len(list(mock_db.genomicsRuns.find({'type': 'flowcell'}))) == 1)
        assert (len(list(mock_db.genomicsSamples.find({'type': 'sequenced library'})))
                == 4)


#@pytest.fixture(scope='function')
def mock_batchfile(filename, tmpdir):
    # GIVEN a simplified workflow batch content with protypical contents
    mock_contents = ['###METADATA\n',
                     '#############\n',
                     'Workflow Name\toptimized_workflow_1\n',
                     'Project Name\t161231_P00-00_C00000XX\n',
                     '###TABLE DATA\n',
                     '#############\n',
                     'SampleName\tin_tag##_::_::_::param_name\n',
                     'sample1\tin_value1\n',
                     'sample2\tin_value2\n']
    mock_file = tmpdir.join(filename)
    mock_file.write(''.join(mock_contents))
    return str(mock_file)

#@pytest.fixture(scope='function')
def mock_workflowfile(filename, tmpdir):
    # GIVEN a simplified workflow batch content with protypical contents
    mock_contents = ['{',
                     '"name": "optimized_workflow_1",',
                     '"steps":{',
                     '"0":{',
                     '"tool_id": "some_tool",',
                     '"tool_version": "1.0.0"',
                     '}}}']
    mock_file = tmpdir.join(filename)
    mock_file.write(''.join(mock_contents))
    return str(mock_file)
    

class TestWorkflowBatchImporter:
    """
    Tests methods for the `WorkflowBatchImporter` class in the
    `bripipetools.dbification.workflowbatch` module.
    """
    def test_collect_workflowbatch(self, mock_db, tmpdir):
        # GIVEN a path to a workflow batch file and a connection to a
        # database in which a document corresponding to the workflow batch
        # may or may not exist (note: behavior of of the associated
        # WorkflowBatchAnnotator class when collecting data about a new or
        # previously imported workflow batch is assumed to be tested in the
        # `test_annotation` module)
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id)
                    .mkdir('globus_batch_submission'))

        mock_filename = '161231_P1-1_P99-99_C00000XX_workflow-name.txt'
        mock_path = mock_batchfile(mock_filename, mock_path)
        
        # AND a workflow file corresponding to the workflow batch
        mock_wkflow_filename = 'optimized_workflow_1.ga'
        mock_workflow = mock_workflowfile(mock_wkflow_filename, tmpdir)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', 
                         "sexcutoff":1,
                         "workflow_dir":str(tmpdir)}

        # AND an importer object is created for the path
        importer = dbification.WorkflowBatchImporter(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN collecting model object for workflow batch
        test_object = importer._collect_workflowbatch()

        # THEN should return object of correct type
        assert (type(test_object) == docs.GalaxyWorkflowBatch)

    def test_collect_processedlibraries(self, mock_db, tmpdir):
        # GIVEN a path to a workflow batch file and a connection to a
        # database in which a document corresponding to the workflow batch
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id).mkdir('globus_batch_submission'))
        mock_filename = '161231_P1-1_P99-99_C00000XX_workflow-name.txt'
        mock_path = mock_batchfile(mock_filename, mock_path)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an importer object is created for the path
        importer = dbification.WorkflowBatchImporter(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN collecting model objects for processed libraries
        # from the workflow batch
        test_objects = importer._collect_processedlibraries()

        # THEN should return objects of correct type
        assert (all(type(pl) == docs.ProcessedLibrary for pl in test_objects))

    def test_insert_genomicsWorkflowbatch(self, mock_db, tmpdir):
        # GIVEN a path to a workflow batch file and a connection to a
        # database in which a document corresponding to the workflow batch
        # may or may not exist (note: behavior for inserting or updating
        # documents in the database is assumed to be tested in the
        # `test_genlims` module)
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id).mkdir('globus_batch_submission'))
        mock_filename = '161231_P1-1_P99-99_C00000XX_workflow-name.txt'
        mock_path = mock_batchfile(mock_filename, mock_path)

        # AND a workflow file corresponding to the workflow batch
        mock_wkflow_filename = 'optimized_workflow_1.ga'
        mock_workflow = mock_workflowfile(mock_wkflow_filename, tmpdir)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', 
                         "sexcutoff":1,
                         "workflow_dir":str(tmpdir)}

        # AND an importer object is created for the path
        importer = dbification.WorkflowBatchImporter(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN workflow batch is inserted into database
        importer._insert_genomicsWorkflowbatch()

        # THEN document should be present in the workflowbatches collection
        assert (len(list(mock_db.genomicsWorkflowbatches
                         .find({'type': 'Galaxy workflow batch'})))
                == 1)

    def test_insert_processedlibraries(self, mock_db, tmpdir):
        # GIVEN a path to a workflow batch file and a connection to a
        # database in which a document corresponding to the workflow batch
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id).mkdir('globus_batch_submission'))
        mock_filename = '161231_P1-1_P99-99_C00000XX_workflow-name.txt'
        mock_path = mock_batchfile(mock_filename, mock_path)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an importer object is created for the path
        importer = dbification.WorkflowBatchImporter(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN processed libraries inserted into database
        importer._insert_genomicsProcessedlibraries()

        # THEN documents should be present in the genomicsSamples collection
        assert (len(list(mock_db.genomicsSamples.find({'type': 'processed library'})))
                == 2)

    def test_insert(self, mock_db, tmpdir):
        # GIVEN a path to a workflow batch file and a connection to a
        # database in which a document corresponding to the workflow batch
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id)
                    .mkdir('globus_batch_submission'))

        mock_filename = '161231_P1-1_P99-99_C00000XX_workflow-name.txt'
        mock_path = mock_batchfile(mock_filename, mock_path)

        # AND a workflow file corresponding to the workflow batch
        mock_wkflow_filename = 'optimized_workflow_1.ga'
        mock_workflow = mock_workflowfile(mock_wkflow_filename, tmpdir)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', 
                         "sexcutoff":1,
                         "workflow_dir":str(tmpdir)}

        # AND an importer object is created for the path
        importer = dbification.WorkflowBatchImporter(
            path=str(mock_path),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN all objects are inserted into all database collections
        importer.insert(collection = 'all')

        # THEN documents should be present in the genomicsWorkflowbatches
        # and genomicsSamples collections
        assert (len(list(mock_db.genomicsWorkflowbatches
                         .find({'type': 'Galaxy workflow batch'})))
                == 1)
        assert (len(list(mock_db.genomicsSamples
                        .find({'type': 'processed library'})))
                == 2)


class TestImportManager:
    """
    Tests methods for the `ImportManager` class in the
    `bripipetools.dbification.control` module.
    """
    def test_sniff_path_for_flowcell_run(self, mock_db):
        # GIVEN a path to a flowcell run folder and a connection to a
        # database in which a document corresponding to the flowcell run
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = '/mnt/bioinformatics/pipeline/Illumina/{}'.format(mock_id)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an import manager is created for the path
        manager = dbification.ImportManager(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN path is checked to determine type
        test_type = manager._sniff_path()

        # THEN path type should be 'flowcell_path'
        assert (test_type == 'flowcell_path')

    def test_sniff_path_for_workflow_batch(self, mock_db):
        # GIVEN a path to a workflow batch file and a connection to a
        # database in which a document corresponding to the workflow batch
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_filename = '161231_P1-1_P99-99_C00000XX_workflow-name.txt'
        mock_path = ('/mnt/bioinformatics/pipeline/Illumina/{}/globus_batch_submission/{}'
                     .format(mock_id, mock_filename))

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an import manager is created for the path
        manager = dbification.ImportManager(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN path is checked to determine type
        test_type = manager._sniff_path()

        # THEN path type should be 'workflowbatch_file'
        assert (test_type == 'workflowbatch_file')

    def test_init_importer_for_flowcell_run(self, mock_db):
        # GIVEN a path to a flowcell run folder and a connection to a
        # database in which a document corresponding to the flowcell run
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = '/mnt/bioinformatics/pipeline/Illumina/{}'.format(mock_id)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        manager = dbification.ImportManager(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # AND an import manager is created for the path
        manager._init_importer()

        # THEN importer should be correct type
        assert (type(manager.importer) == dbification.FlowcellRunImporter)

    def test_init_importer_for_workflow_batch(self, mock_db):
        # GIVEN a path to a workflow batch file and a connection to a
        # database in which a document corresponding to the workflow batch
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_filename = '161231_P1-1_P99-99_C00000XX_workflow-name.txt'
        mock_path = ('/mnt/bioinformatics/pipeline/Illumina/{}/globus_batch_submission/{}'
                     .format(mock_id, mock_filename))

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        manager = dbification.ImportManager(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN importer object is initialized
        manager._init_importer()

        # THEN importer should be correct type
        assert (type(manager.importer) == dbification.WorkflowBatchImporter)

    def test_run_for_flowcell_run(self, mock_db, tmpdir):
        # GIVEN a path to a flowcell run folder and a connection to a
        # database in which a document corresponding to the flowcell run
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id))

        # AND an unaligned folder, which includes multiple project folders,
        # each with multiple folders for sequenced libraries
        mock_projects = ['P1-1-11111111', 'P99-99-99999999']
        mock_libs = {0: ['lib1111-11111111', 'lib2222-22222222'],
                     1: ['lib3333-33333333', 'lib4444-44444444']}
        unalignedpath = mock_path.mkdir('Unaligned')
        for idx, p in enumerate(mock_projects):
            projpath = unalignedpath.mkdir(p)
            for l in mock_libs[idx]:
                projpath.mkdir(l)
                
        # AND a batch submission directory in the run folder
        mock_path.mkdir("globus_batch_submission")

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an import manager is created for the path
        manager = dbification.ImportManager(
            path=str(mock_path),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN all objects are inserted into database
        manager.run()

        # THEN documents should be present in the genomics runs and samples collections
        assert (len(list(mock_db.genomicsRuns.find({'type': 'flowcell'}))) == 1)
        assert (len(list(mock_db.genomicsSamples.find({'type': 'sequenced library'})))
                == 4)

    def test_run_for_workflow_batch(self, mock_db, tmpdir):
        # GIVEN a path to a workflow batch file and a connection to a
        # database in which a document corresponding to the workflow batch
        # may or may not exist
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('bioinformatics')
                    .mkdir('pipeline')
                    .mkdir('Illumina')
                    .mkdir(mock_id)
                    .mkdir('globus_batch_submission'))

        mock_filename = '161231_P1-1_P99-99_C00000XX_workflow-name.txt'
        mock_path = mock_batchfile(mock_filename, mock_path)

        # AND a workflow file corresponding to the workflow batch
        mock_wkflow_filename = 'optimized_workflow_1.ga'
        mock_workflow = mock_workflowfile(mock_wkflow_filename, tmpdir)

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', 
                         "sexcutoff":1,
                         "workflow_dir":str(tmpdir)}

        # AND an importer object is created for the path
        manager = dbification.ImportManager(
            path=mock_path,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN all objects are inserted into all relevant database collections
        manager.run(collections = 'all')

        # THEN documents should be present in the 
        # genomicsWorkflowbatches, genomicsSamples, and samples collections
        assert (len(list(mock_db.genomicsWorkflowbatches
                         .find({'type': 'Galaxy workflow batch'})))
                == 1)
        assert (len(list(mock_db.genomicsSamples.find({'type': 'processed library'})))
                == 2)
