import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
import re

import pytest
import mock

from bripipetools import qc
from bripipetools import util

@pytest.fixture(scope='class')
def mock_proclib(request, mock_genomics_server):
    logger.info(("[setup] mock processed library object with counts file"))
    processedlibrary = mock.Mock(
        _id='lib7294_C6VG0ANXX_processed',
        processed_data=[
            {'workflowbatch_id': 'globusgalaxy_2016-04-12_1',
             'outputs': {
                'counts': [
                    {'source': 'htseq',
                    'name': 'htseq_counts_txt',
                    'file': util.swap_root(
                        mock_genomics_server['htseq_counts_file'],
                        'genomics', '/')}
                ]
             }
            }
        ],
        type='processed library'
    )
    def fin():
        logger.info(("[teardown] mock processed library object"))
    request.addfinalizer(fin)
    return processedlibrary

@pytest.mark.usefixtures('mock_proclib', 'mock_genomics_server')
class TestSexChecker:
    @pytest.fixture(scope='class')
    def checker(self, request, mock_proclib, mock_genomics_server):
        logger.info("[setup] sexchecker test instance")

        # GIVEN a SexChecker with mock processed library and specified
        # workflow batch ID
        sexchecker = qc.SexChecker(
            processedlibrary=mock_proclib,
            workflowbatch_id=mock_proclib.processed_data[0]['workflowbatch_id'],
            genomics_root=mock_genomics_server['genomics_root']
        )
        def fin():
            logger.info("[teardown] FlowcellRunAnnotator mock instance")
        request.addfinalizer(fin)
        return sexchecker

    def test_load_x_genes(self, checker):
        logger.info("test `_load_x_genes()`")

        # WHEN list of X chromosome gene names are read from stored file
        x_df = checker._load_x_genes()

        # THEN should be a dataframe of expected length
        assert(len(x_df) == 2539)

    def test_load_y_genes(self, checker):
        logger.info("test `_load_y_genes()`")

        # WHEN list of Y chromosome gene names are read from stored file
        y_df = checker._load_y_genes()

        # THEN should be a dataframe of expected length
        assert(len(y_df) == 589)

    def test_get_counts_path(self, checker, mock_genomics_server):
        logger.info("test `_get_counts_path()`")

        # WHEN path for current workflow batch counts file is constructed
        counts_path = checker._get_counts_path()

        # THEN should be a valid path to counts file with expected 'genomics'
        # server root
        assert(counts_path == mock_genomics_server['htseq_counts_file'])

    def test_compute_y_x_ratio(self, checker):
        logger.info("test `_compute_y_x_ratio()`")

        # WHEN ratio of Y genes detected to X genes detected is computed
        y_x_ratio = checker._compute_y_x_ratio()

        # THEN ratio should be expected value
        assert(y_x_ratio == 0)
