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
    """
    Tests methods for the `OutputSticher` class in the
    `bripipetools.postprocess.stitching` module, which is used
    to combine output data across all sources and samples into
    a single table for a selected output type.
    """
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
        # GIVEN a path to a folder with output data
        mockpath = tmpdir.join(test_input)

        # AND a sticher object is created for that path
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        # WHEN the path is checked to determine output type from a predefined
        # set of options

        # THEN the assigned output type should match the expected result
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
        # GIVEN an arbitrary path
        mockpath = tmpdir.join('')

        # AND a stitcher object is created for that path
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        # WHEN the io parser class is retrieved for a particular output
        # type and source
        mocktype, mocksource = test_input
        testparser = stitcher._get_parser(mocktype, mocksource)

        # THEN the io class should match the expected result
        assert (testparser == expected_result)

    def test_read_data(self, tmpdir):
        # GIVEN a path to a folder with output data of type 'metrics'
        # (output type should not matter here, assuming that individual
        # io classes/modules have been tested)
        mockpath = tmpdir.join('metrics')

        # AND the folder contains outputs from multiple sources and
        # for multiple samples
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

        # AND a stitcher object is created for the folder path
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        # WHEN all file contents in the folder are read and stored as a dict
        # in the object's 'data' attribute (in the field corresponding to
        # output type)
        stitcher._read_data()

        # THEN the data stored in the dict should be properly parsed into
        # key-value pairs and grouped by output source for each sample
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
        # GIVEN a path to a folder with output data of type 'metrics'
        mockpath = tmpdir.join('metrics')

        # AND a stitcher object is created for the folder path
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        # AND parsed data from output files are stored as a nested dict
        # in the object's 'data' attribute (in the field corresponding to
        # output type)
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

        # WHEN all key-value pairs for output data are combined into a
        # single list corresponding to rows of a table for all samples
        testdata = stitcher._build_table()

        # THEN the list of lists (where each sublist is a table row)
        # should match the expected result, with sample IDs in the first
        # column and output keys in remaining columns
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
        # GIVEN a path to a folder with output data of type 'counts'
        # (methods for combining count data require Pandas dataframe
        # operations, and thus need to be treated differently than
        # other output types)
        mockpath = tmpdir.join('counts')

        # AND a stitcher object is created for the folder path
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        # AND parsed data from output files are stored as a nested dict
        # in the object's 'data' attribute (in the field corresponding to
        # output type)
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

        # WHEN all count data frames merged into a single data frame
        # for all samples, with gene IDs stored in the first column and
        # counts for individual samples stored in remaining columns
        testdata = stitcher._build_table()

        # THEN the combined data frame should match the expected result
        mockdf = pd.DataFrame(
            [['field1', 0, 1], ['field2', 1, 0]],
            columns=['geneName', 'lib1111_C00000XX', 'lib2222_C00000XX']
        )
        assert all((testdata[k] == mockdf[k]).all() for k in mockdf.keys())

    def test_build_combined_filename(self, tmpdir):
        # GIVEN a path to a folder with output data of type 'metrics',
        # which exists in a processed project folder at the path
        # '<root>/genomics/Illumina/<run-id>/<project-folder>'
        mockrun = '161231_INSTID_0001_AC00000XX'
        mockproject = 'Project_P00-00Processed_161231'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mockrun)
                    .mkdir(mockproject)
                    .mkdir('metrics'))

        # AND a stitcher object is created for the folder path
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        # WHEN the combined filename is constructed for output data
        # of the current type
        testfilename = stitcher._build_combined_filename()

        # THEN the filename should be in the form
        # '<project-id>_<flowcell-id>_<process-date>_combined_<out-type>.csv'
        assert (testfilename == 'P00-00_C00000XX_161231_combined_metrics.csv')

    def test_write_table_for_noncount_data(self, tmpdir):
        # GIVEN a path to a folder with output data of type 'metrics',
        # which exists in a processed project folder at the path
        # '<root>/genomics/Illumina/<run-id>/<project-folder>'
        mockrun = '161231_INSTID_0001_AC00000XX'
        mockproject = 'Project_P00-00Processed_161231'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mockrun)
                    .mkdir(mockproject)
                    .mkdir('metrics'))

        # AND the folder contains outputs from multiple sources and
        # for multiple samples
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

        # AND a stitcher object is created for the folder path
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        # WHEN combined data across all samples is written as a table
        # in a new file
        testtablefile = stitcher.write_table()

        # THEN the combined table should exist at the expected path and
        # contain the expected contents
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
        assert (testtablefile == mocktablefile)
        with open(testtablefile) as f:
            assert (f.readlines() == mockcontents)

    def test_write_table_for_count_data(self, tmpdir):
        # GIVEN a path to a folder with output data of type 'counts',
        # which exists in a processed project folder at the path
        # '<root>/genomics/Illumina/<run-id>/<project-folder>'
        mockrun = '161231_INSTID_0001_AC00000XX'
        mockproject = 'Project_P00-00Processed_161231'
        mockpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                    .mkdir(mockrun)
                    .mkdir(mockproject)
                    .mkdir('counts'))

        # AND the folder contains outputs from multiple sources and
        # for multiple samples
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

        # AND a stitcher object is created for the folder path
        stitcher = postprocess.OutputStitcher(
            path=str(mockpath)
        )

        # WHEN combined data across all samples is written as a table
        # in a new file
        testtablefile = stitcher.write_table()

        # THEN the combined table should exist at the expected path and
        # contain the expected contents
        mocktablefile = mockpath.join(
            'P00-00_C00000XX_161231_combined_counts.csv'
        )
        mockcontents = [
            ','.join(['geneName', 'lib2222_C00000XX', 'lib1111_C00000XX\n']),
            ','.join(['field1', '1', '0\n']),
            ','.join(['field2', '0', '1\n']),
        ]
        assert (testtablefile == mocktablefile)
        with open(testtablefile) as f:
            assert (f.readlines() == mockcontents)


class TestOutputCompiler:
    """
    Tests methods for the `OutputCompiler` class in the
    `bripipetools.postprocess.compiling` module, which is used
    to merge combined output data from multiple summary output
    types (i.e., summary indicates one value per sample).
    """
    def test_read_data(self, tmpdir):
        # GIVEN a path to a processed project folder at the path
        # '<root>/genomics/Illumina/<run-id>/<project-folder>'
        mockrun = '161231_INSTID_0001_AC00000XX'
        mockproject = 'Project_P00-00Processed_161231'

        # AND one or more folders with output data of 'summary' types
        # (e.g., metrics, QC, validation), each of which includes a
        # 'combined' table file for its respective type
        mockpaths = []
        mockprojectpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                           .mkdir(mockrun)
                           .mkdir(mockproject))
        for i in range(2):
            mockpath = mockprojectpath.mkdir('type{}'.format(i))
            mocktablefile = mockpath.join(
                'P00-00_C00000XX_161231_combined_type{}.csv'.format(i)
            )
            mockpaths.append(str(mocktablefile))
            mockcontents = [
                'libId,type{}_field1,type{}_field2\n',
                'sample1,type{}_sample1_value1,type{}_sample1_value2\n',
                'sample2,type{}_sample2_value1,type{}_sample2_value2\n',
            ]

            mocktablefile.write(
                ''.join([line.format(i+1, i+1) for line in mockcontents])
            )

        # AND a compiler object is created for the project folder path
        compiler = postprocess.OutputCompiler(
            paths=mockpaths
        )

        # WHEN data from the combined table for each type is read and
        # stored in the object's 'data' attribute
        compiler._read_data()

        # THEN the resulting list stored in the object's 'data' attribute
        # should include a list for each combined table, with each item
        # representing a row in a table as a list of column values
        mockdata = [
            [
                ['libId', 'type1_field1', 'type1_field2'],
                ['sample1','type1_sample1_value1', 'type1_sample1_value2'],
                ['sample2', 'type1_sample2_value1', 'type1_sample2_value2'],
            ],
            [
                ['libId', 'type2_field1', 'type2_field2'],
                ['sample1', 'type2_sample1_value1', 'type2_sample1_value2'],
                ['sample2', 'type2_sample2_value1', 'type2_sample2_value2'],
            ],
        ]
        assert (compiler.data == mockdata)

    def test_build_table(self):
        # GIVEN a compiler object, created for an arbitrary list of paths
        compiler = postprocess.OutputCompiler(
            paths=[]
        )

        # AND parsed data from combined output table files are stroed in the
        # object's 'data' attribute
        mockdata = [
            [
                ['libId', 'type1_field1', 'type1_field2'],
                ['sample1','type1_sample1_value1', 'type1_sample1_value2'],
                ['sample2', 'type1_sample2_value1', 'type1_sample2_value2'],
            ],
            [
                ['libId', 'type2_field1', 'type2_field2'],
                ['sample1', 'type2_sample1_value1', 'type2_sample1_value2'],
                ['sample2', 'type2_sample2_value1', 'type2_sample2_value2'],
            ],
        ]
        compiler.data = mockdata

        # WHEN combined data from each type are merged into a list
        # representing representing rows for an overall project summary table
        testdata = compiler._build_table()

        # THEN the merged rows should contain sample (library) IDs in the
        # first column, and all other columns from different output types
        mocktabledata = [
            ['libId', 'type1_field1', 'type1_field2',
             'type2_field1', 'type2_field2'],
            ['sample1', 'type1_sample1_value1', 'type1_sample1_value2',
             'type2_sample1_value1', 'type2_sample1_value2'],
            ['sample2', 'type1_sample2_value1', 'type1_sample2_value2',
             'type2_sample2_value1', 'type2_sample2_value2'],
        ]
        assert (testdata == mocktabledata)

    def test_build_combined_filename(self):
        # GIVEN a list one or more paths to 'combined' table files for
        # arbitrary output types
        mockpaths = [
            'P00-00_C00000XX_161231_combined_type{}.csv'.format(i)
            for i in range(2)
            ]

        # AND a compiler object is created for the paths
        compiler = postprocess.OutputCompiler(
            paths=mockpaths
        )

        # WHEN the filename is constructed for the merged table with
        # all summary output types
        testfilename = compiler._build_combined_filename()

        # THEN the filename should be in the form
        # '<project-id>_<flowcell-id>_<process-date>_combined_summary_data.csv'
        assert (testfilename
                == 'P00-00_C00000XX_161231_combined_summary-data.csv')

    def test_write_table(self, tmpdir):
        # GIVEN a path to a processed project folder at the path
        # '<root>/genomics/Illumina/<run-id>/<project-folder>'
        mockrun = '161231_INSTID_0001_AC00000XX'
        mockproject = 'Project_P00-00Processed_161231'

        # AND one or more folders with output data of 'summary' types
        # (e.g., metrics, QC, validation), each of which includes a
        # 'combined' table file for its respective type
        mockpaths = []
        mockprojectpath = (tmpdir.mkdir('genomics').mkdir('Illumina')
                           .mkdir(mockrun)
                           .mkdir(mockproject))
        for i in range(2):
            mockpath = mockprojectpath.mkdir('type{}'.format(i))
            mocktablefile = mockpath.join(
                'P00-00_C00000XX_161231_combined_type{}.csv'.format(i)
            )
            mockpaths.append(str(mocktablefile))
            mockcontents = [
                'libId,type{}_field1,type{}_field2\n',
                'sample1,type{}_sample1_value1,type{}_sample1_value2\n',
                'sample2,type{}_sample2_value1,type{}_sample2_value2\n',
            ]

            mocktablefile.write(
                ''.join([line.format(i+1, i+1) for line in mockcontents])
            )

        # AND a compiler object is created for the project folder path
        compiler = postprocess.OutputCompiler(
            paths=mockpaths
        )

        # WHEN compiled data across all summary output types is written
        # as a table in a new file, stored directly under the project folder
        testtablefile = compiler.write_table()

        # THEN the combined table should exist at the expected path and
        # contain the expected contents
        mocktablefile = mockprojectpath.join(
            'P00-00_C00000XX_161231_combined_summary-data.csv'
        )
        mockcontents = [
            ','.join(['libId', 'type1_field1', 'type1_field2',
                      'type2_field1', 'type2_field2\n']),
            ','.join(['sample1',
                      'type1_sample1_value1', 'type1_sample1_value2',
                      'type2_sample1_value1', 'type2_sample1_value2\n']),
            ','.join(['sample2',
                      'type1_sample2_value1', 'type1_sample2_value2',
                      'type2_sample2_value1', 'type2_sample2_value2\n']),
        ]
        assert (testtablefile == mocktablefile)
        with open(testtablefile) as f:
            assert (f.readlines() == mockcontents)


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
