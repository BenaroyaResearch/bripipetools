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


class TestOutputCleaner:
    """
    Tests methods for the `OutputCleaner` class in the
    `bripipetools.postprocess.cleanup` module, which is used to
    reorganize and rename output files from deprecated layouts.
    """

    def test_get_output_types(self, tmpdir):
        # GIVEN a path to a folder with output data
        mockfolders = ['counts', 'metrics', 'QC', 'alignments', 'logs']
        for outfolder in mockfolders:
            tmpdir.mkdir(outfolder)

        # AND a cleaner object is created for that path
        cleaner = postprocess.OutputCleaner(
            path=str(tmpdir)
        )

        # WHEN the path is checked to determine output type from a predefined
        # set of options
        testtypes = cleaner._get_output_types()

        # THEN the assigned output type should match the expected result
        assert (set(testtypes) == set(mockfolders))

    @pytest.mark.parametrize(
        'test_input', ['counts', 'metrics', 'QC', 'alignments', 'logs']
    )
    def test_get_output_paths(self, tmpdir, test_input):
        # GIVEN a path to a folder with output data, and a subfolder
        # corresponding to a particular output type contains one or
        # more files
        mockpath = tmpdir.mkdir(test_input)
        mockpaths = []
        for i in range(2):
            mockfile = mockpath.ensure('outfile{}'.format(i))
            mockpaths.append(str(mockfile))

        # AND a cleaner object is created for that path
        cleaner = postprocess.OutputCleaner(
            path=str(tmpdir)
        )

        # WHEN full paths are collected for all output files
        testpaths = cleaner._get_output_paths(test_input)

        # THEN list of paths should match expected results
        assert (testpaths == mockpaths)

    def test_unzip_output(self, tmpdir):
        # GIVEN a path to a folder with output data, and a subfolder
        # corresponding to a particular output type
        mockpath = tmpdir.mkdir('metrics')

        # AND the folder contains a zipped archive with one or more
        # output files
        mockzipdir = mockpath.mkdir('zipfolder')
        mockzipdir.ensure('outfile1')
        mockzippath = shutil.make_archive(str(mockzipdir), 'zip',
                                          str(mockzipdir))
        shutil.rmtree(str(mockzipdir))

        # AND a cleaner object is created for the path
        outputcleaner = postprocess.OutputCleaner(
            path=str(tmpdir)
        )

        # WHEN the zipped archive is uncompressed
        testpaths = outputcleaner._unzip_output(mockzippath)

        # THEN the individual output files previously stored in the
        # zipped archive should now exist in the output type subfolder
        assert ('outfile1' in str(mockpath.listdir()))
        assert (testpaths[0] == str(mockpath.join('outfile1')))

    def test_unnest_output_file(self, tmpdir):
        # GIVEN a path to a folder with output data, and a subfolder
        # corresponding to a particular output type
        mockpath = tmpdir.mkdir('metrics')

        # AND the folder contains another subfolder with one or more
        # output files
        mocksubdir = mockpath.mkdir('subfolder')
        mocknestpath = mocksubdir.ensure('outfile1')

        # AND a cleaner object is created for the path
        outputcleaner = postprocess.OutputCleaner(
            path=str(tmpdir)
        )

        # WHEN output files in the subfolder are unnested
        outputcleaner._unnest_output(str(mocknestpath))

        # THEN the files should exist directly under the output type
        # folder and be labeled in the form '<subfolder>_<filename>'
        assert ('subfolder_outfile1' in str(mockpath.listdir()))

    def test_unnest_output_zip(self, tmpdir):
        # GIVEN a path to a folder with output data, and a subfolder
        # corresponding to a particular output type
        mockpath = tmpdir.mkdir('metrics')

        # AND the folder contains another subfolder with one or more
        # zipped archives than in turn contain one or more output files
        mocksubdir = mockpath.mkdir('subfolder')
        mockzipdir = mocksubdir.mkdir('zipfolder')
        mockzipdir.ensure('outfile1')
        mockzippath = shutil.make_archive(str(mockzipdir), 'zip',
                                          str(mockzipdir))
        shutil.rmtree(str(mockzipdir))

        # AND a cleaner object is created for the path
        outputcleaner = postprocess.OutputCleaner(
            path=str(tmpdir)
        )

        # WHEN zipped output files in the subfolder are unnested
        outputcleaner._unnest_output(str(mockzippath))

        # THEN the zipped archives should first be flattened such that
        # individual output files exist directly under the subfolder,
        # and these files should then be unnested and exist directly
        # under the output type folder (labeled as '<subfolder>_<filename>'
        assert('subfolder_outfile1' in str(mockpath.listdir()))

    def test_recode_output(self, tmpdir):
        # GIVEN a path to a folder with output data, and a subfolder
        # corresponding to a particular output type, which contains
        # an output file
        mockpath = tmpdir.mkdir('QC')
        mockqcpath = mockpath.ensure('libID_fcID_fastqc_data.txt')

        # AND a cleaner object is created for the path
        outputcleaner = postprocess.OutputCleaner(
            path=str(tmpdir))

        # WHEN the output file is renamed according to some predefined rule
        testpath = outputcleaner._recode_output(str(mockqcpath), 'QC')

        # THEN the new filename should match the expected result
        assert (os.path.basename(testpath) == 'libID_fcID_fastqc_qc.txt')
        assert ('libID_fcID_fastqc_qc.txt' in str(mockpath.listdir()))

    def test_clean_outputs(self, tmpdir):
        # GIVEN a path to a folder with output data, and a subfolder
        # corresponding to a particular output type
        mockpath = tmpdir.mkdir('QC')

        # AND the output type folder contains output files for one or more
        # samples with various levels of compression and nesting
        mockoutputdata = {
            1: 'lib1111_C00000XX',
            2: 'lib2222_C00000XX'
        }
        for i in range(2):
            mocksampledir = mockpath.mkdir(mockoutputdata[i+1])
            mockzipdir = mocksampledir.mkdir('qc{}'.format(i))
            mockzipdir.ensure('fastqc_data.txt')
            shutil.make_archive(str(mockzipdir), 'zip',
                                str(mockzipdir))
            shutil.rmtree(str(mockzipdir))

        # AND a cleaner object is created for the path
        outputcleaner = postprocess.OutputCleaner(
            path=str(tmpdir))

        # WHEN output files for the folder are "cleaned" to resolve unwanted
        # compression, nesting, or deprecated filenames
        outputcleaner.clean_outputs()

        # THEN the updated output organization should match expected results
        assert (len(mockpath.listdir()) == 4)
        assert ('lib1111_C00000XX_fastqc_qc.txt'
                in str(mockpath.listdir()))
