import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
import re

import pytest
import mock

from bripipetools import qc
from bripipetools import util

@pytest.fixture(
    scope='class',
    params=[{'runnum': r, 'projectnum': p, 'samplenum': s}
            for r in range(1)
            for p in range(1)
            for s in range(3)])
def mock_proclibdata(request, mock_genomics_server):
    # GIVEN a processed library object
    runs = mock_genomics_server['root']['genomics']['illumina']['runs']
    rundata = runs[request.param['runnum']]
    projects = rundata['processed']['projects']
    projectdata = projects[request.param['projectnum']]
    samples = projectdata['counts']['sources']['htseq']
    sampledata = samples[request.param['samplenum']]

    logger.info(("[setup] mock processed library object with counts file "
                 "for sample {}".format(sampledata['sample'])))

    processedlibrary = mock.Mock(
        _id='{}_{}_processed'.format(sampledata['sample'],
                                     rundata['flowcell_id']),
        processed_data=[
            {'workflowbatch_id': 'globusgalaxy_2016-09-29_1',
             'outputs': {
                'counts': [
                    {'source': 'htseq',
                     'name': 'htseq_counts_txt',
                     'file': re.sub('.*(?=genomics)', '/',
                                    sampledata['path'])}
                ]
             }
            }
        ],
        type='processed library')

    def fin():
        logger.info(("[teardown] mock processed library object"))
    request.addfinalizer(fin)
    return (processedlibrary, sampledata)

@pytest.mark.usefixtures('mock_proclibdata', 'mock_genomics_server')
class TestSexChecker:
    @pytest.fixture(scope='class')
    def checkerdata(self, request, mock_proclibdata, mock_genomics_server):
        # (GIVEN)
        mock_proclib, sampledata = mock_proclibdata

        logger.info("[setup] sexchecker test instance")

        # AND a SexChecker with mock processed library and specified
        # workflow batch ID
        sexchecker = qc.SexChecker(
            processedlibrary=mock_proclib,
            workflowbatch_id=mock_proclib.processed_data[0]['workflowbatch_id'],
            genomics_root=mock_genomics_server['root']['path'])

        def fin():
            logger.info("[teardown] FlowcellRunAnnotator mock instance")
        request.addfinalizer(fin)
        return (sexchecker, sampledata)

    def test_load_x_genes(self, checkerdata):
        # (GIVEN)
        checker, _ = checkerdata

        logger.info("test `_load_x_genes()`")

        # WHEN list of X chromosome gene names are read from stored file
        x_df = checker._load_x_genes()

        # THEN should be a dataframe of expected length
        assert(len(x_df) == 2539)

    def test_load_y_genes(self, checkerdata):
        # (GIVEN)
        checker, _ = checkerdata

        logger.info("test `_load_y_genes()`")

        # WHEN list of Y chromosome gene names are read from stored file
        y_df = checker._load_y_genes()

        # THEN should be a dataframe of expected length
        assert(len(y_df) == 589)

    def test_get_counts_path(self, checkerdata):
        # (GIVEN)
        checker, sampledata = checkerdata

        logger.info("test `_get_counts_path()`")

        # WHEN path for current workflow batch counts file is constructed
        counts_path = checker._get_counts_path()

        # THEN should be a valid path to counts file with expected 'genomics'
        # server root
        assert(counts_path == sampledata['path'])

    def test_compute_y_x_ratio(self, checkerdata):
        # (GIVEN)
        checker, sampledata = checkerdata
        expected_y_x_ratio = (float(sampledata['y_total'])
                     / float(sampledata['x_total']))

        logger.info("test `_compute_y_x_ratio()`")

        # WHEN ratio of Y genes detected to X genes detected is computed
        y_x_ratio = checker._compute_y_x_ratio()

        # THEN ratio should be expected value
        assert(y_x_ratio == expected_y_x_ratio)

    def test_predict_sex_male(self, checkerdata):
        # (GIVEN)
        checker, _ = checkerdata

        logger.info("test `_predict_sex()`, male ratio")

        # WHEN sex is predicted from a ratio that should indicate male (> 0.1)
        predicted_sex = checker._predict_sex(0.5)

        # THEN predicted sex should be 'male'
        assert(predicted_sex == 'male')

    def test_predict_sex_female(self, checkerdata):
        # (GIVEN)
        checker, _ = checkerdata

        logger.info("test `_predict_sex()`, female ratio")

        # WHEN sex is predicted from a ratio that indicates female (<= 0.1)
        predicted_sex = checker._predict_sex(0.05)

        # THEN predicted sex should be 'female'
        assert(predicted_sex == 'female')

    def test_update(self, checkerdata):
        # (GIVEN)
        checker, sampledata = checkerdata
        expected_y_x_ratio = (float(sampledata['y_total'])
                     / float(sampledata['x_total']))

        logger.info("test `append()`")

        # WHEN sex check validation is appended to processed data for the
        # processed library
        processedlibrary = checker.update()

        # THEN the processed library object should include the expected
        # validation fields
        assert(processedlibrary.processed_data[0]['validations']['sex_check']
               == {'y_x_ratio': expected_y_x_ratio,
                   'predicted_sex': 'female',
                   'pass': None})
