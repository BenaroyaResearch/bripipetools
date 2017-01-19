import datetime

import pytest

from bripipetools import parsing


class TestGencore:
    """
    Tests methods in the `bripipetools.parsing.gencore` module for
    extracting identifiers and other information related to BRI
    Genomics Core samples and data from strings and paths.
    """
    @pytest.mark.parametrize(
        'mock_label, expected_result',
        [
            ('P00Processed', 'P00'),
            ('P00-00Processed', 'P00-00'),
            ('P00-00-0000', 'P00-00'),
        ]
    )
    def test_get_project_label(self, mock_label, expected_result):
        # GIVEN any state

        # WHEN some string is searched for a Genomics Core project label
        # (i.e., 'P<project ID>-<subproject ID>'), where the subproject
        # ID may or may not be included

        # THEN the output string should match the expected result
        assert (parsing.get_project_label(mock_label) == expected_result)

    def test_parse_project_label(self):
        # GIVEN any state

        # WHEN a project label of format 'P<number>-<number>' is parsed
        # into component items
        test_items = parsing.parse_project_label('P1-2')

        # THEN the dictionary should have the first number with key 'project_id'
        # and the second number with key 'subproject_id'
        assert (test_items['project_id'] == 1)
        assert (test_items['subproject_id'] == 2)

    @pytest.mark.parametrize(
        'mock_string, expected_result',
        [
            ('lib1234-1234', 'lib1234'),
            ('Sample_lib1234', 'lib1234'),
            ('Sample1234', ''),
        ]
    )
    def test_get_library_id(self, mock_string, expected_result):
        # GIVEN any state

        # WHEN some string is searched for a Genomics Core library ID
        # (i.e., 'lib0000')

        # THEN the output string should match the expected result
        # (i.e., the matched library ID or an empty string, if no
        # match found)
        assert (parsing.get_library_id(mock_string) == expected_result)

    @pytest.mark.parametrize(
        'mock_string, expected_result',
        [
            ('lib1234-1234', 'lib1234'),
            ('Sample_lib1234', 'lib1234'),
            ('Sample1234', ''),
            ('Sample_1234', 'Sample_1234')
        ]
    )
    def test_get_sample_id(self, mock_string, expected_result):
        # GIVEN any state

        # WHEN some string is searched for a sample identifier
        # for a sequenced library (nominally 'lib0000', but could
        # alternatively be 'Sample_lib0000', or 'Sample_name1' in
        # the case of custom jobs for external data)

        # THEN the output string should match the expected result
        # (i.e., the matched sample ID or an empty string, if no
        # match found)
        assert (parsing.get_sample_id(mock_string) == expected_result)

    @pytest.mark.parametrize(
        'mock_path, expected_result',
        [
            (
                    '/mnt/genomics/Illumina/161231_INSTID_0001_AC00000XX',
                    {'genomics_root': '/mnt/',
                     'run_id': '161231_INSTID_0001_AC00000XX'}
            ),
            (
                    'genomics/Illumina/161231_INSTID_0001_AC00000XX',
                    {'genomics_root': '',
                     'run_id': '161231_INSTID_0001_AC00000XX'}
            ),
            (
                    '/mnt/genomics/Illumina/161231_INSTID_0001_AC00000XX/',
                    {'genomics_root': '/mnt/',
                     'run_id': '161231_INSTID_0001_AC00000XX'}
            ),
        ]
    )
    def test_parse_flowcell_path(self, mock_path, expected_result):
        # GIVEN any state

        # WHEN a flowcell path of format...
        # '<genomics_root>/genomics/Illumina/<run_id>' is parsed
        # into component items (note: function assumes, but does not
        # test that path ends in a folder with valid run ID)
        test_items = parsing.parse_flowcell_path(mock_path)

        # THEN the dictionary include the expected 'genomics_root' and
        # flowcell 'run_id'
        assert (test_items == expected_result)

    @pytest.mark.parametrize(
        'mock_path, expected_result',
        [
            (
                    ('/mnt/genomics/Illumina/161231_INSTID_0001_AC00000XX'
                     'globus_batch_submission/workflow-batch-filename.txt'),
                    {'genomics_root': '/mnt/',
                     'workflowbatch_filename': 'workflow-batch-filename.txt'}
            ),
            (
                    ('genomics/Illumina/161231_INSTID_0001_AC00000XX'
                     'globus_batch_submission/workflow-batch-filename.txt'),
                    {'genomics_root': '',
                     'workflowbatch_filename': 'workflow-batch-filename.txt'}
            ),
        ]
    )
    def test_parse_batch_file_path(self, mock_path, expected_result):
        # GIVEN any state

        # WHEN a workflow batch file path of format...
        # '<genomics_root>/genomics/Illumina/<run_id>/...
        #  globus_batch_submission/<workflowbatch_filename>' is parsed
        # into component items
        test_items = parsing.parse_batch_file_path(mock_path)

        # THEN the dictionary include the expected 'genomics_root' and
        # 'workflowbatch_filename'
        assert (test_items == expected_result)


class TestIllumina:
    """
    Tests methods in the `bripipetools.parsing.illumina` module for
    extracting identifiers and other information related to Illumina
    sequencing technology from strings and paths.
    """
    def test_get_flowcell_id(self):
        # GIVEN any state

        # WHEN some string is searched for an Illumina flowcell ID
        # (i.e., a string of 9 alphanumeric characters - typically starting
        # with the letter 'C' for normal runs and 'H' for rapid runs and
        # ending in 'XX' or 'XY')

        # THEN the output string should match the expected result
        assert (parsing.get_flowcell_id('150615_D00565_0087_AC6VG0ANXX')
                == 'C6VG0ANXX')

    def test_parse_flowcell_run_id_standard(self):
        # GIVEN any state

        # WHEN a flowcell run ID is parsed into its component items
        mock_runid = '150615_D00565_0087_AC6VG0ANXX'
        test_items = parsing.parse_flowcell_run_id(mock_runid)

        # THEN the components should be correctly parsed and assigned to
        # appropriate field in the output dictionary
        assert (test_items['date'] == '2015-06-15')
        assert (test_items['instrument_id'] == 'D00565')
        assert (test_items['run_number'] == 87)
        assert (test_items['flowcell_id'] == 'C6VG0ANXX')
        assert (test_items['flowcell_position'] == 'A')

    def test_parse_flowcell_run_id_invalid_date(self):
        # GIVEN any state

        # WHEN a flowcell run ID is parsed into its component items,
        # but the run ID does not contain a valid date
        mock_runid = 'NOTDATE_D00565_0087_AC6VG0ANXX'
        test_items = parsing.parse_flowcell_run_id(mock_runid)

        # THEN the components should be correctly parsed and assigned to
        # appropriate field in the output dictionary; in this case,
        # the value for date should be 'None'
        assert (test_items['date'] is None)
        assert (test_items['instrument_id'] == 'D00565')
        assert (test_items['run_number'] == 87)
        assert (test_items['flowcell_id'] == 'C6VG0ANXX')
        assert (test_items['flowcell_position'] == 'A')

    def test_parse_flowcell_run_id_invalid_runnum(self):
        # GIVEN any state

        # WHEN a flowcell run ID is parsed into its component items,
        # but the run ID does not contain a valid run number
        # TODO: use more realistic example
        mock_runid = 'NOTDATE_FCIDENTIFIER'
        test_items = parsing.parse_flowcell_run_id(mock_runid)

        # THEN the components should be correctly parsed and assigned to
        # appropriate field in the output dictionary; in this case,
        # the value for run_number should be 'None'
        assert (test_items['date'] is None)
        assert (test_items['instrument_id'] == 'FCIDENTIFIER')
        assert (test_items['run_number'] is None)
        assert (test_items['flowcell_id'] == '')
        assert (test_items['flowcell_position'] == 'N')

    def test_parse_fastq_filename(self):
        # GIVEN any state

        # WHEN a standard Illumina FASTQ filename is parsed into its
        # component items
        mock_path = ('tests/test-data/genomics/Illumina/'
                     '150615_D00565_0087_AC6VG0ANXX/Unaligned/'
                     'P14-12-23221204/lib7293-25920016/'
                     'MXU01-CO072_S1_L001_R1_001.fastq.gz')
        test_items = parsing.parse_fastq_filename(mock_path)

        # THEN the components should be correctly parsed and assigned to
        # appropriate field in the output dictionary
        assert (test_items['path']
                == ('/genomics/Illumina/'
                    '150615_D00565_0087_AC6VG0ANXX/Unaligned/'
                    'P14-12-23221204/lib7293-25920016/'
                    'MXU01-CO072_S1_L001_R1_001.fastq.gz'))
        assert (test_items['lane_id'] == 'L001')
        assert (test_items['read_id'] == 'R1')
        assert (test_items['sample_number'] == 1)


class TestProcessing:
    """
    Tests methods in the `bripipetools.parsing.processing` module for
    extracting identifiers and other information related to processing
    workflows, batches, steps, and parameters from strings and paths.
    """
    def test_parse_batch_name(self):
        # GIVEN any state

        # WHEN parsing batch name from workflow batch file with name
        # formatted as '<date>_<project1>_..._<projectN>_<fc_id>'
        test_items = parsing.parse_batch_name('160929_P109-1_P14-12_C6VG0ANXX')

        # THEN items should be in a dict with fields for date (datetime),
        # project labels (list of strings), and flowcell ID (string)
        assert (test_items['date'] == datetime.datetime(2016, 9, 29, 0, 0))
        assert (test_items['projects'] == ['P109-1', 'P14-12'])
        assert (test_items['flowcell_id'] == 'C6VG0ANXX')

    @pytest.mark.parametrize(
        'mock_param, expected_result',
        [
            ('SampleName', {'tag': 'SampleName',
                            'type': 'sample',
                            'name': 'SampleName'}),
            ('annotation_tag##_::_::param_name', {'tag': 'annotation_tag',
                                                  'type': 'annotation',
                                                  'name': 'param_name'}),
            ('mock_in##_::_::_::param_name', {'tag': 'mock_in',
                                              'type': 'input',
                                              'name': 'param_name'}),
            ('mock_out##_::_::_::param_name', {'tag': 'mock_out',
                                               'type': 'output',
                                               'name': 'param_name'}),
        ]
    )
    def test_parse_workflow_param(self, mock_param, expected_result):
        # GIVEN any state

        # WHEN a workflow parameter formatted 'tag##unused::details::param_name'
        # is parsed to collect its component parts and classified as 'sample',
        # 'input', 'output', or 'annotation'
        test_items = parsing.parse_workflow_param(mock_param)

        # THEN parsed dict should match expected result
        assert (test_items == expected_result)

    @pytest.mark.parametrize(
        'mock_path, expected_result',
        [
            (
                    'tophat_alignments_bam_out',
                    {'type': 'alignments',
                     'label': 'alignments',
                     'source': 'tophat',
                     'extension': 'bam'}
            ),
            (
                    'picard_markdups_metrics_html_out',
                    {'type': 'metrics',
                     'label': 'metrics',
                     'source': 'picard-markdups',
                     'extension': 'html'}
            ),
            (
                    'picard-markdups_metrics_html_out',
                    {'type': 'metrics',
                     'label': 'metrics',
                     'source': 'picard-markdups',
                     'extension': 'html'}
            ),
            (
                    'bowtie2_alignments-rmdup_bam_out',
                    {'type': 'alignments',
                     'label': 'alignments-rmdup',
                     'source': 'bowtie2',
                     'extension': 'bam'}
            ),
        ]
    )
    def test_parse_output_name(self, mock_path, expected_result):

        # WHEN parsing output name from workflow batch parameter, and the
        # source name has one parts (i.e., 'tophat')
        test_items = parsing.parse_output_name(mock_path)

        # THEN output items should be a dictionary including fields for
        # name, type, and source
        assert (test_items == expected_result)

    @pytest.mark.parametrize(
        'mock_path, expected_result',
        [
            (
                    ('/mnt/genomics/Illumina/161231_INSTID_0001_AC00000XX'
                     'Project_P1-1Processed/alignments/'
                     'lib1111_C00000XX_tophat_alignments.bam'),
                    {'sample_id': 'lib1111_C00000XX',
                     'type': 'alignments',
                     'source': 'tophat'}
            ),
            (
                    ('/mnt/genomics/Illumina/161231_INSTID_0001_AC00000XX'
                     'Project_P1-1Processed/alignments/'
                     'lib1111_tophat_alignments.bam'),
                    {'sample_id': 'lib1111',
                     'type': 'alignments',
                     'source': 'tophat'}
            ),
            (
                    ('/mnt/genomics/Illumina/161231_INSTID_0001_AC00000XX'
                     'Project_P1-1Processed/metrics/'
                     'lib1111_picard_markdups_metrics.html'),
                    {'sample_id': 'lib1111',
                     'type': 'metrics',
                     'source': 'picard-markdups'}
            ),
            (
                    ('/mnt/genomics/Illumina/161231_INSTID_0001_AC00000XX'
                     'Project_P1-1Processed/metrics/'
                     'lib1111_C00000XX_picard_markdups_metrics.html'),
                    {'sample_id': 'lib1111_C00000XX',
                     'type': 'metrics',
                     'source': 'picard-markdups'}
            ),
            (
                    ('/mnt/genomics/Illumina/161231_INSTID_0001_AC00000XX'
                     'Project_P1-1Processed/metrics/'
                     'lib1111_C00000XX_picard-markdups_metrics.html'),
                    {'sample_id': 'lib1111_C00000XX',
                     'type': 'metrics',
                     'source': 'picard-markdups'}
            ),
            (
                    ('/mnt/genomics/Illumina/161231_INSTID_0001_AC00000XX'
                     'Project_P1-1Processed/metrics/'
                     'lib1111_picard-markdups_metrics.html'),
                    {'sample_id': 'lib1111',
                     'type': 'metrics',
                     'source': 'picard-markdups'}
            ),
        ]
    )
    def test_parse_output_filename(self, mock_path, expected_result):

        # WHEN parsing output name from workflow batch parameter, and the
        # source name has one parts (i.e., 'tophat')
        test_items = parsing.parse_output_filename(mock_path)

        # THEN output items should be a dictionary including fields for
        # name, type, and source
        assert (test_items == expected_result)
