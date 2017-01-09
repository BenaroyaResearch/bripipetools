import logging
import os
import re

import pytest
import mock
import mongomock
import pandas as pd

from bripipetools import qc
from bripipetools import util

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def mock_db():
    # GIVEN a mocked version of the TG3 Mongo database
    logger.debug(("[setup] mock database, connect "
                  "to mock Mongo database"))

    yield mongomock.MongoClient().db
    logger.debug(("[teardown] mock database, disconnect "
                  "from mock Mongo database"))


# @pytest.fixture(
#     scope='class',
#     params=[{'runnum': r, 'projectnum': p, 'samplenum': s}
#             for r in range(1)
#             for p in range(3)
#             for s in range(3)])
# def testproclib(request, mock_genomics_server):
#     # GIVEN a processed library object
#     runs = mock_genomics_server['root']['genomics']['illumina']['runs']
#     rundata = runs[request.param['runnum']]
#     projects = rundata['processed']['projects']
#     projectdata = projects[request.param['projectnum']]
#     samples = projectdata['counts']['sources']['htseq']
#     sampledata = samples[request.param['samplenum']]
#     outputs = projectdata['validation']['sources']['sexcheck']
#     outputdata = outputs[request.param['samplenum']]
#
#     logger.info(("[setup] mock processed library object with counts file "
#                  "for sample {}".format(sampledata['sample'])))
#
#     processedlibrary = mock.Mock(
#         _id='{}_{}_processed'.format(sampledata['sample'],
#                                      rundata['flowcell_id']),
#         processed_data=[
#             {'workflowbatch_id': 'globusgalaxy_2016-09-29_1',
#              'outputs': {
#                 'counts': [
#                     {'source': 'htseq',
#                      'name': 'htseq_counts_txt',
#                      'file': re.sub('.*(?=genomics)', '/',
#                                     sampledata['path'])}
#                 ]
#              }
#             }
#         ],
#         parent_id='mock_sample',
#         type='processed library')
#
#     yield processedlibrary, sampledata, outputdata
#     logger.info("[teardown] mock processed library object")


@pytest.fixture(scope='function')
def mock_countfile(s, filename, tmpdir):
    f = tmpdir.join(filename)
    f.write(s)

    return str(f)


@pytest.fixture(scope='function')
def mock_proclib(count_filename=None):
    # GIVEN a processed library object
    mock_batchid = 'globusgalaxy_2016-12-31_1'

    processedlibrary = mock.Mock(
        _id='lib1111_C00000XX_processed',
        processed_data=[
            {'workflowbatch_id': mock_batchid,
             'outputs': {
                'counts': [
                    {'source': 'htseq',
                     'name': 'htseq_counts_txt',
                     'file': count_filename
                     }
                 ]
             }
             }
        ],
        parent_id='mock_sample',
        type='processed library')

    # logger.info("[teardown] mock processed library object")
    return processedlibrary

class TestSexChecker:
    """
    Tests methods for the `SexChecker` class in the
    `bripipetools.qc.sexcheck` module.
    """
    def test_load_x_genes(self, mock_db, tmpdir):

        # AND a SexChecker with mock processed library and specified
        # workflow batch ID
        mock_object = mock_proclib()
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            genomics_root=str(tmpdir),
            db=mock_db
        )

        test_table = checker._load_x_genes()

        assert (len(test_table) == 2539)
        assert (len(test_table.columns) == 1)

    def test_load_y_genes(self, mock_db, tmpdir):

        # AND a SexChecker with mock processed library and specified
        # workflow batch ID
        mock_object = mock_proclib()
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            genomics_root=str(tmpdir),
            db=mock_db
        )

        test_table = checker._load_y_genes()

        assert (len(test_table) == 589)
        assert (len(test_table.columns) == 1)

    def test_get_counts_path(self, mock_db, tmpdir):
        # AND a SexChecker with mock processed library and specified
        # workflow batch ID
        mock_contents = ['ENSG00000000001\t0\n', ]
        mock_filename = 'lib1111_htseq_counts.txt'
        mock_path = mock_countfile(''.join(mock_contents), mock_filename,
                                   tmpdir)

        mock_object = mock_proclib(count_filename=mock_filename)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            genomics_root=str(tmpdir),
            db=mock_db
        )

        test_path = checker._get_counts_path()

        assert (test_path == mock_path)

    def test_get_x_y_counts(self, mock_db, tmpdir):
        mock_contents = ['ENSG00000182888\t1\n',
                         'ENSG00000273773\t1\n',
                         'ENSG00000224873\t1\n',
                         'ENSG00000231159\t1\n', ]

        mock_filename = 'lib1111_htseq_counts.txt'
        mock_path = mock_countfile(''.join(mock_contents), mock_filename,
                                   tmpdir)

        mock_object = mock_proclib(count_filename=mock_filename)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            genomics_root=str(tmpdir),
            db=mock_db
        )

        checker._get_x_y_counts()

        assert checker.x_counts.equals(
            pd.DataFrame([['ENSG00000182888', 1],
                          ['ENSG00000273773', 1]],
                         columns=['geneName', 'count'])
        )
        assert checker.y_counts.equals(
            pd.DataFrame([['ENSG00000224873', 1],
                          ['ENSG00000231159', 1]],
                         columns=['geneName', 'count'])
        )

    def test_compute_x_y_data(self, mock_db, tmpdir):
        mock_contents = ['ENSG00000182888\t1\n',
                         'ENSG00000273773\t2\n',
                         'ENSG00000224873\t1\n',
                         'ENSG00000231159\t2\n', ]

        mock_filename = 'lib1111_htseq_counts.txt'
        mock_countfile(''.join(mock_contents), mock_filename, tmpdir)

        mock_object = mock_proclib(count_filename=mock_filename)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            genomics_root=str(tmpdir),
            db=mock_db
        )

        checker._compute_x_y_data()

        assert (
            checker.data == {'x_genes': 2,
                             'y_genes': 2,
                             'x_counts': 3,
                             'y_counts': 3,
                             'total_counts': 6}
        )

    def test_predict_sex(self, mock_db, tmpdir):
        mock_object = mock_proclib()
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            genomics_root=str(tmpdir),
            db=mock_db
        )

        checker.data = {'x_genes': 2,
                        'y_genes': 2,
                        'x_counts': 3,
                        'y_counts': 3,
                        'total_counts': 6}

        checker._predict_sex()

        # THEN predicted sex should match reported sex
        assert (checker.data['predicted_sex'] in ['male', 'female'])

    def test_verify_sex(self, mock_db, tmpdir):
        mock_object = mock_proclib()
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            genomics_root=str(tmpdir),
            db=mock_db
        )

        checker.data = {'predicted_sex': 'male'}

        # WHEN sex is verified
        checker._verify_sex()

        # THEN predicted sex should match reported sex
        assert (checker.data['sex_check'] == 'NA')

    def test_write_data(self, mock_db, tmpdir):
        mock_contents = ['ENSG00000182888\t1\n',
                         'ENSG00000273773\t2\n',
                         'ENSG00000224873\t1\n',
                         'ENSG00000231159\t2\n', ]

        mock_root = str(tmpdir)
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_projdir = tmpdir.mkdir(mock_runid).mkdir('Project_P1-1Processed')
        mock_countdir = mock_projdir.mkdir('counts')

        mock_filename = 'lib1111_C00000XX_htseq_counts.txt'
        mock_path = mock_countfile(''.join(mock_contents), mock_filename,
                                   mock_countdir)

        mock_filename = str(mock_path).replace(mock_root, '')

        mock_object = mock_proclib(count_filename=mock_filename)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            genomics_root=mock_root,
            db=mock_db
        )

        checker.data = {'x_genes': 2,
                        'y_genes': 2,
                        'x_counts': 3,
                        'y_counts': 3,
                        'total_counts': 6,
                        'predicted_sex': 'male'}

        test_path = checker._write_data()

        mock_path = (mock_projdir.join('validation')
                     .join('lib1111_C00000XX_sexcheck_validation.csv'))

        assert (test_path == str(mock_path))

    def test_update(self, mock_db, tmpdir):
        mock_contents = ['ENSG00000182888\t1\n',
                         'ENSG00000273773\t2\n',
                         'ENSG00000224873\t1\n',
                         'ENSG00000231159\t2\n', ]

        mock_root = str(tmpdir)
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_projdir = tmpdir.mkdir(mock_runid).mkdir('Project_P1-1Processed')
        mock_countdir = mock_projdir.mkdir('counts')

        mock_filename = 'lib1111_C00000XX_htseq_counts.txt'
        mock_path = mock_countfile(''.join(mock_contents), mock_filename,
                                   mock_countdir)

        mock_filename = str(mock_path).replace(mock_root, '')

        mock_object = mock_proclib(count_filename=mock_filename)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            genomics_root=mock_root,
            db=mock_db
        )

        # WHEN sex check validation is appended to processed data for the
        # processed library
        processedlibrary = checker.update()

        # THEN the processed library object should include the expected
        # validation fields
        assert (
            all(
                [field in
                 processedlibrary.processed_data[0]['validation']['sex_check']
                 for field in ['x_genes', 'y_genes', 'x_counts', 'y_counts',
                               'total_counts', 'y_x_gene_ratio', 'y_x_count_ratio',
                               'predicted_sex', 'sex_check']]
            )
        )


# class TestSexChecker:
#     @pytest.fixture(scope='class')
#     def checkerdata(self, testproclib, mock_db, mock_genomics_server):
#         # (GIVEN)
#         mock_proclib, sampledata, outputdata = testproclib
#
#         logger.info("[setup] SexChecker test instance")
#
#         # AND a SexChecker with mock processed library and specified
#         # workflow batch ID
#         sexchecker = qc.SexChecker(
#             processedlibrary=mock_proclib,
#             reference='grch38',
#             workflowbatch_id=mock_proclib.processed_data[0]['workflowbatch_id'],
#             genomics_root=mock_genomics_server['root']['path'],
#             db=mock_db
#         )
#
#         yield sexchecker, sampledata, outputdata
#         logger.info("[teardown] SexChecker mock instance")
#
#     def test_load_x_genes(self, checkerdata):
#         # (GIVEN)
#         checker, _, _ = checkerdata
#
#         logger.info("test `_load_x_genes()`")
#
#         # WHEN list of X chromosome gene names are read from stored file
#         x_df = checker._load_x_genes()
#
#         # THEN should be a dataframe of expected length
#         assert(len(x_df) == 2539)
#
#     def test_load_y_genes(self, checkerdata):
#         # (GIVEN)
#         checker, _, _ = checkerdata
#
#         logger.info("test `_load_y_genes()`")
#
#         # WHEN list of Y chromosome gene names are read from stored file
#         y_df = checker._load_y_genes()
#
#         # THEN should be a dataframe of expected length
#         assert(len(y_df) == 589)
#
#     def test_get_counts_path(self, checkerdata):
#         # (GIVEN)
#         checker, sampledata, _ = checkerdata
#
#         logger.info("test `_get_counts_path()`")
#
#         # WHEN path for current workflow batch counts file is constructed
#         counts_path = checker._get_counts_path()
#
#         # THEN should be a valid path to counts file with expected 'genomics'
#         # server root
#         assert(counts_path == sampledata['path'])
#
#     def test_get_x_y_counts(self, checkerdata):
#         # (GIVEN)
#         checker, sampledata, _ = checkerdata
#
#         logger.info("test `_get_gene_data()`")
#
#         # WHEN counts for X and Y genes are extracted
#         checker._get_x_y_counts()
#
#         # THEN X and Y count dfs should be expected length
#         assert(len(checker.x_counts) == sampledata['x_total'])
#         assert(len(checker.y_counts) == sampledata['y_total'])
#
#     def test_compute_x_y_data(self, checkerdata):
#         # (GIVEN)
#         checker, sampledata, _ = checkerdata
#
#         # WHEN gene and read totals are computed for X and Y genes
#         checker._compute_x_y_data()
#
#         # THEN X and Y data should match expected results
#         assert(checker.data['x_genes'] == sampledata['x_total'])
#         assert(checker.data['x_counts'] == sampledata['x_count'])
#         assert(checker.data['y_genes'] == sampledata['y_total'])
#         assert(checker.data['y_counts'] == sampledata['y_count'])
#
#     def test_predict_sex(self, checkerdata):
#         # (GIVEN)
#         checker, _, _ = checkerdata
#
#         # WHEN sex is predicted
#         checker._predict_sex()
#
#         # THEN predicted sex should match reported sex
#         assert(checker.data['predicted_sex'] in ['male', 'female'])
#
#     def test_verify_sex(self, checkerdata):
#         # (GIVEN)
#         checker, _, _ = checkerdata
#
#         # WHEN sex is verified
#         checker._verify_sex()
#
#         # THEN predicted sex should match reported sex
#         assert (checker.data['sex_check'] == 'NA')
#
#     def test_write_data(self, checkerdata):
#         # (GIVEN)
#         checker, _, outputdata = checkerdata
#
#         # AND combined file does not already exist
#         expected_path = outputdata['path']
#         try:
#             os.remove(expected_path)
#         except OSError:
#             pass
#
#         # WHEN sex check data (a dict) is written to a new validation file
#         data = {'x_genes': None, 'y_genes': None,
#                 'x_counts': None, 'y_counts': None, 'total_counts': None,
#                 'y_x_gene_ratio': None, 'y_x_count_ratio': None,
#                 'sexcheck_eqn': None, 'sexcheck_cutoff': None,
#                 'predicted_sex': None, 'sex_check': None}
#         output = checker._write_data(data)
#
#         assert(output == expected_path)
#         assert(os.path.exists(expected_path))
#
#     def test_update(self, checkerdata):
#         # (GIVEN)
#         checker, sampledata, _ = checkerdata
#
#         # WHEN sex check validation is appended to processed data for the
#         # processed library
#         processedlibrary = checker.update()
#
#         # THEN the processed library object should include the expected
#         # validation fields
#         assert(all(
#             [field in
#              processedlibrary.processed_data[0]['validation']['sex_check']
#              for field in ['x_genes', 'y_genes', 'x_counts', 'y_counts',
#                            'total_counts', 'y_x_gene_ratio', 'y_x_count_ratio',
#                            'predicted_sex', 'sex_check']]))
#
#
# class TestSexPredict:
#     @pytest.fixture(scope='class')
#     def predictordata(self, testproclib):
#         # (GIVEN)
#         _, sampledata, _ = testproclib
#         mock_countdata = {'x_genes': sampledata['x_total'],
#                           'y_genes': sampledata['y_total'],
#                           'x_counts': sampledata['x_count'],
#                           'y_counts': sampledata['y_count'],
#                           'total_counts': 10000}
#         logger.info("[setup] SexPredictor test instance")
#
#         # AND
#         sexpredictor = qc.SexPredictor(
#             data=mock_countdata,
#         )
#
#         yield sexpredictor, sampledata
#         logger.info("[teardown] SexPredictor mock instance")
#
#     def test_compute_y_x_gene_ratio(self, predictordata):
#         # (GIVEN)
#         predictor, sampledata = predictordata
#         expected_y_x_ratio = (float(sampledata['y_total'])
#                               / float(sampledata['x_total']))
#
#         logger.info("test `_compute_y_x_ratio()`")
#
#         # WHEN ratio of Y genes detected to X genes detected is computed
#         predictor._compute_y_x_gene_ratio()
#
#         # THEN ratio should be expected value
#         assert(predictor.data['y_x_gene_ratio'] == expected_y_x_ratio)
#
#     def test_compute_y_x_count_ratio(self, predictordata):
#         # (GIVEN)
#         predictor, sampledata = predictordata
#         expected_y_x_ratio = (float(sampledata['y_count'])
#                               / float(sampledata['x_count']))
#
#         logger.info("test `_compute_y_x_ratio()`")
#
#         # WHEN ratio of Y counts to X counts is computed
#         predictor._compute_y_x_count_ratio()
#
#         # THEN ratio should be expected value
#         assert(predictor.data['y_x_count_ratio'] == expected_y_x_ratio)
#
#     def test_predict_sex(self, predictordata):
#         # (GIVEN)
#         predictor, _ = predictordata
#
#         logger.info("test `_predict_sex()`")
#
#         # WHEN sex is predicted
#         predictor._predict_sex()
#
#         # THEN predicted sex should match reported sex
#         assert(predictor.data['predicted_sex'] in ['male', 'female'])
#
#     def test_predict(self, predictordata):
#         # (GIVEN)
#         predictor, _ = predictordata
#
#         logger.info("test `predict()`")
#
#         # WHEN sex is predicted
#         predictor.predict()
#
#         # THEN predicted sex should match reported sex
#         assert(predictor.data['predicted_sex'] in ['male', 'female'])
#
#
# class TestSexVerifier:
#     @pytest.fixture(scope='class')
#     def verifierdata(self, testproclib, mock_db):
#         # (GIVEN)
#         processedlibrary, sampledata, _ = testproclib
#         testdata = {'predicted_sex': 'male'}
#
#         logger.info("[setup] SexVerifier test instance")
#
#         # AND
#         sexverifier = qc.SexVerifier(
#             data=testdata,
#             processedlibrary=processedlibrary,
#             db=mock_db,
#         )
#
#         yield sexverifier, sampledata
#         logger.info("[teardown] SexVerifier mock instance")
#
#     def test_retrieve_sex(self, verifierdata, testproclib, mock_db):
#         # (GIVEN)
#         verifier, _ = verifierdata
#
#         # AND a hierarchy of objects in the 'samples' collection, with
#         # parent relationship specified by the 'parentId' field
#         mock_db.samples.insert(
#             {'_id': testproclib[0]._id, 'parentId': testproclib[0].parent_id})
#         mock_db.samples.insert(
#             {'_id': 'mock_sample', 'reportedSex': 'male'})
#
#         # WHEN searching for the field among all sample ancestors in
#         # the hierarchy
#         reported_sex = verifier._retrieve_sex('mock_sample')
#
#         # THEN
#         assert(reported_sex == 'male')
#
#         mock_db.samples.drop()
#
#     def test_verify(self, verifierdata):
#         # (GIVEN)
#         verifier, _ = verifierdata
#
#         assert(verifier.verify()['sex_check'] == 'NA')
