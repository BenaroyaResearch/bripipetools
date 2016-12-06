import pytest

from bripipetools import parsing


class TestIllumina:
    """
    Tests methods for extracting identifiers and other information
    related to Illumina sequencing technology from strings and paths.
    """
    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            ('P00Processed', 'P00'),
            ('P00-00Processed', 'P00-00'),
            ('P00-00-0000', 'P00-00'),
        ]
    )
    def test_get_project_label(self, test_input, expected_result):
        # GIVEN any state

        # WHEN some string is searched for a Genomics Core project label
        # (i.e., 'P<project ID>-<subproject ID>'), where the subproject
        # ID may or may not be included

        # THEN the output string should match the expected result
        assert (parsing.get_project_label(test_input) == expected_result)

    def test_parse_project_label(self):
        # GIVEN any state

        # WHEN a project label of format 'P<number>-<number>' is parsed
        # into component items
        project_items = parsing.parse_project_label('P1-2')

        # THEN the dictionary should have the first number with key 'project_id'
        # and the second number with key 'subproject_id'
        assert (project_items['project_id'] == 1)
        assert (project_items['subproject_id'] == 2)

    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            ('lib1234-1234', 'lib1234'),
            ('Sample_lib1234', 'lib1234'),
            ('Sample1234', ''),
        ]
    )
    def test_get_library_id(self, test_input, expected_result):
        # GIVEN any state

        # WHEN some string is searched for a Genomics Core library ID
        # (i.e., 'lib0000')

        # THEN the output string should match the expected result
        # (i.e., the matched library ID or an empty string, if no
        # match found)
        assert (parsing.get_library_id(test_input) == expected_result)

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
        run_id = '150615_D00565_0087_AC6VG0ANXX'
        run_items = parsing.parse_flowcell_run_id(run_id)

        # THEN the components should be correctly parsed and assigned to
        # appropriate field in the output dictionary
        assert (run_items['date'] == '2015-06-15')
        assert (run_items['instrument_id'] == 'D00565')
        assert (run_items['run_number'] == 87)
        assert (run_items['flowcell_id'] == 'C6VG0ANXX')
        assert (run_items['flowcell_position'] == 'A')

    def test_parse_flowcell_run_id_invalid_date(self):
        # GIVEN any state

        # WHEN a flowcell run ID is parsed into its component items,
        # but the run ID does not contain a valid date
        run_id = 'NOTDATE_D00565_0087_AC6VG0ANXX'
        run_items = parsing.parse_flowcell_run_id(run_id)

        # THEN the components should be correctly parsed and assigned to
        # appropriate field in the output dictionary; in this case,
        # the value for date should be 'None'
        assert (run_items['date'] is None)
        assert (run_items['instrument_id'] == 'D00565')
        assert (run_items['run_number'] == 87)
        assert (run_items['flowcell_id'] == 'C6VG0ANXX')
        assert (run_items['flowcell_position'] == 'A')

    def test_parse_flowcell_run_id_invalid_runnum(self):
        # GIVEN any state

        # WHEN a flowcell run ID is parsed into its component items,
        # but the run ID does not contain a valid run number
        # TODO: use more realistic example
        run_id = 'NOTDATE_FCIDENTIFIER'
        run_items = parsing.parse_flowcell_run_id(run_id)

        # THEN the components should be correctly parsed and assigned to
        # appropriate field in the output dictionary; in this case,
        # the value for run_number should be 'None'
        assert (run_items['date'] is None)
        assert (run_items['instrument_id'] == 'FCIDENTIFIER')
        assert (run_items['run_number'] is None)
        assert (run_items['flowcell_id'] == '')
        assert (run_items['flowcell_position'] == 'N')

    def test_parse_fastq_filename(self):
        # GIVEN any state

        # WHEN a standard Illumina FASTQ filename is parsed into its
        # component items
        path = ('tests/test-data/genomics/Illumina/'
                '150615_D00565_0087_AC6VG0ANXX/Unaligned/'
                'P14-12-23221204/lib7293-25920016/'
                'MXU01-CO072_S1_L001_R1_001.fastq.gz')
        fastq_items = parsing.parse_fastq_filename(path)

        # THEN the components should be correctly parsed and assigned to
        # appropriate field in the output dictionary
        assert (fastq_items['path']
                == ('/genomics/Illumina/'
                    '150615_D00565_0087_AC6VG0ANXX/Unaligned/'
                    'P14-12-23221204/lib7293-25920016/'
                    'MXU01-CO072_S1_L001_R1_001.fastq.gz'))
        assert (fastq_items['lane_id'] == 'L001')
        assert (fastq_items['read_id'] == 'R1')
        assert (fastq_items['sample_number'] == 1)
