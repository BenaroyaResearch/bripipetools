import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
import re
import shutil

import pytest
import pandas as pd

from bripipetools import postprocess
from bripipetools import io


class TestOutputStitcher:

    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            ('counts', 'counts'),
            ('metrics', 'metrics'),
            ('QC', 'qc'),
            ('validation', 'validation'),
        ]
    )
    def test_sniff_output_type(self, tmpdir, test_input, expected_result):
        mockpath = tmpdir.join(test_input)

        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        assert (stitcher._sniff_output_type() == expected_result)

    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            (('metrics', 'htseq'), getattr(io, 'HtseqMetricsFile')),
            (('metrics', 'picard_rnaseq'), getattr(io, 'PicardMetricsFile')),
            (('metrics', 'picard_markdups'), getattr(io, 'PicardMetricsFile')),
            (('metrics', 'picard_align'), getattr(io, 'PicardMetricsFile')),
            (('metrics', 'tophat_stats'), getattr(io, 'TophatStatsFile')),
            (('qc', 'fastqc'), getattr(io, 'FastQCFile')),
            (('counts', 'htseq'), getattr(io, 'HtseqCountsFile')),
            (('validation', 'sexcheck'), getattr(io, 'SexcheckFile'))
        ]
    )
    def test_get_parser(self, tmpdir, test_input, expected_result):
        mockpath = tmpdir.join('')

        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        mocktype, mocksource = test_input

        # WHEN the parser is retrieved given output type and source
        testparser = stitcher._get_parser(mocktype, mocksource)

        # THEN the expected number of outputs should be found
        assert (testparser == expected_result)

    def test_read_data(self, tmpdir):
        mockpath = tmpdir.join('metrics')
        mockfiledata = [
            {'mockfilename': 'lib1111_C00000XX_htseq_metrics.txt',
             'mockcontents': ['__field_1\tsource1_value1\n',
                              '__field_2\tsource1_value2\n']},
            {'mockfilename': 'lib1111_C00000XX_tophat_stats_metrics.txt',
             'mockcontents': ['source2_value1\ttotal reads in fastq file\n'
                              'source2_value2\treads aligned in sam file\n']},
            {'mockfilename': 'lib2222_C00000XX_htseq_metrics.txt',
             'mockcontents': ['__field_1\tsource1_value1\n',
                              '__field_2\tsource1_value2\n']},
            {'mockfilename': 'lib2222_C00000XX_tophat_stats_metrics.txt',
             'mockcontents': ['source2_value1\ttotal reads in fastq file\n'
                              'source2_value2\treads aligned in sam file\n']},
        ]
        for m in mockfiledata:
            mockfile = mockpath.ensure(m['mockfilename'])
            mockfile.write(''.join(m['mockcontents']))

        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        stitcher._read_data()

        assert (stitcher.data['metrics'] ==
                {
                    'lib1111_C00000XX': [
                        {'htseq': {'field_1': 'source1_value1',
                                   'field_2': 'source1_value2'}},
                        {'tophat_stats': {'fastq_total_reads':
                                              'source2_value1',
                                          'reads_aligned_sam':
                                              'source2_value2'}},
                    ],
                    'lib2222_C00000XX': [
                        {'htseq': {'field_1': 'source1_value1',
                                   'field_2': 'source1_value2'}},
                        {'tophat_stats': {'fastq_total_reads':
                                              'source2_value1',
                                          'reads_aligned_sam':
                                              'source2_value2'}},
                    ],
                })

    def test_build_table_for_noncount_data(self, tmpdir):
        mockpath = tmpdir.join('metrics')

        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        mockdata = {
            'lib1111_C00000XX': [
                {'htseq': {'field_1': 'source1_value1',
                           'field_2': 'source1_value2'}},
                {'tophat_stats': {'fastq_total_reads':
                                      'source2_value1',
                                  'reads_aligned_sam':
                                      'source2_value2'}},
            ],
            'lib2222_C00000XX': [
                {'htseq': {'field_1': 'source1_value1',
                           'field_2': 'source1_value2'}},
                {'tophat_stats': {'fastq_total_reads':
                                      'source2_value1',
                                  'reads_aligned_sam':
                                      'source2_value2'}},
            ],
        }

        stitcher.data = {'metrics': mockdata}

        testdata = stitcher._build_table()

        assert (testdata
                == [
                    ['libId', 'fastq_total_reads',
                     'field_1', 'field_2', 'reads_aligned_sam'],
                    ['lib2222_C00000XX', 'source2_value1',
                     'source1_value1', 'source1_value2', 'source2_value2'],
                    ['lib1111_C00000XX', 'source2_value1',
                     'source1_value1', 'source1_value2', 'source2_value2'],
                ])

    def test_build_table_for_count_data(self, tmpdir):
        mockpath = tmpdir.join('counts')

        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        mockdata = {
            'lib1111_C00000XX': [
                {'htseq': pd.DataFrame([['field1', 0], ['field2', 1]],
                                       columns=['geneName', 'count'])}
                ],
            'lib2222_C00000XX': [
                {'htseq': pd.DataFrame([['field1', 1], ['field2', 0]],
                                       columns=['geneName', 'count'])}
                ]
        }

        stitcher.data = {'counts': mockdata}

        testdata = stitcher._build_table()
        mockdf = pd.DataFrame(
            [['field1', 0, 1], ['field2', 1, 0]],
            columns=['geneName', 'lib1111_C00000XX', 'lib2222_C00000XX']
        )

        assert all((testdata[k] == mockdf[k]).all() for k in mockdf.keys())

    def test_build_combined_filename(self, tmpdir):
        mockrun = '161231_INSTID_0001_AC00000XX'
        mockproject = 'Project_P00-00Processed_161231'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mockrun)
                    .mkdir(mockproject)
                    .mkdir('metrics'))

        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        testfilename = stitcher._build_combined_filename()

        assert (testfilename == 'P00-00_C00000XX_161231_combined_metrics.csv')

    def test_write_table_for_noncount_data(self, tmpdir):
        mockrun = '161231_INSTID_0001_AC00000XX'
        mockproject = 'Project_P00-00Processed_161231'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mockrun)
                    .mkdir(mockproject)
                    .mkdir('metrics'))
        mockfiledata = [
            {'mockfilename': 'lib1111_C00000XX_htseq_metrics.txt',
             'mockcontents': ['__field_1\tsource1_value1\n',
                              '__field_2\tsource1_value2\n']},
            {'mockfilename': 'lib1111_C00000XX_tophat_stats_metrics.txt',
             'mockcontents': ['source2_value1\ttotal reads in fastq file\n'
                              'source2_value2\treads aligned in sam file\n']},
            {'mockfilename': 'lib2222_C00000XX_htseq_metrics.txt',
             'mockcontents': ['__field_1\tsource1_value1\n',
                              '__field_2\tsource1_value2\n']},
            {'mockfilename': 'lib2222_C00000XX_tophat_stats_metrics.txt',
             'mockcontents': ['source2_value1\ttotal reads in fastq file\n'
                              'source2_value2\treads aligned in sam file\n']},
        ]
        for m in mockfiledata:
            mockfile = mockpath.ensure(m['mockfilename'])
            mockfile.write(''.join(m['mockcontents']))

        mocktablefile = mockpath.join(
            'P00-00_C00000XX_161231_combined_metrics.csv'
        )
        mockcontents = [
            ','.join(['libId', 'fastq_total_reads',
                      'field_1', 'field_2', 'reads_aligned_sam\n']),
            ','.join(['lib2222_C00000XX', 'source2_value1',
                      'source1_value1', 'source1_value2', 'source2_value2\n']),
            ','.join(['lib1111_C00000XX', 'source2_value1',
                      'source1_value1', 'source1_value2', 'source2_value2\n']),
        ]
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        testtablefile = stitcher.write_table()
        assert (testtablefile == mocktablefile)

        with open(testtablefile) as f:
            assert (f.readlines() == mockcontents)

    def test_write_table_for_count_data(self, tmpdir):
        mockrun = '161231_INSTID_0001_AC00000XX'
        mockproject = 'Project_P00-00Processed_161231'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mockrun)
                    .mkdir(mockproject)
                    .mkdir('counts'))
        mockfiledata = [
            {'mockfilename': 'lib1111_C00000XX_htseq_counts.txt',
             'mockcontents': ['field1\t0\n',
                              'field2\t1\n']},
            {'mockfilename': 'lib2222_C00000XX_htseq_counts.txt',
             'mockcontents': ['field1\t1\n',
                              'field2\t0\n']},
        ]
        for m in mockfiledata:
            mockfile = mockpath.ensure(m['mockfilename'])
            mockfile.write(''.join(m['mockcontents']))

        mocktablefile = mockpath.join(
            'P00-00_C00000XX_161231_combined_counts.csv'
        )
        mockcontents = [
            ','.join(['geneName', 'lib2222_C00000XX', 'lib1111_C00000XX\n']),
            ','.join(['field1', '1', '0\n']),
            ','.join(['field2', '0', '1\n']),
        ]
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        testtablefile = stitcher.write_table()
        assert (testtablefile == mocktablefile)

        with open(testtablefile) as f:
            assert (f.readlines() == mockcontents)


# class TestOutputCompiler:
#     @pytest.fixture(
#         scope='class',
#         params=[{'runnum': r, 'projectnum': p}
#                 for r in range(1)
#                 for p in range(3)])
#     def compilerdata(self, request, mock_genomics_server):
#         # GIVEN a OutputCompiler with list of mock 'genomics' server path to
#         # combined output files
#         runs = mock_genomics_server['root']['genomics']['illumina']['runs']
#         rundata = runs[request.param['runnum']]
#         projects = rundata['processed']['projects']
#         projectdata = projects[request.param['projectnum']]
#         outputs = [projectdata[out_type]['combined']
#                    for out_type in projectdata
#                    if out_type not in ['path', 'counts', 'combined_summary']]
#         outputdata = projectdata['combined_summary']
#
#         logger.info("[setup] OutputCompiler test instance "
#                     "for combined output files '{}'"
#                     .format([f['path'] for f in outputs]))
#
#         outputcompiler = postprocess.OutputCompiler(
#             paths=[f['path'] for f in outputs])
#
#         def fin():
#             logger.info("[teardown] OutputCompiler mock instance")
#         request.addfinalizer(fin)
#         return (outputcompiler, outputs, outputdata)
#
#     def test_init(self, compilerdata):
#         # (GIVEN)
#         outputcompiler, outputs, _ = compilerdata
#
#         logger.info("test `__init__()`")
#
#         # WHEN object is created
#
#         # THEN should have expected paths stored as attribute
#         assert(len(outputcompiler.paths) == len(outputs))
#
#     def test_read_data(self, compilerdata):
#         # (GIVEN)
#         outputcompiler, outputs, _ = compilerdata
#
#         logger.info("test `_read_data()`")
#
#         # WHEN data from individual file paths are read into a list
#         outputcompiler._read_data()
#
#         # THEN data should be stored as list of expected length
#         assert(len(outputcompiler.data) == len(outputs))
#
#     def test_build_table(self, compilerdata):
#         # (GIVEN)
#         outputcompiler, outputs, _ = compilerdata
#
#         logger.info("test `_build_table()`")
#
#         # WHEN data are combined into a single table
#         table_data = outputcompiler._build_table()
#
#         # THEN the table should have the same number of rows (list elements)
#         # as the first combined output table in the list; and 'libId' should
#         # only appear once in the header row
#         assert(len(table_data) == outputs[0]['len_table'])
#         assert(table_data[0].count('libId') == 1)
#
#     def test_build_combined_filename(self, compilerdata):
#         # (GIVEN)
#         outputcompiler, outputs, outputdata = compilerdata
#
#         logger.info("test `_build_combined_filename()`")
#
#         # WHEN path to outputs is parsed to build combined CSV file name
#         combined_filename = outputcompiler._build_combined_filename()
#
#         # THEN combined filename should be correctly formatted
#         assert(combined_filename
#                == os.path.basename(outputdata['path']))
#
#     def test_write_table(self, compilerdata):
#         # (GIVEN)
#         outputcompiler, outputs, outputdata = compilerdata
#
#         logger.info("test `write_table()`")
#
#         # AND combined file does not already exist
#         expected_path = outputdata['path']
#         try:
#             os.remove(expected_path)
#         except OSError:
#             pass
#
#         # WHEN data is read, combined, and written to file
#         outputcompiler.write_table()
#
#         # THEN file should exist at expected path
#         assert(os.path.exists(expected_path))
#
#
# class TestOutputCleaner:
#     @pytest.fixture(scope='function')
#     def output_folder(self, tmpdir):
#         return tmpdir.mkdir('processed')
#
#     def test_get_output_types(self, output_folder):
#         path = output_folder
#         path.mkdir('metrics')
#         path.mkdir('counts')
#         # assert(str(path) == "foo")
#         outputcleaner = postprocess.OutputCleaner(
#             path=str(path))
#         assert(set(outputcleaner._get_output_types())
#                == set(['metrics', 'counts']))
#
#     def test_get_output_paths(self, output_folder):
#         path = output_folder
#         path.mkdir('QC').mkdir('sample1').ensure('file1.zip')
#
#         outputcleaner = postprocess.OutputCleaner(
#             path=str(path))
#         assert(outputcleaner._get_output_paths('QC')
#                == [str(path.join('QC').join('sample1').join('file1.zip'))])
#
#     def test_unzip_output(self, output_folder):
#         path = output_folder
#         zipdir = path.mkdir('zipfolder')
#         zipdir.ensure('file1')
#         zipoutput = shutil.make_archive(str(zipdir), 'zip',
#                                         str(zipdir))
#         shutil.rmtree(str(zipdir))
#
#         outputcleaner = postprocess.OutputCleaner(
#             path=str(path))
#         paths = outputcleaner._unzip_output(zipoutput)
#
#         assert('file1' in str(path.listdir()))
#         assert(paths[0] == str(path.join('file1')))
#
#     def test_unnest_output_file(self, output_folder):
#         path = output_folder
#         subdir = path.mkdir('subfolder')
#         nestedoutput = subdir.ensure('file1')
#
#         outputcleaner = postprocess.OutputCleaner(
#             path=str(path))
#         outputcleaner._unnest_output(str(nestedoutput))
#
#         assert('subfolder_file1' in str(path.listdir()))
#
#     def test_unnest_output_zip(self, output_folder):
#         path = output_folder
#         subdir = path.mkdir('subfolder')
#         zipdir = subdir.mkdir('zipfolder')
#         nestedoutput = zipdir.ensure('file1')
#         zipoutput = shutil.make_archive(str(zipdir), 'zip',
#                                         str(zipdir))
#         shutil.rmtree(str(zipdir))
#
#         outputcleaner = postprocess.OutputCleaner(
#             path=str(path))
#         outputcleaner._unnest_output(str(zipoutput))
#
#         assert('subfolder_file1' in str(path.listdir()))
#
#     def test_recode_output(self, output_folder):
#         path = output_folder
#         qcfile = path.ensure('libID_fcID_fastqc_data.txt')
#
#         outputcleaner = postprocess.OutputCleaner(
#             path=str(path))
#         newpath = outputcleaner._recode_output(str(qcfile), 'QC')
#
#         assert(os.path.basename(newpath) == 'libID_fcID_fastqc_qc.txt')
#         assert('libID_fcID_fastqc_qc.txt' in str(path.listdir()))
#
#     def test_clean_outputs(self, output_folder):
#         path = output_folder
#         outdir = path.mkdir('QC')
#
#         lib1dir = outdir.mkdir('lib1_fcID')
#         zip1dir = lib1dir.mkdir('qc1')
#         qc1file = zip1dir.ensure('fastqc_data.txt')
#         zip1out = shutil.make_archive(str(zip1dir), 'zip', str(zip1dir))
#         shutil.rmtree(str(zip1dir))
#
#         lib2dir = outdir.mkdir('lib2_fcID')
#         zip2dir = lib2dir.mkdir('qc1')
#         qc2file = zip2dir.ensure('fastqc_data.txt')
#         zip2out = shutil.make_archive(str(zip2dir), 'zip', str(zip2dir))
#         shutil.rmtree(str(zip2dir))
#
#         outputcleaner = postprocess.OutputCleaner(
#             path=str(path))
#         outputcleaner.clean_outputs()
#
#         assert(len(outdir.listdir()) == 4)
#         assert('lib1_fcID_fastqc_qc.txt' in str(outdir.listdir()))
