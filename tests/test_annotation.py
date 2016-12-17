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
def mock_db(request):
    # GIVEN a mocked version of the TG3 Mongo database
    logger.info(("[setup] mock database, connect "
                 "to mock Mongo database"))

    yield mongomock.MongoClient().db
    logger.debug(("[teardown] mock database, disconnect "
                  "from mock Mongo database"))


class TestSequencedLibraryAnnotator:
    """
    Tests methods for the `SequencedLibraryAnnotator` class in the
    `bripipetools.annotation.illuminaseq` module.
    """
    def test_init_sequencedlibrary_for_existing_sample(self, mock_db):
        # GIVEN a sequenced library ID and a connection to a database in which
        # a document corresponding to the sequenced library exists already
        mockid = 'lib1111_C00000XX'

        mock_db.samples.insert_one(
            {'_id': mockid,
             'type': 'sequenced library'}
        )

        # AND an annotator object is created for the sequenced library with
        # project and library folder names, run ID, and an arbitrary path to
        # the libraries raw data
        mocklib = 'lib1111-1111'
        mockproject = 'P1-1-1111'
        mockrunid = '161231_INSTID_0001_AC00000XX'
        annotator = annotation.SequencedLibraryAnnotator(
            path='mock-path-to-raw-data.fastq.gz',
            library=mocklib,
            project=mockproject,
            run_id=mockrunid,
            db=mock_db
        )

        # WHEN the model object is initiated for the annotator
        modelobject = annotator._init_sequencedlibrary()

        # THEN the sequenced library object should be returned and
        # should be correctly mapped from the database object
        assert (type(modelobject) == docs.SequencedLibrary)
        assert (modelobject._id == mockid)
        assert modelobject.is_mapped

    def test_init_sequencedlibrary_for_existing_sample(self, mock_db):
        # GIVEN a sequenced library ID and a connection to a database in which
        # a document corresponding to the sequenced library does not exist
        mockid = 'lib1111_C00000XX'

        # AND an annotator object is created for the sequenced library with
        # project and library folder names, run ID, and an arbitrary path to
        # the libraries raw data
        mocklib = 'lib1111-1111'
        mockproject = 'P1-1-1111'
        mockrunid = '161231_INSTID_0001_AC00000XX'
        annotator = annotation.SequencedLibraryAnnotator(
            path='mock-path-to-raw-data.fastq.gz',
            library=mocklib,
            project=mockproject,
            run_id=mockrunid,
            db=mock_db
        )

        # WHEN the model object is initiated for the annotator
        modelobject = annotator._init_sequencedlibrary()

        # THEN the sequenced library object should be returned and
        # should be correctly mapped from the database object
        assert (type(modelobject) == docs.SequencedLibrary)
        assert (modelobject._id == mockid)
        assert not modelobject.is_mapped

    def test_get_raw_data(self, mock_db, tmpdir):
        # GIVEN an annotator object created for the sequenced library with
        # project and library folder names, run ID, and the full path to the
        # folder containing raw data (i.e., one or more FASTQ files)
        mocklib = 'lib1111'
        mockproject = 'P1-1'
        mockrunid = '161231_INSTID_0001_AC00000XX'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mockrunid)
                    .mkdir('Unaligned')
                    .mkdir(mockproject)
                    .mkdir(mocklib))
        mockdata = 'sample-name_S001_L001_R1_001.fastq.gz'
        mockpath.ensure(mockdata)
        annotator = annotation.SequencedLibraryAnnotator(
            path=str(mockpath),
            library=mocklib,
            project=mockproject,
            run_id=mockrunid,
            db=mock_db
        )

        # WHEN raw data details are recovered for the library
        testdata = annotator._get_raw_data()

        # THEN the path field of the raw data file should match
        # the expected result
        assert (testdata[0]['path'] == mockdata)

    def test_update_sequencedlibrary(self, mock_db, tmpdir):
        # GIVEN an annotator object created for a sequenced library with
        # project and library folder names, run ID, and the full path to the
        # folder containing raw data (i.e., one or more FASTQ files)
        mocklib = 'lib1111'
        mockproject = 'P1-1'
        mockrunid = '161231_INSTID_0001_AC00000XX'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mockrunid)
                    .mkdir('Unaligned')
                    .mkdir(mockproject)
                    .mkdir(mocklib))
        mockdata = 'sample-name_S001_L001_R1_001.fastq.gz'
        mockpath.ensure(mockdata)
        annotator = annotation.SequencedLibraryAnnotator(
            path=str(mockpath),
            library=mocklib,
            project=mockproject,
            run_id=mockrunid,
            db=mock_db
        )

        # AND the annotator object has a mapped model object with the
        # corresponding sequenced library ID
        mockid = 'lib1111_C00000XX'
        mockobject = mock.create_autospec(docs.SequencedLibrary)
        mockobject._id = mockid
        mockobject.is_mapped = True
        annotator.sequencedlibrary = mockobject

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
        mocklib = 'lib1111'
        mockproject = 'P1-1'
        mockrunid = '161231_INSTID_0001_AC00000XX'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mockrunid)
                    .mkdir('Unaligned')
                    .mkdir(mockproject)
                    .mkdir(mocklib))
        mockdata = 'sample-name_S001_L001_R1_001.fastq.gz'
        mockpath.ensure(mockdata)
        annotator = annotation.SequencedLibraryAnnotator(
            path=str(mockpath),
            library=mocklib,
            project=mockproject,
            run_id=mockrunid,
            db=mock_db
        )

        # AND the annotator object has a mapped model object with the
        # corresponding sequenced library ID
        mockid = 'lib1111_C00000XX'
        mockobject = mock.create_autospec(docs.SequencedLibrary)
        mockobject._id = mockid
        mockobject.is_mapped = True
        annotator.sequencedlibrary = mockobject

        # WHEN the mapped model object is retrieved
        testobject = annotator.get_sequenced_library()

        # THEN the model object should now have expected fields including
        # for raw data, and should no longer be flagged as mapped
        assert (hasattr(testobject, 'raw_data'))
        assert not testobject.is_mapped


class TestFlowcellRunAnnotator:
    """
    Tests methods for the `FlowcellRunAnnotator` class in the
    `bripipetools.annotation.flowcellruns` module.
    """
    def test_init_flowcellrun_for_existing_run(self, mock_db):
        # GIVEN a flowcell run ID and a connection to a database in which
        # a document corresponding to the flowcell run exists already
        mockid = '161231_INSTID_0001_AC00000XX'
        mock_db.runs.insert_one(
            {'_id': mockid,
             'type': 'flowcell'}
        )

        # AND an annotator object is created for the flowcell run with
        # an arbitrary 'genomics' root specified
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root='/mnt'
        )

        # WHEN the model object is initiated for the annotator
        modelobject = annotator._init_flowcellrun()

        # THEN the flowcell run object should be returned and
        # should be correctly mapped from the database object
        assert (type(modelobject) == docs.FlowcellRun)
        assert (modelobject._id == mockid)
        assert modelobject.is_mapped

    def test_init_flowcellrun_for_new_run(self, mock_db):
        # GIVEN a flowcell run ID and a connection to a database in which
        # a document corresponding to the flowcell run does not exist
        mockid = '161231_INSTID_0001_AC00000XX'

        # AND an annotator object is created for the flowcell run with
        # an arbitrary 'genomics' root specified
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root='/mnt'
        )

        # WHEN the model object is initiated for the annotator
        modelobject = annotator._init_flowcellrun()

        # THEN the new flowcell run object should be returned
        assert (type(modelobject) == docs.FlowcellRun)
        assert (modelobject._id == mockid)
        assert not modelobject.is_mapped

    def test_get_flowcell_path_for_existing_folder(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at the path 'genomics/Illumina/<run_id>'
        mockid = '161231_INSTID_0001_AC00000XX'
        mockpath = tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mockid)

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mockobject = mock.create_autospec(docs.FlowcellRun)
        mockobject._id = mockid
        annotator.flowcellrun = mockobject

        # WHEN the flowcell folder path is retrieved
        testpath = annotator._get_flowcell_path()

        # THEN correct flowcell folder should be found in 'genomics/Illumina/'
        assert (testpath == str(mockpath))

    def test_get_flowcell_path_for_invalid_root(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary directory that does not
        # contain 'genomics/Illumina/'
        mockid = '161231_INSTID_0001_AC00000XX'

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mockobject = mock.create_autospec(docs.FlowcellRun)
        mockobject._id = mockid
        annotator.flowcellrun = mockobject

        # WHEN the flowcell folder path is retrieved

        # THEN should raise expected exception
        with pytest.raises(OSError):
            annotator._get_flowcell_path()

    def test_get_unaligned_path_for_existing_folder(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mockid = '161231_INSTID_0001_AC00000XX'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mockid)
                    .mkdir('Unaligned'))

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mockobject = mock.create_autospec(docs.FlowcellRun)
        mockobject._id = mockid
        annotator.flowcellrun = mockobject

        # WHEN the flowcell folder path is retrieved
        testpath = annotator._get_unaligned_path()

        # THEN correct flowcell folder should be found in 'genomics/Illumina/'
        assert (testpath == str(mockpath))

    def test_get_unaligned_path_for_missing_folder(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and there is no subfolder named 'Unaligned'
        mockid = '161231_INSTID_0001_AC00000XX'
        mockpath = tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mockid)

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mockobject = mock.create_autospec(docs.FlowcellRun)
        mockobject._id = mockid
        annotator.flowcellrun = mockobject

        # WHEN the unaligned folder path is retrieved

        # THEN should raise expected exception
        with pytest.raises(OSError):
            annotator._get_unaligned_path()

    def test_get_flowcell_run(self, mock_db):
        # GIVEN any state and a flowcell run annotator object
        mockid = '161231_INSTID_0001_AC00000XX'
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root='/mnt'
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mockobject = mock.create_autospec(docs.FlowcellRun)
        mockobject._id = mockid
        annotator.flowcellrun = mockobject

        # WHEN model object is retrieved
        testobject = annotator.get_flowcell_run()

        # THEN should be expected object
        assert (testobject == mockobject)

    def test_get_projects(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mockid = '161231_INSTID_0001_AC00000XX'

        # AND the unaligned folder includes multiple project folders
        mockprojects = ['P1-1-11111111', 'P99-99-99999999']
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mockid)
                    .mkdir('Unaligned'))
        for p in mockprojects:
            mockpath.mkdir(p)

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mockobject = mock.create_autospec(docs.FlowcellRun)
        mockobject._id = mockid
        annotator.flowcellrun = mockobject

        # WHEN list of projects is retrieved
        testprojects = annotator.get_projects()

        # THEN the list of projects should include all project folders
        # in the unaligned folder (and nothing else)
        assert (testprojects == mockprojects)

    def test_get_libraries(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mockid = '161231_INSTID_0001_AC00000XX'

        # AND the unaligned folder includes multiple project folders,
        # each with multiple folders for sequenced libraries
        mockprojects = ['P1-1-11111111', 'P99-99-99999999']
        mocklibs = {0: ['lib1111-11111111', 'lib2222-22222222'],
                    1: ['lib3333-33333333', 'lib4444-44444444']}
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mockid)
                    .mkdir('Unaligned'))
        for idx, p in enumerate(mockprojects):
            projpath = mockpath.mkdir(p)
            for l in mocklibs[idx]:
                projpath.mkdir(l)

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mockobject = mock.create_autospec(docs.FlowcellRun)
        mockobject._id = mockid
        annotator.flowcellrun = mockobject

        # WHEN the full list of unaligned libraries is retrieved
        testlibs = annotator.get_libraries()

        # THEN the list should include all library folders across all projects
        # in the unaligned folder (and nothing else)
        assert (set(testlibs) ==
                set([l for libs in mocklibs.values() for l in libs]))

    def test_get_sequenced_libraries(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mockid = '161231_INSTID_0001_AC00000XX'

        # AND the unaligned folder includes multiple project folders,
        # each with multiple folders for sequenced libraries that contain
        # one or more FASTQ files for the library
        mockprojects = ['P1-1-11111111', 'P99-99-99999999']
        mocklibs = {0: ['lib1111-11111111', 'lib2222-22222222'],
                    1: ['lib3333-33333333', 'lib4444-44444444']}
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mockid)
                    .mkdir('Unaligned'))
        for idx, p in enumerate(mockprojects):
            projpath = mockpath.mkdir(p)
            for l in mocklibs[idx]:
                libpath = projpath.mkdir(l)
                libpath.ensure('sample-name_S001_L001_R1_001.fastq.gz')
                libpath.ensure('sample-name_S001_L002_R1_001.fastq.gz')

        # AND an annotator object created for a flowcell run ID with that
        # directory specified as 'genomics' root
        annotator = annotation.FlowcellRunAnnotator(
            run_id=mockid,
            db=mock_db,
            genomics_root=str(tmpdir)
        )

        # AND the annotator object has a mapped model object with the
        # corresponding run ID
        mockobject = mock.create_autospec(docs.FlowcellRun)
        mockobject._id = mockid
        annotator.flowcellrun = mockobject

        # WHEN the full list of sequenced library model objects is retrieved
        testobjects = annotator.get_sequenced_libraries()

        # THEN the list should include a sequenced library model object
        # corresponding to each library in the unaligned folder;
        # note: library IDs correspond to library folder names without any
        # of the numbers following the dash, and library IDs for each
        # sequenced library is be stored in the 'parent_id' attribute
        assert (all[type(sl) == docs.SequencedLibrary] for sl in testobjects)
        assert (set([sl.parent_id for sl in testobjects]) ==
                set([l.split('-')[0] for libs in mocklibs.values()
                     for l in libs]))


@pytest.fixture(scope='function')
def mockbatchfile(filename, tmpdir):
    mockcontents = ['###METADATA\n',
                    '#############\n',
                    'Workflow Name\toptimized_workflow_1\n',
                    'Project Name\t161231_P00-00_C00000XX\n',
                    '###TABLE DATA\n',
                    '#############\n',
                    'SampleName\tin_tag##_::_::_::param_name\n',
                    'sample1\tin_value1\n',
                    'sample2\tin_value2\n']
    mockfile = tmpdir.join(filename)
    mockfile.write(''.join(mockcontents))
    return str(mockfile)


class TestWorkflowBatchAnnotator:
    """
    Tests methods for the `WorkflowBatchAnnotator` class in the
    `bripipetools.annotation.globusgalaxy` module.
    """
    def test_init_workflowbatch_for_existing_workflowbatch(self, mock_db,
                                                           tmpdir):
        # GIVEN a workflow batch ID and path to the workflow batch file
        mockid = 'globusgalaxy_2016-12-31_1'
        mockfilename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mockfile = mockbatchfile(mockfilename, tmpdir)

        # AND a connection to a database in which a document corresponding
        # to the workflow batch exists already
        mock_db.workflowbatches.insert_one(
            {'_id': mockid,
             'workflowbatchFile': mockfile,
             'date': datetime.datetime(2016, 12, 31, 0, 0),
             'type': 'Galaxy workflow batch'})

        # AND an annotator object is created for the workflow batch with
        # an arbitrary 'genomics' root specified
        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mockfile,
            db=mock_db,
            genomics_root='/mnt'
        )

        # WHEN the model object is initiated for the annotator
        modelobject = annotator._init_workflowbatch()

        # THEN the workflow batch object should be returned and
        # should be correctly mapped from the database object
        assert (type(modelobject) == docs.GalaxyWorkflowBatch)
        assert (modelobject._id == mockid)
        assert modelobject.is_mapped

    def test_init_workflowbatch_for_new_workflowbatch(self, mock_db,
                                                           tmpdir):
        # GIVEN a path to a workflow batch file
        mockid = 'globusgalaxy_2016-12-31_1'
        mockfilename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mockfile = mockbatchfile(mockfilename, tmpdir)

        # AND a connection to a database in which a document corresponding
        # to the workflow batch does not exist

        # AND an annotator object is created for the workflow batch with
        # an arbitrary 'genomics' root specified
        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mockfile,
            db=mock_db,
            genomics_root='/mnt'
        )

        # WHEN the model object is initiated for the annotator
        modelobject = annotator._init_workflowbatch()

        # THEN the workflow batch object should be returned and
        # should be correctly mapped from the database object
        assert (type(modelobject) == docs.GalaxyWorkflowBatch)
        assert (modelobject._id == mockid)
        assert not modelobject.is_mapped

    def test_update_workflowbatch(self, mock_db, tmpdir):
        # GIVEN an annotator object created for a workflow batch with
        # associated workflow batch file
        mockfilename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mockfile = mockbatchfile(mockfilename, tmpdir)
        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mockfile,
            db=mock_db,
            genomics_root='/mnt'
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
        mockfilename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mockfile = mockbatchfile(mockfilename, tmpdir)
        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mockfile,
            db=mock_db,
            genomics_root='/mnt'
        )

        # WHEN the mapped model object is retrieved
        testobject = annotator.get_workflow_batch()

        # THEN the model object should now have expected fields including
        # for projects, and should no longer be flagged as mapped
        assert (testobject.projects == ['P00-00'])
        assert not testobject.is_mapped

    def test_get_sequenced_libraries(self, mock_db, tmpdir):
        # GIVEN an annotator object created for a workflow batch with
        # associated workflow batch file
        mockfilename = '161231_P00-00_C00000XX_optimized_workflow_1.txt'
        mockfile = mockbatchfile(mockfilename, tmpdir)
        annotator = annotation.WorkflowBatchAnnotator(
            workflowbatch_file=mockfile,
            db=mock_db,
            genomics_root='/mnt'
        )

        # WHEN the list of sequenced libraries processed in the workflow
        # batch is retrieved
        testseqlibs = annotator.get_sequenced_libraries()

        # THEN the model object should now have expected fields including
        # for projects, and should no longer be flagged as mapped
        assert (testseqlibs == ['sample1', 'sample2'])

    # TODO: test_check_sex
    # TODO: test_get_processed_libraries


# @pytest.mark.usefixtures('mock_genomics_server', 'mock_db')
# class TestProcessedLibraryAnnotator:
#     """
#     Tests methods for the `ProcessedLibraryAnnotator` class in the
#     `bripipetools.annotation.globusgalaxy` module.
#     """
#     @pytest.fixture(
#         scope='class',
#         params=[{'runnum': r, 'batchnum': b, 'samplenum': s}
#                 for r in range(1)
#                 for b in range(2)
#                 for s in range(6)
#                 if not (b == 1 and s > 2)])
#     @pytest.fixture(scope='class')
#     def annotatordata(self, request, mock_genomics_server, mock_db):
#         # GIVEN a ProcessedLibraryAnnotator with mock 'genomics' server path,
#         # and path to library folder (i.e., where data/organization is known),
#         # with specified library, project, and run ID,
#         # as well as a mock db connection
#         runs = mock_genomics_server['root']['genomics']['illumina']['runs']
#         rundata = runs[request.param['runnum']]
#         batches = rundata['submitted']['batches']
#         batchdata = batches[request.param['batchnum']]
#         samples = batchdata['samples']
#         samplename = samples[request.param['samplenum']]
#         proclib_id = ('{}_{}_processed'
#                       .format(samplename, rundata['flowcell_id']))
#
#         logger.info("[setup] ProcessedLibraryAnnotator mock instance "
#                     "for sample {}".format(samplename))
#
#         workflowbatch_id = batchdata['id']
#         # TODO: try to remove the test dependency on the io module here
#         workflowbatch_data = io.WorkflowBatchFile(
#             path=batchdata['path'],
#             state='submit').parse()
#
#         proclibannotator = annotation.ProcessedLibraryAnnotator(
#             workflowbatch_id=workflowbatch_id,
#             params=workflowbatch_data['samples'][request.param['samplenum']],
#             db=mock_db)
#
#         def fin():
#             logger.info("[teardown] ProcessedLibraryAnnotator mock instance")
#         request.addfinalizer(fin)
#         return (proclibannotator, batchdata, proclib_id)
#
#     def test_init_attribute_munging(self, annotatordata):
#         # (GIVEN)
#         annotator, _, proclib_id = annotatordata
#
#         logger.info("test `__init__()` for proper attribute munging "
#                     " with sample {}".format(proclib_id))
#
#         # WHEN checking whether input arguments were automatically munged
#         # when setting annotator attributes
#
#         # THEN the processed library ID should be properly constructed as the
#         # library ID and flowcell ID, tagged as processed
#         assert(annotator.proclib_id == proclib_id)
#
#     def test_init_processedlibrary_existing_sample(self, annotatordata,
#                                                    mock_db):
#         # (GIVEN)
#         annotator, _, proclib_id = annotatordata
#
#         logger.info("test `_init_processedlibrary()` with existing sample {}"
#                     .format(proclib_id))
#
#         # WHEN processed library already exists in 'samples' collection
#         mock_db.samples.insert_one(
#             {'_id': proclib_id,
#              'type': 'processed library',
#              'isMock': True})
#         processedlibrary = annotator._init_processedlibrary()
#
#         # THEN the processed library object should be returned and
#         # should be correctly mapped from the database object
#         assert(type(processedlibrary) == docs.ProcessedLibrary)
#         assert(processedlibrary._id == proclib_id)
#         assert(hasattr(processedlibrary, 'is_mock'))
#
#         logger.info("[rollback] remove most recently inserted "
#                     "from mock database")
#         mock_db.samples.drop()
#
#     def test_init_processedlibrary_new_sample(self, annotatordata):
#         # (GIVEN)
#         annotator, _, proclib_id = annotatordata
#
#         logger.info("test `_init_processedlibrary()` with new sample")
#
#         # WHEN processed library sample does not already exist in
#         # 'samples' collection
#         processedlibrary = annotator._init_processedlibrary()
#
#         # THEN a new processed library object should be returned
#         assert(type(processedlibrary) == docs.ProcessedLibrary)
#         assert(processedlibrary._id == proclib_id)
#         assert(not hasattr(processedlibrary, 'is_mock'))
#
#     def test_get_outputs(self, annotatordata):
#         # (GIVEN)
#         annotator, batchdata, proclib_id = annotatordata
#
#         logger.info("test `_get_outputs()`")
#
#         # WHEN collecting the list of outputs for a processed library
#
#         # THEN the outputs should be stored in a dict with expected length
#         assert(len(annotator._get_outputs()) == batchdata['num_outputs'])
#
#     def test_parse_output_name_onepart_source(self, annotatordata):
#         # (GIVEN)
#         annotator, _, _ = annotatordata
#
#         logger.info("test `_parse_output_name()`, one-part source")
#
#         # WHEN parsing output name from workflow batch parameter, and the
#         # source name has one parts (i.e., 'tophat')
#         output_items = annotator._parse_output_name(
#             'tophat_alignments_bam_out')
#
#         # THEN output items should be a dictionary including fields for
#         # name, type, and source
#         assert(output_items['name'] == 'tophat_alignments_bam')
#         assert(output_items['type'] == 'alignments')
#         assert(output_items['source'] == 'tophat')
#
#     def test_parse_output_name_twopart_source(self, annotatordata):
#         # (GIVEN)
#         annotator, _, _ = annotatordata
#
#         logger.info("test `_parse_output_name()`, two-part source")
#
#         # WHEN parsing output name from workflow batch parameter, and the
#         # source name has two parts (i.e., 'picard_rnaseq')
#         output_items = annotator._parse_output_name(
#             'picard_rnaseq_metrics_html_out')
#
#         # THEN output items should be a dictionary including fields for
#         # name, type, and source
#         assert(output_items['name'] == 'picard_rnaseq_metrics_html')
#         assert(output_items['type'] == 'metrics')
#         assert(output_items['source'] == 'picard_rnaseq')
#
#     def test_group_outputs(self, annotatordata, mock_genomics_server):
#         # (GIVEN)
#         annotator, _, _ = annotatordata
#
#         logger.info("test `_group_outputs()`")
#
#         # WHEN collecting the organized dictionary of outputs
#         outputs = annotator._group_outputs()
#
#         # THEN the outputs should be correctly grouped according to type
#         # and source (tool)
#         assert(set(outputs.keys())
#                == set(mock_genomics_server['out_types']))
#         assert(set([k['source'] for k in outputs['metrics']])
#                == set(['picard_align', 'tophat_stats', 'picard_markdups',
#                        'picard_rnaseq', 'htseq']))
#
#     def test_append_processed_data(self, annotatordata):
#         # (GIVEN)
#         annotator, _, _ = annotatordata
#
#         logger.info("test `_append_processed_data()`")
#
#         # WHEN batch information and outputs are added to processed data
#         # field for processed library object
#         annotator._append_processed_data()
#
#         # THEN the length of the processed data field should be 1, containing
#         # a dictionary with workflow batch ID and outputs
#         assert(len(annotator.processedlibrary.processed_data) == 1)
#         assert(set(annotator.processedlibrary.processed_data[0].keys())
#                == set(['workflowbatch_id', 'outputs']))
#         annotator.processedlibrary.processed_data = []
#
#     def test_append_processed_data_exists(self, annotatordata):
#         # (GIVEN)
#         annotator, batchdata, _ = annotatordata
#
#         logger.info("test `_append_processed_data()`")
#
#         # AND outputs for the workflow batch are already present
#         annotator.processedlibrary.processed_data.append(
#             {'workflowbatch_id': batchdata['id'],
#              'outputs': []})
#
#         # WHEN batch information and outputs are added to processed data
#         # field for processed library object
#         annotator._append_processed_data()
#
#         # THEN the length of the processed data field should be 1, containing
#         # a dictionary with workflow batch ID and outputs
#         assert(len(annotator.processedlibrary.processed_data) == 1)
#         assert(set(annotator.processedlibrary.processed_data[0].keys())
#                == set(['workflowbatch_id', 'outputs']))
#         annotator.processedlibrary.processed_data = []
#
#     def test_append_processed_data_new(self, annotatordata):
#         # (GIVEN)
#         annotator, batchdata, _ = annotatordata
#
#         logger.info("test `_append_processed_data()`")
#
#         # AND outputs from a different workflow batch are already present
#         annotator.processedlibrary.processed_data.append(
#             {'workflowbatch_id': re.sub('\d$',
#                                         lambda x: str(int(x.group(0)) + 1),
#                                         batchdata['id']),
#              'outputs': []})
#
#         # WHEN batch information and outputs are added to processed data
#         # field for processed library object
#         annotator._append_processed_data()
#
#         # THEN the length of the processed data field should be 2, containing
#         # a dictionary with workflow batch ID and outputs
#         assert(len(annotator.processedlibrary.processed_data) == 2)
#         assert(set(annotator.processedlibrary.processed_data[1].keys())
#                == set(['workflowbatch_id', 'outputs']))
#         annotator.processedlibrary.processed_data = []
#
#     def test_update_processedlibrary(self, annotatordata):
#         # (GIVEN)
#         annotator, _, _ = annotatordata
#
#         logger.info("test `_update_processedlibrary()`")
#
#         # WHEN processed library object is updated
#         annotator._update_processedlibrary()
#
#         # THEN the object should have at least the 'parent_id' and
#         # 'processed_data', and 'processed_data' should be length 1
#         assert(all([hasattr(annotator.processedlibrary, field)
#                     for field in ['parent_id', 'processed_data',
#                                   'date_created', 'last_updated']]))
#         assert(len(annotator.processedlibrary.processed_data) == 1)
#         assert(annotator.processedlibrary.last_updated
#                > annotator.processedlibrary.date_created)
