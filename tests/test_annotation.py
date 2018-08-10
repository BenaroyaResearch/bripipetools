import logging
import datetime

import pytest
import mongomock
import mock

from bripipetools import model as docs
from bripipetools import annotation

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def mock_db():
    # GIVEN a mock_ed version of the TG3 Mongo database
    logger.info(("[setup] mock_ database, connect "
                 "to mock_ Mongo database"))

    yield mongomock.MongoClient().db
    logger.debug(("[teardown] mock_ database, disconnect "
                  "from mock_ Mongo database"))


class TestSequencedLibraryAnnotator:
    """
    Tests methods for the `SequencedLibraryAnnotator` class in the
    `bripipetools.annotation.illuminaseq` module.
    """
    def test_init_sequencedlibrary_for_existing_sample(self, mock_db):
        # GIVEN a sequenced library ID and a connection to a database in which
        # a document corresponding to the sequenced library exists already
        mock_id = 'lib1111_C00000XX'

        mock_db.samples.insert_one(
            {'_id': mock_id,
             'type': 'sequenced library'}
        )

        # AND an annotator object is created for the sequenced library with
        # project and library folder names, run ID, and an arbitrary path to
        # the libraries raw data
        mock_lib = 'lib1111-1111'
        mock_project = 'P1-1-1111'
        mock_runid = '161231_INSTID_0001_AC00000XX'
        annotator = annotation.SequencedLibraryAnnotator(
            path='mock-path-to-raw-data.fastq.gz',
            library=mock_lib,
            project=mock_project,
            run_id=mock_runid,
            db=mock_db
        )

        # WHEN the model object is initiated for the annotator
        test_object = annotator._init_sequencedlibrary()

        # THEN the sequenced library object should be returned and
        # should be correctly mapped from the database object
        assert (type(test_object) == docs.SequencedLibrary)
        assert (test_object._id == mock_id)
        assert test_object.is_mapped

    def test_init_sequencedlibrary_for_existing_sample(self, mock_db):
        # GIVEN a sequenced library ID and a connection to a database in which
        # a document corresponding to the sequenced library does not exist
        mock_id = 'lib1111_C00000XX'

        # AND an annotator object is created for the sequenced library with
        # project and library folder names, run ID, and an arbitrary path to
        # the libraries raw data
        mock_lib = 'lib1111-1111'
        mock_project = 'P1-1-1111'
        mock_runid = '161231_INSTID_0001_AC00000XX'
        annotator = annotation.SequencedLibraryAnnotator(
            path='mock-path-to-raw-data.fastq.gz',
            library=mock_lib,
            project=mock_project,
            run_id=mock_runid,
            db=mock_db
        )

        # WHEN the model object is initiated for the annotator
        test_object = annotator._init_sequencedlibrary()

        # THEN the sequenced library object should be returned and
        # should be correctly mapped from the database object
        assert (type(test_object) == docs.SequencedLibrary)
        assert (test_object._id == mock_id)
        assert not test_object.is_mapped

    def test_get_raw_data(self, mock_db, tmpdir):
        # GIVEN an annotator object created for the sequenced library with
        # project and library folder names, run ID, and the full path to the
        # folder containing raw data (i.e., one or more FASTQ files)
        mock_lib = 'lib1111'
        mock_project = 'P1-1'
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('genomics').mkdir('Illumina')
                     .mkdir(mock_runid)
                     .mkdir('Unaligned')
                     .mkdir(mock_project)
                     .mkdir(mock_lib))
        mock_data = '/sample-name_S001_L001_R1_001.fastq.gz'
        mock_path.ensure(mock_data)
        mock_data_path = ('/genomics/Illumina/'
                         + mock_runid
                         + '/Unaligned/'
                         + mock_project + '/'
                         + mock_lib
                         + mock_data)
        annotator = annotation.SequencedLibraryAnnotator(
            path=str(mock_path),
            library=mock_lib,
            project=mock_project,
            run_id=mock_runid,
            db=mock_db
        )

        # WHEN raw data details are recovered for the library
        test_data = annotator._get_raw_data()

        # THEN the path field of the raw data file should match
        # the expected result
        assert (test_data[0]['path'] == mock_data_path)

    def test_update_sequencedlibrary(self, mock_db, tmpdir):
        # GIVEN an annotator object created for a sequenced library with
        # project and library folder names, run ID, and the full path to the
        # folder containing raw data (i.e., one or more FASTQ files)
        mock_lib = 'lib1111'
        mock_project = 'P1-1'
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mock_runid)
                    .mkdir('Unaligned')
                    .mkdir(mock_project)
                    .mkdir(mock_lib))
        mock_data = 'sample-name_S001_L001_R1_001.fastq.gz'
        mock_path.ensure(mock_data)
        annotator = annotation.SequencedLibraryAnnotator(
            path=str(mock_path),
            library=mock_lib,
            project=mock_project,
            run_id=mock_runid,
            db=mock_db
        )

        # AND the annotator object has a mapped model object with the
        # corresponding sequenced library ID
        mock_id = 'lib1111_C00000XX'
        mock_object = mock.create_autospec(docs.SequencedLibrary)
        mock_object._id = mock_id
        mock_object.is_mapped = True
        annotator.sequencedlibrary = mock_object

        # WHEN the mapped model object is updated to add any missing fields
        annotator._update_sequencedlibrary()

        # THEN the model object should now have expected fields including
        # for raw data, and should no longer be flagged as mapped
        assert (hasattr(annotator.sequencedlibrary, 'raw_data'))
        assert not annotator.sequencedlibrary.is_mapped

    def test_get_sequenced_library(self, mock_db, tmpdir):
        # GIVEN an annotator object created for a sequenced library with
        # project and library folder names, run ID, and the full path to the
        # folder containing raw data (i.e., one or more FASTQ files)
        mock_lib = 'lib1111'
        mock_project = 'P1-1'
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mock_runid)
                    .mkdir('Unaligned')
                    .mkdir(mock_project)
                    .mkdir(mock_lib))
        mock_data = 'sample-name_S001_L001_R1_001.fastq.gz'
        mock_path.ensure(mock_data)
        annotator = annotation.SequencedLibraryAnnotator(
            path=str(mock_path),
            library=mock_lib,
            project=mock_project,
            run_id=mock_runid,
            db=mock_db
        )

        # AND the annotator object has a mapped model object with the
        # corresponding sequenced library ID
        mock_id = 'lib1111_C00000XX'
        mock_object = mock.create_autospec(docs.SequencedLibrary)
        mock_object._id = mock_id
        mock_object.is_mapped = True
        annotator.sequencedlibrary = mock_object

        # WHEN the mapped model object is retrieved
        test_object = annotator.get_sequenced_library()

        # THEN the model object should now have expected fields including
        # for raw data, and should no longer be flagged as mapped
        assert (hasattr(test_object, 'raw_data'))
        assert not test_object.is_mapped


class TestFlowcellRunAnnotator:
    """
    Tests methods for the `FlowcellRunAnnotator` class in the
    `bripipetools.annotation.flowcellruns` module.
    """
    def test_init_flowcellrun_for_existing_run(self, mock_db):
        # GIVEN a flowcell run ID and a connection to a database in which
        # a document corresponding to the flowcell run exists already
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_db.runs.insert_one(
            {'_id': mock_id,
             'type': 'flowcell'}
        )

        # AND an annotator object is created for the flowcell run with
        # an arbitrary 'genomics' root specified
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root='/mnt'
        )

        # WHEN the model object is initiated for the annotator
        test_object = annotator._init_flowcellrun()

        # THEN the flowcell run object should be returned and
        # should be correctly mapped from the database object
        assert (type(test_object) == docs.FlowcellRun)
        assert (test_object._id == mock_id)
        assert test_object.is_mapped

    def test_init_flowcellrun_for_new_run(self, mock_db):
        # GIVEN a flowcell run ID and a connection to a database in which
        # a document corresponding to the flowcell run does not exist
        mock_id = '161231_INSTID_0001_AC00000XX'

        # AND an annotator object is created for the flowcell run with
        # an arbitrary 'genomics' root specified
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root='/mnt'
        )

        # WHEN the model object is initiated for the annotator
        test_object = annotator._init_flowcellrun()

        # THEN the new flowcell run object should be returned
        assert (type(test_object) == docs.FlowcellRun)
        assert (test_object._id == mock_id)
        assert not test_object.is_mapped

    def test_get_flowcell_path_for_existing_folder(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at the path 'genomics/Illumina/<run_id>'
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mock_id)

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mock_object = mock.create_autospec(docs.FlowcellRun)
        mock_object._id = mock_id
        annotator.flowcellrun = mock_object

        # WHEN the flowcell folder path is retrieved
        testpath = annotator.get_flowcell_path()

        # THEN correct flowcell folder should be found in 'genomics/Illumina/'
        assert (testpath == str(mock_path))

    def test_get_flowcell_path_for_invalid_root(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary directory that does not
        # contain 'genomics/Illumina/'
        mock_id = '161231_INSTID_0001_AC00000XX'

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mock_object = mock.create_autospec(docs.FlowcellRun)
        mock_object._id = mock_id
        annotator.flowcellrun = mock_object

        # WHEN the flowcell folder path is retrieved

        # THEN should raise expected exception
        with pytest.raises(OSError):
            annotator.get_flowcell_path()

    def test_get_unaligned_path_for_existing_folder(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = (tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mock_id)
                    .mkdir('Unaligned'))

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mock_object = mock.create_autospec(docs.FlowcellRun)
        mock_object._id = mock_id
        annotator.flowcellrun = mock_object

        # WHEN the flowcell folder path is retrieved
        testpath = annotator.get_unaligned_path()

        # THEN correct flowcell folder should be found in 'genomics/Illumina/'
        assert (testpath == str(mock_path))

    def test_get_unaligned_path_for_missing_folder(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and there is no subfolder named 'Unaligned'
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_path = tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mock_id)

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mock_object = mock.create_autospec(docs.FlowcellRun)
        mock_object._id = mock_id
        annotator.flowcellrun = mock_object

        # WHEN the unaligned folder path is retrieved

        # THEN should raise expected exception
        with pytest.raises(OSError):
            annotator.get_unaligned_path()

    def test_get_flowcell_run(self, mock_db):
        # GIVEN any state and a flowcell run annotator object
        mock_id = '161231_INSTID_0001_AC00000XX'
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root='/mnt'
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mock_object = mock.create_autospec(docs.FlowcellRun)
        mock_object._id = mock_id
        annotator.flowcellrun = mock_object

        # WHEN model object is retrieved
        test_object = annotator.get_flowcell_run()

        # THEN should be expected object
        assert (test_object == mock_object)

    def test_get_projects(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mock_id = '161231_INSTID_0001_AC00000XX'

        # AND the unaligned folder includes multiple project folders
        mock_projects = ['P1-1-11111111', 'P99-99-99999999']
        mock_path = (tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mock_id)
                    .mkdir('Unaligned'))
        for p in mock_projects:
            mock_path.mkdir(p)

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mock_object = mock.create_autospec(docs.FlowcellRun)
        mock_object._id = mock_id
        annotator.flowcellrun = mock_object

        # WHEN list of projects is retrieved
        test_projects = annotator.get_projects()

        # THEN the list of projects should include all project folders
        # in the unaligned folder (and nothing else)
        assert (test_projects == mock_projects)

    def test_get_libraries(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mock_id = '161231_INSTID_0001_AC00000XX'

        # AND the unaligned folder includes multiple project folders,
        # each with multiple folders for sequenced libraries
        mock_projects = ['P1-1-11111111', 'P99-99-99999999']
        mock_libs = {0: ['lib1111-11111111', 'lib2222-22222222'],
                    1: ['lib3333-33333333', 'lib4444-44444444']}
        mock_path = (tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mock_id)
                     .mkdir('Unaligned'))
        for idx, p in enumerate(mock_projects):
            projpath = mock_path.mkdir(p)
            for l in mock_libs[idx]:
                projpath.mkdir(l)

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mock_object = mock.create_autospec(docs.FlowcellRun)
        mock_object._id = mock_id
        annotator.flowcellrun = mock_object

        # WHEN the full list of unaligned libraries is retrieved
        test_libs = annotator.get_libraries()

        # THEN the list should include all library folders across all projects
        # in the unaligned folder (and nothing else)
        assert (set(test_libs) ==
                set([l for libs in mock_libs.values() for l in libs]))

    def test_get_sequenced_libraries(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mock_id = '161231_INSTID_0001_AC00000XX'

        # AND the unaligned folder includes multiple project folders,
        # each with multiple folders for sequenced libraries that contain
        # one or more FASTQ files for the library
        mock_projects = ['P1-1-11111111', 'P99-99-99999999']
        mock_libs = {0: ['lib1111-11111111', 'lib2222-22222222'],
                    1: ['lib3333-33333333', 'lib4444-44444444']}
        mock_path = (tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mock_id)
                    .mkdir('Unaligned'))
        for idx, p in enumerate(mock_projects):
            projpath = mock_path.mkdir(p)
            for l in mock_libs[idx]:
                libpath = projpath.mkdir(l)
                libpath.ensure('sample-name_S001_L001_R1_001.fastq.gz')
                libpath.ensure('sample-name_S001_L002_R1_001.fastq.gz')

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mock_id,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mock_object = mock.create_autospec(docs.FlowcellRun)
        mock_object._id = mock_id
        annotator.flowcellrun = mock_object

        # WHEN the full list of sequenced library model objects is retrieved
        test_objects = annotator.get_sequenced_libraries()

        # THEN the list should include a sequenced library model object
        # corresponding to each library in the unaligned folder;
        # note: library IDs correspond to library folder names without any
        # of the numbers following the dash, and library IDs for each
        # sequenced library is be stored in the 'parent_id' attribute
        assert (all[type(sl) == docs.SequencedLibrary] for sl in test_objects)
        assert (set([sl.parent_id for sl in test_objects]) ==
                set([l.split('-')[0] for libs in mock_libs.values()
                     for l in libs]))


@pytest.fixture(scope='function')
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
    
@pytest.fixture(scope='function')
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
    

class TestWorkflowBatchAnnotator:
    """
    Tests methods for the `WorkflowBatchAnnotator` class in the
    `bripipetools.annotation.globusgalaxy` module.
    """
    def test_init_workflowbatch_for_existing_workflowbatch(self, mock_db,
                                                           tmpdir):
        # GIVEN a workflow batch ID and path to the workflow batch file
        mock_id = 'globusgalaxy_2016-12-31_1'
        mock_filename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mock_file = mock_batchfile(mock_filename, tmpdir)

        # AND a connection to a database in which a document corresponding
        # to the workflow batch exists already
        mock_db.workflowbatches.insert_one(
            {'_id': mock_id,
             'workflowbatchFile': mock_file,
             'date': datetime.datetime(2016, 12, 31, 0, 0),
             'type': 'Galaxy workflow batch'})

        # AND a set of run options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND an annotator object is created for the workflow batch with
        # an arbitrary 'genomics' root specified
        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mock_file,
            db=mock_db,
            genomics_root='/mnt',
            run_opts = mock_run_opts
        )

        # WHEN the model object is initiated for the annotator
        test_object = annotator._init_workflowbatch()

        # THEN the workflow batch object should be returned and
        # should be correctly mapped from the database object
        assert (type(test_object) == docs.GalaxyWorkflowBatch)
        assert (test_object._id == mock_id)
        assert test_object.is_mapped

    def test_init_workflowbatch_for_new_workflowbatch(self, mock_db,
                                                           tmpdir):
        # GIVEN a path to a workflow batch file
        mock_id = 'globusgalaxy_2016-12-31_1'
        mock_filename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mock_file = mock_batchfile(mock_filename, tmpdir)

        # AND a set of run options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a connection to a database in which a document corresponding
        # to the workflow batch does not exist

        # AND an annotator object is created for the workflow batch with
        # an arbitrary 'genomics' root specified
        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mock_file,
            db=mock_db,
            genomics_root='/mnt',
            run_opts = mock_run_opts
        )

        # WHEN the model object is initiated for the annotator
        test_object = annotator._init_workflowbatch()

        # THEN the workflow batch object should be returned and
        # should be correctly mapped from the database object
        assert (type(test_object) == docs.GalaxyWorkflowBatch)
        assert (test_object._id == mock_id)
        assert not test_object.is_mapped

    def test_update_workflowbatch(self, mock_db, tmpdir):
        # GIVEN an annotator object created for a workflow batch with
        # associated workflow batch file
        mock_batch_filename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mock_batch = mock_batchfile(mock_batch_filename, tmpdir)
        
        # AND a workflow file corresponding to the workflow batch
        mock_wkflow_filename = 'optimized_workflow_1.ga'
        mock_workflow = mock_workflowfile(mock_wkflow_filename, tmpdir)

        # AND a set of run options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', 
                         "sexcutoff":1,
                         "workflow_dir":str(tmpdir)}

        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mock_batch,
            db=mock_db,
            genomics_root='/mnt',
            run_opts = mock_run_opts
        )

        # WHEN the mapped model object is updated to add any missing fields
        annotator._update_workflowbatch()

        # THEN the model object should now have expected fields including
        # for projects, and should no longer be flagged as mapped
        assert (annotator.workflowbatch.projects == ['P00-00'])
        assert not annotator.workflowbatch.is_mapped

    def test_get_workflow_batch(self, mock_db, tmpdir):
        # GIVEN an annotator object created for a workflow batch with
        # associated workflow batch file
        mock_filename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mock_file = mock_batchfile(mock_filename, tmpdir)

        # AND a workflow file corresponding to the workflow batch
        mock_wkflow_filename = 'optimized_workflow_1.ga'
        mock_workflow = mock_workflowfile(mock_wkflow_filename, tmpdir)

        # AND a set of run options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', 
                         "sexcutoff":1,
                         "workflow_dir":str(tmpdir)}

        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mock_file,
            db=mock_db,
            genomics_root='/mnt',
            run_opts = mock_run_opts
        )

        # WHEN the mapped model object is retrieved
        test_object = annotator.get_workflow_batch()

        # THEN the model object should now have expected fields including
        # for projects, and should no longer be flagged as mapped
        assert (test_object.projects == ['P00-00'])
        assert not test_object.is_mapped

    def test_get_sequenced_libraries(self, mock_db, tmpdir):
        # GIVEN an annotator object created for a workflow batch with
        # associated workflow batch file
        mock_filename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mock_file = mock_batchfile(mock_filename, tmpdir)

        # AND a set of run options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mock_file,
            db=mock_db,
            genomics_root='/mnt',
            run_opts = mock_run_opts
        )

        # WHEN the list of sequenced libraries processed in the workflow
        # batch is retrieved
        testseqlibs = annotator.get_sequenced_libraries()

        # THEN the model object should now have expected fields including
        # for projects, and should no longer be flagged as mapped
        assert (testseqlibs == ['sample1', 'sample2'])

    # TODO: test_check_sex
    # TODO: test_get_processed_libraries


@pytest.fixture(scope='function')
def mock_batchdata():
    mock_id = 'lib1111_C00000XX'
    yield (
        mock_id,
        [
            {'name': 'SampleName',
             'tag': 'SampleName',
             'type': 'sample',
             'value': mock_id},
            {'name': 'to_path',
             'tag': 'out-source1_out-type1_out-ext_out',
             'type': 'output',
             'value': 'outfilepath1'},
            {'name': 'to_path',
             'tag': 'out-source2_out-type1_out-ext_out',
             'type': 'output',
             'value': 'outfilepath2'},
            {'name': 'to_path',
             'tag': 'out-source3_out-type2_out-ext_out',
             'type': 'output',
             'value': 'outfilepath3'}
        ]
    )


class TestProcessedLibraryAnnotator:
    """
    Tests methods for the `ProcessedLibraryAnnotator` class in the
    `bripipetools.annotation.globusgalaxy` module.
    """
    def test_init_processedlibrary_for_existing_sample(self, mock_db,
                                                       mock_batchdata):
        # GIVEN a processed library ID and a connection to a database in which
        # a document corresponding to the processed library exists already
        mock_id, mock_params = mock_batchdata

        mock_db.samples.insert_one(
            {'_id': '{}_processed'.format(mock_id),
             'type': 'processed library'}
        )

        # AND an annotator object is created for the processed library with
        # workflow batch ID and workflow parameters for that sample
        mock_batchid = 'globusgalaxy_2016-12-31_1'
        annotator = annotation.ProcessedLibraryAnnotator(
            workflowbatch_id=mock_batchid,
            params=mock_params,
            db=mock_db
        )

        # WHEN the model object is initiated for the annotator
        test_object = annotator._init_processedlibrary()

        # THEN the processed library object should be returned and
        # should be correctly mapped from the database object
        assert (type(test_object) == docs.ProcessedLibrary)
        assert (test_object._id == '{}_processed'.format(mock_id))
        assert test_object.is_mapped

    def test_init_processedlibrary_for_new_sample(self, mock_db,
                                                  mock_batchdata):
        # GIVEN a processed library ID and a connection to a database in which
        # a document corresponding to the processed library does not exist
        mock_id, mock_params = mock_batchdata

        # AND an annotator object is created for the processed library with
        # workflow batch ID and workflow parameters for that sample
        mock_batchid = 'globusgalaxy_2016-12-31_1'
        annotator = annotation.ProcessedLibraryAnnotator(
            workflowbatch_id=mock_batchid,
            params=mock_params,
            db=mock_db
        )

        # WHEN the model object is initiated for the annotator
        test_object = annotator._init_processedlibrary()

        # THEN the processed library object should be returned and
        # should be correctly mapped from the database object
        assert (type(test_object) == docs.ProcessedLibrary)
        assert (test_object._id == '{}_processed'.format(mock_id))
        assert not test_object.is_mapped

    def test_get_outputs(self, mock_db, mock_batchdata):
        # GIVEN a processed library ID and a connection to a database in which
        # a document corresponding to the processed library does not exist
        mock_id, mock_params = mock_batchdata

        # AND an annotator object is created for the processed library with
        # workflow batch ID and workflow parameters for that sample
        mock_batchid = 'globusgalaxy_2016-12-31_1'
        annotator = annotation.ProcessedLibraryAnnotator(
            workflowbatch_id=mock_batchid,
            params=mock_params,
            db=mock_db
        )

        # WHEN outputs are retrieved for the processed library
        testoutputs = annotator._get_outputs()

        # THEN outputs should be stored in a dict with parameter tag and value
        # as key-value pairs
        assert (testoutputs
                == {'out-source1_out-type1_out-ext_out': 'outfilepath1',
                    'out-source2_out-type1_out-ext_out': 'outfilepath2',
                    'out-source3_out-type2_out-ext_out': 'outfilepath3'})

    def test_group_outputs(self, mock_db, mock_batchdata):
        # GIVEN a processed library ID and a connection to a database in which
        # a document corresponding to the processed library does not exist
        mock_id, mock_params = mock_batchdata

        # AND an annotator object is created for the processed library with
        # workflow batch ID and workflow parameters for that sample
        mock_batchid = 'globusgalaxy_2016-12-31_1'
        annotator = annotation.ProcessedLibraryAnnotator(
            workflowbatch_id=mock_batchid,
            params=mock_params,
            db=mock_db
        )

        # WHEN outputs are grouped by type and source
        testoutputs = annotator._group_outputs()

        # THEN outputs annotated in separate dicts according to source, name,
        # and file path, grouped into lists for each output type
        assert (testoutputs
                == {
                    'out-type1': [
                        {'source': 'out-source1',
                         'name': 'out-source1_out-type1_out-ext',
                         'file': '/outfilepath1'},
                        {'source': 'out-source2',
                         'name': 'out-source2_out-type1_out-ext',
                         'file': '/outfilepath2'},
                    ],
                    'out-type2': [
                        {'source': 'out-source3',
                         'name': 'out-source3_out-type2_out-ext',
                         'file': '/outfilepath3'},
                    ]
                })

    def test_append_processed_data_first_time(self, mock_db, mock_batchdata):
        # GIVEN a processed library ID and a connection to a database in which
        # a document corresponding to the processed library does not exist
        mock_id, mock_params = mock_batchdata

        # AND an annotator object is created for the processed library with
        # workflow batch ID and workflow parameters for that sample
        mock_batchid = 'globusgalaxy_2016-12-31_1'
        annotator = annotation.ProcessedLibraryAnnotator(
            workflowbatch_id=mock_batchid,
            params=mock_params,
            db=mock_db
        )

        # WHEN outputs are grouped by type and source
        annotator._append_processed_data()

        # THEN outputs annotated in separate dicts according to source, name,
        # and file path, grouped into lists for each output type
        assert (annotator.processedlibrary.processed_data[0]['workflowbatch_id']
                == mock_batchid)

    def test_append_processed_data_previously_processed(self, mock_db,
                                                        mock_batchdata):
        # GIVEN a processed library ID and a connection to a database in which
        # a document corresponding to the processed library does not exist
        mock_id, mock_params = mock_batchdata

        # AND an annotator object is created for the processed library with
        # workflow batch ID and workflow parameters for that sample
        mock_batchid = 'globusgalaxy_2016-12-31_1'
        annotator = annotation.ProcessedLibraryAnnotator(
            workflowbatch_id=mock_batchid,
            params=mock_params,
            db=mock_db
        )

        # AND processed data for the workflow batch are already present
        annotator.processedlibrary.processed_data.append(
            {'workflowbatch_id': mock_batchid,
             'outputs': []}
        )

        # WHEN outputs are grouped by type and source
        annotator._append_processed_data()

        # THEN outputs annotated in separate dicts according to source, name,
        # and file path, grouped into lists for each output type
        assert (annotator.processedlibrary.processed_data[0]['workflowbatch_id']
                == mock_batchid)

    def test_update_processedlibrary(self, mock_db, mock_batchdata):
        # GIVEN a processed library ID and a connection to a database in which
        # a document corresponding to the processed library does not exist
        mock_id, mock_params = mock_batchdata

        # AND an annotator object is created for the processed library with
        # workflow batch ID and workflow parameters for that sample
        mock_batchid = 'globusgalaxy_2016-12-31_1'
        annotator = annotation.ProcessedLibraryAnnotator(
            workflowbatch_id=mock_batchid,
            params=mock_params,
            db=mock_db
        )

        # WHEN the mapped model object is updated to add any missing fields
        annotator._update_processedlibrary()

        # THEN the model object should now have expected fields including
        # for processed data and parent ID, and should no longer be flagged
        # as mapped
        assert (annotator.processedlibrary.parent_id == mock_id)
        assert not annotator.processedlibrary.is_mapped

    def test_get_processed_library(self, mock_db, mock_batchdata):
        # GIVEN a processed library ID and a connection to a database in which
        # a document corresponding to the processed library does not exist
        mock_id, mock_params = mock_batchdata

        # AND an annotator object is created for the processed library with
        # workflow batch ID and workflow parameters for that sample
        mock_batchid = 'globusgalaxy_2016-12-31_1'
        annotator = annotation.ProcessedLibraryAnnotator(
            workflowbatch_id=mock_batchid,
            params=mock_params,
            db=mock_db
        )

        # WHEN the mapped model object is retrieved
        test_object = annotator.get_processed_library()

        # THEN the model object should have expected fields including
        # for processed data and parent ID, and should no longer be flagged
        # as mapped
        assert (test_object.parent_id == mock_id)
        assert not test_object.is_mapped
