import logging

import mock
import mongomock
import pandas as pd
import pytest

from bripipetools import qc

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


@pytest.fixture(scope='function')
def mock_stringfile(s, filename, tmpdir):
    f = tmpdir.join(filename)
    f.write(s)

    return str(f)


@pytest.fixture(scope='function')
def mock_proclib(count_filename=None):
    # GIVEN a processed library object
    mock_batchid = 'globusgalaxy_2016-12-31_1'

    processedlibrary = mock.Mock(
        _id='lib1111_C00000XX_processed',
        processed_data=[{
            'workflowbatch_id': mock_batchid,
            'outputs': {
                'counts': [{'source': 'htseq',
                            'name': 'htseq_counts_txt',
                            'file': count_filename}]
            }
        }],
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
        # GIVEN data for a processed library from a specified workflow batch
        # and and a connection to a database
        mock_object = mock_proclib()
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a SexChecker is created for the processed library and
        # corresponding workflow batch ID
        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            pipeline_root=str(tmpdir),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN X chromosome genes are loaded from expected package file
        test_table = checker._load_x_genes()

        # THEN the genes should be returned in a single column data frame
        assert (len(test_table) == 2539)
        assert (len(test_table.columns) == 1)

    def test_load_y_genes(self, mock_db, tmpdir):
        # GIVEN data for a processed library from a specified workflow batch
        # and and a connection to a database
        mock_object = mock_proclib()
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a SexChecker is created for the processed library and
        # corresponding workflow batch ID
        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            pipeline_root=str(tmpdir),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN Y chromosome genes are loaded from expected package file
        test_table = checker._load_y_genes()

        # THEN the genes should be returned in a single column data frame
        assert (len(test_table) == 589)
        assert (len(test_table.columns) == 1)

    def test_get_counts_path(self, mock_db, tmpdir):
        # GIVEN data for a processed library from a specified workflow batch
        # and and a connection to a database, and a file of gene counts
        # exists for the library from the workflow batch
        mock_contents = ['ENSG00000000001\t0\n', ]
        mock_filename = 'lib1111_htseq_counts.txt'
        mock_path = mock_stringfile(''.join(mock_contents), mock_filename,
                                    tmpdir)
        mock_object = mock_proclib(count_filename=mock_filename)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a SexChecker is created for the processed library and
        # corresponding workflow batch ID
        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            pipeline_root=str(tmpdir),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN the full path to the counts file is retrieved
        test_path = checker._get_counts_path()

        # THEN the path should match the expected result
        assert (test_path == mock_path)

    def test_get_x_y_counts(self, mock_db, tmpdir):
        # GIVEN data for a processed library from a specified workflow batch
        # and and a connection to a database, and a file of gene counts
        # exists for the library from the workflow batch
        mock_contents = ['ENSG00000182888\t1\n',
                         'ENSG00000273773\t1\n',
                         'ENSG00000224873\t1\n',
                         'ENSG00000231159\t1\n', ]
        mock_filename = 'lib1111_htseq_counts.txt'
        mock_stringfile(''.join(mock_contents), mock_filename, tmpdir)
        mock_object = mock_proclib(count_filename=mock_filename)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a SexChecker is created for the processed library and
        # corresponding workflow batch ID
        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            pipeline_root=str(tmpdir),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN X and Y chromosome specific counts are extracted from the
        # library counts file and stored as separate attributes on the
        # checker object
        checker._get_x_y_counts()

        # THEN the 'x_counts' and 'y_counts' attributes should be data
        # frames, containing counts for X and Y genes, respectively
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
        # GIVEN data for a processed library from a specified workflow batch
        # and and a connection to a database, and a file of gene counts
        # exists for the library from the workflow batch
        mock_contents = ['ENSG00000182888\t1\n',
                         'ENSG00000273773\t2\n',
                         'ENSG00000224873\t1\n',
                         'ENSG00000231159\t2\n', ]
        mock_filename = 'lib1111_htseq_counts.txt'
        mock_stringfile(''.join(mock_contents), mock_filename, tmpdir)
        mock_object = mock_proclib(count_filename=mock_filename)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a SexChecker is created for the processed library and
        # corresponding workflow batch ID
        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            pipeline_root=str(tmpdir),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN all X and Y related count data are pre-computed, then results
        # should be stored in a dictionary under the checker object's 'data'
        # attribute and include fields for '_genes' (the number of genes
        # detected with count > 0), and '_counts' (the sum of raw counts)
        # for X and Y genes, as well as total counts
        checker._compute_x_y_data()

        # THEN the summarized X/Y count data should match expected results
        assert (
            checker.data == {'x_genes': 2,
                             'y_genes': 2,
                             'x_counts': 3,
                             'y_counts': 3,
                             'total_counts': 6}
        )

    def test_predict_sex(self, mock_db, tmpdir):
        # GIVEN data for a processed library from a specified workflow batch
        # and and a connection to a database
        mock_object = mock_proclib()
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a SexChecker is created for the processed library and
        # corresponding workflow batch ID
        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            pipeline_root=str(tmpdir),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # AND X/Y count summary data are stored as a dict in the object's
        # 'data' attribute
        checker.data = {'x_genes': 2,
                        'y_genes': 2,
                        'x_counts': 3,
                        'y_counts': 3,
                        'total_counts': 6}

        # WHEN the object calls a different class to predict sample sex
        checker._predict_sex()

        # THEN predicted sex should be returned as either 'male' or 'female'
        # (note: the behavior and performance for predicting sex is tested
        # separately for the `sexpredict` module)
        assert (checker.data['predicted_sex'] in ['male', 'female'])

    def test_verify_sex(self, mock_db, tmpdir):
        # GIVEN data for a processed library from a specified workflow batch
        # and and a connection to a database
        mock_object = mock_proclib()
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a SexChecker is created for the processed library and
        # corresponding workflow batch ID
        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            pipeline_root=str(tmpdir),
            db=mock_db,
            run_opts = mock_run_opts
        )

        # AND the result of sex prediction is stored in the object's data
        # attribute under the 'predicted_sex' field
        checker.data = {'predicted_sex': 'male'}

        # WHEN the object calls a different class to verify whether the
        # predicted sex matches the reported sex for the corresponding
        # subject in the database
        checker._verify_sex()

        # THEN the verification result, stored in the 'sex_check' field of
        # the object's 'data' attribute, should indicate either 'pass',
        # 'fail', or 'NA' (note: the behavior for verifying sex is tested
        # separately for the `sexverify` module)
        assert (checker.data['sex_check'] in ['pass', 'fail', 'NA'])

    def test_write_data(self, mock_db, tmpdir):
        # GIVEN data for a processed library from a specified workflow batch
        # and and a connection to a database, and a file of gene counts
        # exists at the path formatted:
        # <run_folder>/<project_folder>/<counts_folder>/<counts_file>
        mock_contents = ['ENSG00000182888\t1\n',
                         'ENSG00000273773\t2\n',
                         'ENSG00000224873\t1\n',
                         'ENSG00000231159\t2\n', ]
        mock_root = str(tmpdir)
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_projdir = tmpdir.mkdir(mock_runid).mkdir('Project_P1-1Processed')
        mock_countdir = mock_projdir.mkdir('counts')
        mock_filename = 'lib1111_C00000XX_htseq_counts.txt'
        mock_path = mock_stringfile(''.join(mock_contents), mock_filename,
                                    mock_countdir)
        mock_countfile = str(mock_path).replace(mock_root, '')
        mock_object = mock_proclib(count_filename=mock_countfile)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a SexChecker is created for the processed library and
        # corresponding workflow batch ID
        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            pipeline_root=mock_root,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # AND X/Y count summary data as well as the result of sex prediction
        # and sex verification are stored as a dict in the object's
        # 'data' attribute
        checker.data = {'x_genes': 2,
                        'y_genes': 2,
                        'x_counts': 3,
                        'y_counts': 3,
                        'total_counts': 6,
                        'predicted_sex': 'male'}

        # WHEN the sex check data is written to a new file under the
        # processed project's 'validation' folder
        test_path = checker._write_data()

        # THEN the file should exist at the expected path
        mock_outpath = (mock_projdir.join('validation')
                        .join('lib1111_C00000XX_sexcheck_validation.csv'))
        assert (test_path == str(mock_outpath))

    def test_update(self, mock_db, tmpdir):
        # GIVEN data for a processed library from a specified workflow batch
        # and and a connection to a database, and a file of gene counts
        # exists at the path formatted:
        # <run_folder>/<project_folder>/<counts_folder>/<counts_file>
        mock_contents = ['ENSG00000182888\t1\n',
                         'ENSG00000273773\t2\n',
                         'ENSG00000224873\t1\n',
                         'ENSG00000231159\t2\n', ]
        mock_root = str(tmpdir)
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_projdir = tmpdir.mkdir(mock_runid).mkdir('Project_P1-1Processed')
        mock_countdir = mock_projdir.mkdir('counts')
        mock_filename = 'lib1111_C00000XX_htseq_counts.txt'
        mock_path = mock_stringfile(''.join(mock_contents), mock_filename,
                                    mock_countdir)
        mock_countfile = str(mock_path).replace(mock_root, '')
        mock_object = mock_proclib(count_filename=mock_countfile)
        mock_batchid = mock_object.processed_data[0]['workflowbatch_id']

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a SexChecker is created for the processed library and
        # corresponding workflow batch ID
        checker = qc.SexChecker(
            processedlibrary=mock_object,
            reference='grch38',
            workflowbatch_id=mock_batchid,
            pipeline_root=mock_root,
            db=mock_db,
            run_opts = mock_run_opts
        )

        # WHEN sex check validation is appended to processed data for the
        # processed library
        test_object = checker.update()

        # THEN the processed library object should include the expected
        # validation fields
        expected_fields = ['x_genes', 'y_genes', 'x_counts', 'y_counts',
                           'total_counts', 'y_x_gene_ratio', 'y_x_count_ratio',
                           'sexcheck_eqn', 'sexcheck_cutoff',
                           'predicted_sex', 'sex_check']
        test_fields = test_object.processed_data[0]['validation']['sex_check']
        assert (all([field in expected_fields for field in test_fields]))


class TestSexPredictor:
    """
    Tests methods for the `SexPredictor` class in the
    `bripipetools.qc.sexpredict` module.
    """
    def test_compute_y_x_gene_ratio(self):
        # GIVEN a dictionary with X/Y chromosome gene count summary data
        # from a processed library
        mock_data = {'x_genes': 1,
                     'y_genes': 2,
                     'x_counts': 4,
                     'y_counts': 6,
                     'total_counts': 10}

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a predictor object created for the data
        predictor = qc.SexPredictor(data=mock_data, run_opts=mock_run_opts)

        # WHEN the ratio of detected Y genes to detected X genes is
        # computed and stored in the 'y_x_gene_ratio' field of the
        # predictor object's 'data' attribute
        predictor._compute_y_x_gene_ratio()

        # THEN the value of the ratio should match the expected result,
        # which is equal to 'y_genes' / 'x_genes'
        test_data = predictor.data
        assert (test_data['y_x_gene_ratio'] == 2)

    def test_compute_y_x_count_ratio(self):
        # GIVEN a dictionary with X/Y chromosome gene count summary data
        # from a processed library
        mock_data = {'x_genes': 1,
                     'y_genes': 2,
                     'x_counts': 4,
                     'y_counts': 6,
                     'total_counts': 10}

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a predictor object created for the data
        predictor = qc.SexPredictor(data=mock_data, run_opts=mock_run_opts)

        # WHEN the ratio of total Y counts to total X counts is
        # computed and stored in the 'y_x_count_ratio' field of the
        # predictor object's 'data' attribute
        predictor._compute_y_x_count_ratio()

        # THEN the value of the ratio should match the expected result,
        # which is equal to 'y_counts' / 'x_counts'
        test_data = predictor.data
        assert (test_data['y_x_count_ratio'] == 1.5)

    def test_predict_sex(self):
        # GIVEN a dictionary with X/Y chromosome gene count summary data
        # from a processed library
        mock_data = {'x_genes': 1,
                     'y_genes': 2,
                     'x_counts': 4,
                     'y_counts': 6,
                     'total_counts': 10}

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a predictor object created for the data
        predictor = qc.SexPredictor(data=mock_data, run_opts=mock_run_opts)

        # WHEN sex is predicted based on a pre-determined function of
        # X and Y gene counts and stored in the 'predicted_sex' field
        # of the predictor object's 'data' attribute
        # (note: the default function is currently
        # male IF (y_counts^2 / total_counts) > 1 ELSE female;
        # rather than changing this within the SexPredictor class, it may
        # be preferable to encapsulate the sex predict strategy within
        # a separate class or set of classes)
        predictor._predict_sex()

        # THEN predicted sex should match the expected result
        assert (predictor.data['predicted_sex'] == 'male')

    def test_predict(self):
        # GIVEN a dictionary with X/Y chromosome gene count summary data
        # from a processed library
        mock_data = {'x_genes': 1,
                     'y_genes': 2,
                     'x_counts': 4,
                     'y_counts': 6,
                     'total_counts': 10}

        # AND a set of quality control options
        mock_run_opts = {"sexmodel":'y_sq_over_tot', "sexcutoff":1}

        # AND a predictor object created for the data
        predictor = qc.SexPredictor(data=mock_data, run_opts=mock_run_opts)

        # WHEN sex is predicted
        predictor.predict()

        # THEN predicted sex should match reported sex
        assert (predictor.data['predicted_sex'] in ['male', 'female'])


class TestSexVerifier:
    """
    Tests methods for the `SexVerifier` class in the
    `bripipetools.qc.sexverify` module.
    """
    def test_retrieve_sex(self, mock_db):
        # GIVEN a processed library object and corresponding dictionary
        # with X/Y chromosome gene count summary data
        mock_object = mock_proclib()
        mock_data = {'x_genes': 1,
                     'y_genes': 2,
                     'x_counts': 4,
                     'y_counts': 6,
                     'total_counts': 10,
                     'predicted_sex': 'male'}

        # AND a SexVerifier object is created for the processed library
        # and associated X/Y count data
        verifier = qc.SexVerifier(
            data=mock_data,
            processedlibrary=mock_object,
            db=mock_db
        )

        # AND a hierarchy of documents exists in the 'samples' collection,
        # with parent relationship specified by the 'parentId' field
        mock_db.samples.insert(
            {'_id': mock_object._id, 'parentId': mock_object.parent_id}
        )
        mock_db.samples.insert(
            {'_id': mock_object.parent_id, 'reportedSex': 'male'}
        )

        # WHEN the 'reportedSex' for the processed library is retrieved
        # from an upstream parent sample
        test_result = verifier._retrieve_sex(mock_object.parent_id)

        # THEN the reported sex should match the expected result
        assert (test_result == 'male')

    def test_verify(self, mock_db):
        # GIVEN a processed library object and corresponding dictionary
        # with X/Y chromosome gene count summary data
        mock_object = mock_proclib()
        mock_data = {'x_genes': 1,
                     'y_genes': 2,
                     'x_counts': 4,
                     'y_counts': 6,
                     'total_counts': 10,
                     'predicted_sex': 'male'}

        # AND a SexVerifier object is created for the processed library
        # and associated X/Y count data
        verifier = qc.SexVerifier(
            data=mock_data,
            processedlibrary=mock_object,
            db=mock_db
        )

        # AND a hierarchy of documents exists in the 'samples' collection,
        # with parent relationship specified by the 'parentId' field
        mock_db.samples.insert(
            {'_id': mock_object._id, 'parentId': mock_object.parent_id}
        )
        mock_db.samples.insert(
            {'_id': mock_object.parent_id, 'reportedSex': 'male'}
        )

        # WHEN predicted sex for the processed library is verified, and
        # the result is stored in the 'sex_check' field of the returned
        # data dictionary
        test_data = verifier.verify()

        # THEN verification result should match expected result
        assert (test_data['sex_check'] == 'pass')
