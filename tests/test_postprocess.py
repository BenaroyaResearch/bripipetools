import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
import re
import shutil

import pytest

from bripipetools import postprocess
from bripipetools import io

@pytest.mark.usefixtures('mock_genomics_server')
class TestOutputStitcher:
    @pytest.fixture(
        scope='class',
        params=[(out_type, {'runnum': r, 'projectnum': p})
                for r in range(1)
                for p in range(3)
                for out_type in ['metrics', 'qc', 'counts']])
    def outputstitcherdata(self, request, mock_genomics_server):
        # GIVEN a OutputStitcher with mock 'genomics' server path to outputs
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param[1]['runnum']]
        projects = rundata['processed']['projects']
        projectdata = projects[request.param[1]['projectnum']]
        outputdata = projectdata[request.param[0]]

        logger.info("[setup] OutputStitcher test instance "
                    "for output type '{}'".format(request.param))

        outputstitcher = postprocess.OutputStitcher(
            path=outputdata['path'])

        def fin():
            logger.info("[teardown] OutputStitcher mock instance")
        request.addfinalizer(fin)
        return (outputstitcher, outputdata, request.param[0])

    def test_sniff_output_type(self, outputstitcherdata):
        # (GIVEN)
        outputstitcher, _, out_type = outputstitcherdata

        logger.info("test `_sniff_output_type()`")

        # WHEN the file specified by path is read
        output_type = outputstitcher._sniff_output_type()

        # THEN output type should match expected type
        assert(output_type == out_type)

    def test_get_outputs(self, outputstitcherdata):
        # (GIVEN)
        outputstitcher, outputdata, _ = outputstitcherdata

        logger.info("test `_get_outputs()`")

        # WHEN the list of output files is collected
        outputs = outputstitcher._get_outputs(outputstitcher.type)

        # THEN the expected number of outputs should be found
        assert(len(outputs)
               == sum(map(lambda x: len(x),
                      outputdata['sources'].values())))

    @pytest.mark.parametrize(
        'output,expected',
        [(('metrics', 'htseq'), getattr(io, 'HtseqMetricsFile')),
         (('metrics', 'picard_rnaseq'), getattr(io, 'PicardMetricsFile')),
         (('metrics', 'picard_markdups'), getattr(io, 'PicardMetricsFile')),
         (('metrics', 'picard_align'), getattr(io, 'PicardMetricsFile')),
         (('metrics', 'tophat_stats'), getattr(io, 'TophatStatsFile')),
         (('qc', 'fastqc'), getattr(io, 'FastQCFile')),
         (('counts', 'htseq'), getattr(io, 'HtseqCountsFile'))])
    def test_get_parser(self, outputstitcherdata, output, expected):
        # (GIVEN)
        outputstitcher, _, _ = outputstitcherdata

        logger.info("test `_get_parser()`")

        # WHEN the parser is retrieved given output type and source
        parser = outputstitcher._get_parser(output[0], output[1])

        # THEN the expected number of outputs should be found
        assert(parser == expected)

    def test_read_data(self, outputstitcherdata):
        # (GIVEN)
        outputstitcher, outputdata, out_type = outputstitcherdata

        logger.info("test `_read_data()`")

        # WHEN data from each output file is read and parsed
        outputstitcher._read_data()
        data = outputstitcher.data[out_type]

        # THEN data should be stored in a dictionary named for the current
        # output type, with a sub-dict for each output source
        assert(all([len(data[s]) == len(outputdata['sources'])
                    for s in data]))

    def test_build_table(self, outputstitcherdata):
        # (GIVEN)
        outputstitcher, outputdata, out_type = outputstitcherdata

        logger.info("test `_build_table()`")

        # WHEN data is combined into a table
        outputstitcher._read_data()
        table_data = outputstitcher._build_table()

        # THEN table should have expected number of rows, and rows should
        # be the same length
        assert(len(table_data) == outputdata['combined']['len_table'])

    def test_build_combined_filename(self, outputstitcherdata):
        # (GIVEN)
        outputstitcher, outputdata, out_type = outputstitcherdata

        logger.info("test `_build_combined_filename()`")

        # WHEN path to outputs is parsed to build combined CSV file_name
        combined_filename = outputstitcher._build_combined_filename()

        # THEN combined filename should be correctly formatted
        output_type = outputstitcher.type
        assert(combined_filename
               == os.path.basename(outputdata['combined']['path']))

    def test_build_overrepresented_seq_table(self, outputstitcherdata):
        # (GIVEN)
        outputstitcher, outputdata, out_type = outputstitcherdata

        # WHEN overrepresented sequences are combined into a table
        overrep_seq_table = outputstitcher._build_overrepresented_seq_table()

        if out_type == 'qc':
            assert(len(overrep_seq_table)
                   == sum(map(lambda x: x['num_overrep_seqs'],
                          outputdata['sources']['fastqc'])))
        else:
            assert(len(overrep_seq_table) == 0)

    def test_write_overrepresented_seq_table(self, outputstitcherdata):
        # (GIVEN)
        outputstitcher, outputdata, out_type = outputstitcherdata

        # AND combined overrepresented seqs file does not already exist
        if out_type == 'qc':
            expected_path = outputdata['combined_overrep_seqs']['path']
            try:
                os.remove(expected_path)
            except OSError:
                pass

            # WHEN data is read and combined overrepresented seqs are written
            # to file
            outputstitcher.write_overrepresented_seq_table()

            # THEN file should exist at expected path
            assert(os.path.exists(expected_path))

    def test_write_table(self, outputstitcherdata):
        # (GIVEN)
        outputstitcher, outputdata, out_type = outputstitcherdata

        logger.info("test `write_table()`")

        # AND combined file does not already exist
        expected_path = outputdata['combined']['path']
        try:
            os.remove(expected_path)
        except OSError:
            pass

        # WHEN data is read, combined, and written to file
        outputstitcher.write_table()

        # THEN file should exist at expected path
        assert(os.path.exists(expected_path))


class TestOutputCompiler:
    @pytest.fixture(
        scope='class',
        params=[{'runnum': r, 'projectnum': p}
                for r in range(1)
                for p in range(3)])
    def compilerdata(self, request, mock_genomics_server):
        # GIVEN a OutputCompiler with list of mock 'genomics' server path to
        # combined output files
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param['runnum']]
        projects = rundata['processed']['projects']
        projectdata = projects[request.param['projectnum']]
        outputs = [projectdata[out_type]['combined']
                   for out_type in projectdata
                   if out_type not in ['path', 'counts', 'combined_summary']]
        outputdata = projectdata['combined_summary']

        logger.info("[setup] OutputCompiler test instance "
                    "for combined output files '{}'"
                    .format([f['path'] for f in outputs]))

        outputcompiler = postprocess.OutputCompiler(
            paths=[f['path'] for f in outputs])

        def fin():
            logger.info("[teardown] OutputCompiler mock instance")
        request.addfinalizer(fin)
        return (outputcompiler, outputs, outputdata)

    def test_init(self, compilerdata):
        # (GIVEN)
        outputcompiler, outputs, _ = compilerdata

        logger.info("test `__init__()`")

        # WHEN object is created

        # THEN should have expected paths stored as attribute
        assert(len(outputcompiler.paths) == len(outputs))

    def test_read_data(self, compilerdata):
        # (GIVEN)
        outputcompiler, outputs, _ = compilerdata

        logger.info("test `_read_data()`")

        # WHEN data from individual file paths are read into a list
        outputcompiler._read_data()

        # THEN data should be stored as list of expected length
        assert(len(outputcompiler.data) == len(outputs))

    def test_build_table(self, compilerdata):
        # (GIVEN)
        outputcompiler, outputs, _ = compilerdata

        logger.info("test `_build_table()`")

        # WHEN data are combined into a single table
        table_data = outputcompiler._build_table()

        # THEN the table should have the same number of rows (list elements)
        # as the first combined output table in the list; and 'libId' should
        # only appear once in the header row
        assert(len(table_data) == outputs[0]['len_table'])
        assert(table_data[0].count('libId') == 1)

    def test_build_combined_filename(self, compilerdata):
        # (GIVEN)
        outputcompiler, outputs, outputdata = compilerdata

        logger.info("test `_build_combined_filename()`")

        # WHEN path to outputs is parsed to build combined CSV file name
        combined_filename = outputcompiler._build_combined_filename()

        # THEN combined filename should be correctly formatted
        assert(combined_filename
               == os.path.basename(outputdata['path']))

    def test_write_table(self, compilerdata):
        # (GIVEN)
        outputcompiler, outputs, outputdata = compilerdata

        logger.info("test `write_table()`")

        # AND combined file does not already exist
        expected_path = outputdata['path']
        try:
            os.remove(expected_path)
        except OSError:
            pass

        # WHEN data is read, combined, and written to file
        outputcompiler.write_table()

        # THEN file should exist at expected path
        assert(os.path.exists(expected_path))


class TestOutputCleaner:
    @pytest.fixture(scope='function')
    def output_folder(self, tmpdir):
        return tmpdir.mkdir('processed')

    def test_get_output_types(self, output_folder):
        path = output_folder
        path.mkdir('metrics')
        path.mkdir('counts')
        # assert(str(path) == "foo")
        outputcleaner = postprocess.OutputCleaner(
            path=str(path))
        assert(set(outputcleaner._get_output_types())
               == set(['metrics', 'counts']))

    def test_get_output_paths(self, output_folder):
        path = output_folder
        path.mkdir('QC').mkdir('sample1').ensure('file1.zip')

        outputcleaner = postprocess.OutputCleaner(
            path=str(path))
        assert(outputcleaner._get_output_paths('QC')
               == [str(path.join('QC').join('sample1').join('file1.zip'))])

    def test_unzip_output(self, output_folder):
        path = output_folder
        zipdir = path.mkdir('zipfolder')
        zipdir.ensure('file1')
        zipoutput = shutil.make_archive(str(zipdir), 'zip',
                                        str(zipdir))
        shutil.rmtree(str(zipdir))

        outputcleaner = postprocess.OutputCleaner(
            path=str(path))
        paths = outputcleaner._unzip_output(zipoutput)

        assert('file1' in str(path.listdir()))
        assert(paths[0] == str(path.join('file1')))

    def test_unnest_output_file(self, output_folder):
        path = output_folder
        subdir = path.mkdir('subfolder')
        nestedoutput = subdir.ensure('file1')

        outputcleaner = postprocess.OutputCleaner(
            path=str(path))
        outputcleaner._unnest_output(str(nestedoutput))

        assert('subfolder_file1' in str(path.listdir()))

    def test_unnest_output_zip(self, output_folder):
        path = output_folder
        subdir = path.mkdir('subfolder')
        zipdir = subdir.mkdir('zipfolder')
        nestedoutput = zipdir.ensure('file1')
        zipoutput = shutil.make_archive(str(zipdir), 'zip',
                                        str(zipdir))
        shutil.rmtree(str(zipdir))

        outputcleaner = postprocess.OutputCleaner(
            path=str(path))
        outputcleaner._unnest_output(str(zipoutput))

        assert('subfolder_file1' in str(path.listdir()))

    def test_recode_output(self, output_folder):
        path = output_folder
        qcfile = path.ensure('libID_fcID_fastqc_data.txt')

        outputcleaner = postprocess.OutputCleaner(
            path=str(path))
        newpath = outputcleaner._recode_output(str(qcfile), 'QC')

        assert(os.path.basename(newpath) == 'libID_fcID_fastqc_qc.txt')
        assert('libID_fcID_fastqc_qc.txt' in str(path.listdir()))

    def test_clean_outputs(self, output_folder):
        path = output_folder
        outdir = path.mkdir('QC')

        lib1dir = outdir.mkdir('lib1_fcID')
        zip1dir = lib1dir.mkdir('qc1')
        qc1file = zip1dir.ensure('fastqc_data.txt')
        zip1out = shutil.make_archive(str(zip1dir), 'zip', str(zip1dir))
        shutil.rmtree(str(zip1dir))

        lib2dir = outdir.mkdir('lib2_fcID')
        zip2dir = lib2dir.mkdir('qc1')
        qc2file = zip2dir.ensure('fastqc_data.txt')
        zip2out = shutil.make_archive(str(zip2dir), 'zip', str(zip2dir))
        shutil.rmtree(str(zip2dir))

        outputcleaner = postprocess.OutputCleaner(
            path=str(path))
        outputcleaner.clean_outputs()

        assert(len(outdir.listdir()) == 4)
        assert('lib1_fcID_fastqc_qc.txt' in str(outdir.listdir()))
