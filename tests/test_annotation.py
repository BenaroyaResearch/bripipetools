import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import pytest
import os
import re

from bripipetools.annotation import illuminaseq

@pytest.fixture(scope="class")
def mock_genomics_server(request):
    logger.info(("[setup] mock 'genomics' server, connect "
                 "to mock 'genomics' server"))
    run_id = '150615_D00565_0087_AC6VG0ANXX'
    mock_genomics_root = './tests/test-data/'
    mock_genomics_path = os.path.join(mock_genomics_root, 'genomics')
    mock_flowcell_path = os.path.join(mock_genomics_path, 'Illumina', run_id)
    mock_unaligned_path = os.path.join(mock_flowcell_path, 'Unaligned')
    mock_project_p14_12 = 'P14-12-23221204'
    mock_project_p109_1 = 'P109-1-21113094'
    mock_lib7293 = 'lib7293-25920016'
    data = {'run_id': run_id,
            'genomics_root': mock_genomics_root,
            'genomics_path': mock_genomics_path,
            'flowcell_path': mock_flowcell_path,
            'unaligned_path': mock_unaligned_path,
            'project_p14_12': mock_project_p14_12,
            'project_p109_1': mock_project_p109_1,
            'lib7293': mock_lib7293}
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

    def test_get_flowcell_path(self, annotator, prod_genomics_server):
        class_name = self.__class__.__name__
        logger.info("{} - test `get_flowcell_path()`".format(class_name))

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

@pytest.mark.usefixtures('mock_genomics_server')
class TestSequencedLibraryAnnotatorWithMockGenomicsServer:
    @pytest.fixture(scope="class")
    def annotator(self, request, mock_genomics_server):
        logger.info("[setup] SequencedLibraryAnnotator mock instance")

        # GIVEN a SequencedLibraryAnnotator with mock 'genomics' server path,
        # and path to library folder (i.e., where data/organization is known)
        seqlibannotator = illuminaseq.SequencedLibraryAnnotator(
            os.path.join(mock_genomics_server['unaligned_path'],
                         mock_genomics_server['project_p14_12'],
                         mock_genomics_server['lib7293'])
        )
        def fin():
            logger.info("[teardown] SequencedLibraryAnnotator mock instance")
        request.addfinalizer(fin)
        return seqlibannotator

# def test_sequencedlibraryannotator_creation():
#     seqlibannotator = illuminaseq.SequencedLibraryAnnotator(
#         ('./tests/test-data/genomics/Illumina/150615_D00565_0087_AC6VG0ANXX/'
#          'P14-12-23221204/lib7293-25920016')
#     )
#     assert(seqlibannotator.path)
