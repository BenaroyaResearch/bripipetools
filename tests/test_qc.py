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
            for p in range(3)
            for s in range(3)])
def mock_proclibdata(request, mock_genomics_server):
    # GIVEN a processed library object
    runs = mock_genomics_server['root']['genomics']['illumina']['runs']
    rundata = runs[request.param['runnum']]
    projects = rundata['processed']['projects']
    projectdata = projects[request.param['projectnum']]
    samples = projectdata['counts']['sources']['htseq']
    sampledata = samples[request.param['samplenum']]
    outputs = projectdata['validation']['sources']['sexcheck']
    outputdata = outputs[request.param['samplenum']]

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
    return (processedlibrary, sampledata, outputdata)

@pytest.mark.usefixtures('mock_proclibdata', 'mock_genomics_server')
class TestSexChecker:
    @pytest.fixture(scope='class')
    def checkerdata(self, request, mock_proclibdata, mock_genomics_server):
        # (GIVEN)
        mock_proclib, sampledata, outputdata = mock_proclibdata

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
        return (sexchecker, sampledata, outputdata)

    def test_load_x_genes(self, checkerdata):
        # (GIVEN)
        checker, _, _ = checkerdata

        logger.info("test `_load_x_genes()`")

        # WHEN list of X chromosome gene names are read from stored file
        x_df = checker._load_x_genes()

        # THEN should be a dataframe of expected length
        assert(len(x_df) == 2539)

    def test_load_y_genes(self, checkerdata):
        # (GIVEN)
        checker, _, _ = checkerdata

        logger.info("test `_load_y_genes()`")

        # WHEN list of Y chromosome gene names are read from stored file
        y_df = checker._load_y_genes()

        # THEN should be a dataframe of expected length
        assert(len(y_df) == 589)

    def test_get_counts_path(self, checkerdata):
        # (GIVEN)
        checker, sampledata, _ = checkerdata

        logger.info("test `_get_counts_path()`")

        # WHEN path for current workflow batch counts file is constructed
        counts_path = checker._get_counts_path()

        # THEN should be a valid path to counts file with expected 'genomics'
        # server root
        assert(counts_path == sampledata['path'])

    def test_get_x_y_counts(self, checkerdata):
        # (GIVEN)
        checker, sampledata, _ = checkerdata

        logger.info("test `_get_gene_data()`")

        # WHEN counts for X and Y genes are extracted
        checker._get_x_y_counts()

        # THEN X and Y count dfs should be expected length
        assert(len(checker.x_counts) == sampledata['x_total'])
        assert(len(checker.y_counts) == sampledata['y_total'])

    def test_compute_x_y_data(self, checkerdata):
        # (GIVEN)
        checker, sampledata, _ = checkerdata

        # WHEN gene and read totals are computed for X and Y genes
        checker._compute_x_y_data()

        # THEN X and Y data should match expected results
        assert(checker.data['x_genes'] == sampledata['x_total'])
        assert(checker.data['x_reads'] == sampledata['x_count'])
        assert(checker.data['y_genes'] == sampledata['y_total'])
        assert(checker.data['y_reads'] == sampledata['y_count'])

    def test_compute_y_x_gene_ratio(self, checkerdata):
        # (GIVEN)
        checker, sampledata, _ = checkerdata
        expected_y_x_ratio = (float(sampledata['y_total'])
                              / float(sampledata['x_total']))

        logger.info("test `_compute_y_x_ratio()`")

        # WHEN ratio of Y genes detected to X genes detected is computed
        checker._compute_y_x_gene_ratio()

        # THEN ratio should be expected value
        assert(checker.data['y_x_gene_ratio'] == expected_y_x_ratio)

    def test_compute_y_x_count_ratio(self, checkerdata):
        # (GIVEN)
        checker, sampledata, _ = checkerdata
        expected_y_x_ratio = (float(sampledata['y_count'])
                              / float(sampledata['x_count']))

        logger.info("test `_compute_y_x_ratio()`")

        # WHEN ratio of Y reads to X reads is computed
        checker._compute_y_x_count_ratio()

        # THEN ratio should be expected value
        assert(checker.data['y_x_count_ratio'] == expected_y_x_ratio)

    def test_predict_sex(self, checkerdata):
        # (GIVEN)
        checker, sampledata, _ = checkerdata
        expected_y_x_ratio = (float(sampledata['y_total'])
                     / float(sampledata['x_total']))
        expected_prediction = 'male' if expected_y_x_ratio > 0.01 else 'female'

        logger.info("test `_predict_sex()`")

        # WHEN sex is predicted from a ratio that should indicate male
        # (> 0.01)
        checker._predict_sex()

        # THEN predicted sex should be 'male'
        assert(checker.data['predicted_sex'] == expected_prediction)

    def test_write_data(self, checkerdata):
        # (GIVEN)
        checker, _, outputdata = checkerdata

        logger.info("test `_predict_sex()`")

        # AND combined file does not already exist
        expected_path = outputdata['path']
        try:
            os.remove(expected_path)
        except OSError:
            pass

        # WHEN sex check data (a dict) is written to a new validation file
        output = checker._write_data({'foo': 0, 'bar': 'a'})

        assert(output == expected_path)
        assert(os.path.exists(expected_path))

    def test_update(self, checkerdata):
        # (GIVEN)
        checker, sampledata, _ = checkerdata
        expected_y_x_ratio = (float(sampledata['y_total'])
                     / float(sampledata['x_total']))

        logger.info("test `update()`")

        # WHEN sex check validation is appended to processed data for the
        # processed library
        processedlibrary = checker.update()

        # THEN the processed library object should include the expected
        # validation fields
        assert(all(
            [field in
             processedlibrary.processed_data[0]['validation']['sex_check']
             for field in ['x_genes', 'y_genes', 'x_reads', 'y_reads',
                           'y_x_gene_ratio', 'y_x_count_ratio',
                           'predicted_sex', 'sexcheck_pass']]))
