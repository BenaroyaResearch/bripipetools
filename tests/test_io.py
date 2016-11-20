import logging

import pytest
from bs4 import BeautifulSoup as bsoup

from bripipetools import io

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# @pytest.fixture(
#     scope='module',
#     params=[{'runnum': r, 'projectnum': p}
#             for r in range(1)
#             for p in range(3)]
# )
# def testproject(request, mock_genomics_server):
#     # GIVEN processing data for one of 3 example projects from a flowcell run
#     runs = mock_genomics_server['root']['genomics']['illumina']['runs']
#     rundata = runs[request.param['runnum']]
#     projects = rundata['processed']['projects']
#     logger.debug("[setup] test project file data")
#
#     yield projects[request.param['projectnum']]
#     logger.debug("[teardown] test project file data")


@pytest.fixture(scope='function')
def mockstringfile(s, tmpdir):
    f = tmpdir.join("mockfile")
    f.write(s)

    return str(f)


class TestPicardMetricsFile:

    def test_read_file(self, tmpdir):
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.PicardMetricsFile(path=testpath)

        assert(len(testfile.data['raw']))

    def test_get_table(self, tmpdir):
        testcontents = (
            """
            <html>
            <body>
            <table cellpadding="3" ><tr><td></td></tr></table>
            </body>
            </html>
            """
            )

        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.PicardMetricsFile(path=testpath)

        # WHEN metrics table is found in raw HTML
        testfile._get_table()

        # THEN
        assert(len(testfile.data['table']) == 1)

    def test_check_table_format_long(self, tmpdir):
        testcontents = (
            """
            <html>
            <body>
            <table cellpadding="3" >
            <tr class="d1"><td>FIELD1</td><td>value1&nbsp;</td></tr>
            <tr class="d0"><td>FIELD2</td><td>value2&nbsp;</td></tr>
            </table>
            </body>
            </html>
            """
            )

        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.PicardMetricsFile(path=testpath)
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN checking whether table in metrics HTML is long or wide
        table_format = testfile._check_table_format()

        # THEN should return the expected format
        assert(table_format == 'long')

    def test_check_table_format_wide(self, tmpdir):
        testcontents = (
            """
            <html>
            <body>
            <table cellpadding="3" >
            <tr class="d0"><td colspan="2">FIELD1	FIELD2</td></tr>
            <tr class="d1"><td colspan="2">value1	value2</td></tr>
            </table>
            </body>
            </html>
            """
            )

        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.PicardMetricsFile(path=testpath)
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN checking whether table in metrics HTML is long or wide
        table_format = testfile._check_table_format()

        # THEN should return the expected format
        assert(table_format == 'wide')

    def test_parse_long(self, tmpdir):
        testcontents = (
            """
            <html>
            <body>
            <table cellpadding="3" >
            <tr class="d1"><td>FIELD1</td><td>value1&nbsp;</td></tr>
            <tr class="d0"><td>FIELD2</td><td>value2&nbsp;</td></tr>
            </table>
            </body>
            </html>
            """
            )

        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.PicardMetricsFile(path=testpath)
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN parsing long format table
        table_data = testfile._parse_long()

        # THEN should return parsed dict
        assert(table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

    def test_parse_wide(self, tmpdir):
        testcontents = (
            """
            <html>
            <body>
            <table cellpadding="3" >
            <tr class="d0"><td colspan="2">FIELD1	FIELD2</td></tr>
            <tr class="d1"><td colspan="2">value1	value2</td></tr>
            </table>
            </body>
            </html>
            """
            )

        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.PicardMetricsFile(path=testpath)
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN parsing wide format table
        table_data = testfile._parse_wide()

        # THEN should return parsed dict
        assert(table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

    def test_parse_w_long_table(self, tmpdir):
        testcontents = (
            """
            <html>
            <body>
            <table cellpadding="3" >
            <tr class="d1"><td>FIELD1</td><td>value1&nbsp;</td></tr>
            <tr class="d0"><td>FIELD2</td><td>value2&nbsp;</td></tr>
            </table>
            </body>
            </html>
            """
            )

        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.PicardMetricsFile(path=testpath)
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN parsing metrics table
        table_data = testfile.parse()

        # THEN should return parsed dict
        assert (table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

    def test_parse_w_wide_table(self, tmpdir):
        testcontents = (
            """
            <html>
            <body>
            <table cellpadding="3" >
            <tr class="d0"><td colspan="2">FIELD1	FIELD2</td></tr>
            <tr class="d1"><td colspan="2">value1	value2</td></tr>
            </table>
            </body>
            </html>
            """
            )

        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.PicardMetricsFile(path=testpath)
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN parsing metrics table
        table_data = testfile.parse()

        # THEN should return parsed dict
        assert (table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})


class TestTophatStatsFile:
    # @pytest.fixture(
    #     scope='class',
    #     params=[(source, {'samplenum': s})
    #             for s in range(3)
    #             for source in
    #             ['tophat_stats']]
    # )
    # def testfiledata(self, request, mock_genomics_server, testproject):
    #     # GIVEN a TophatStatsFile for one of 3 example samples from a
    #     # project, with known details about file path, length, etc.
    #     sourcedata = testproject['metrics']['sources'][request.param[0]]
    #     samplefile = sourcedata[request.param[1]['samplenum']]
    #     logger.debug("[setup] TophatStatsFile test instance "
    #                 "for file type '{}' for sample {}"
    #                  .format(request.param[0], samplefile['sample']))
    #
    #     testfile = io.TophatStatsFile(path=samplefile['path'])
    #     filedata = (mock_genomics_server['out_types']['metrics']
    #                 [request.param[0]])
    #     yield testfile, filedata
    #     logger.debug("[teardown] TophatStatsFile mock instance")

    def test_read_file(self, testfiledata):
        # (GIVEN)
        testfile, filedata = testfiledata

        # WHEN the file specified by path is read
        testfile._read_file()
        raw_text = testfile.data['raw']

        # THEN class should have raw text stored in data attribute and raw
        # text should be a list of expected length
        assert(raw_text)
        assert(len(raw_text) == filedata['raw_len'])
#
#     def test_parse_lines(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN text lines are parsed into key-value pairs based on column
#         metrics = testfile._parse_lines()
#
#         # THEN output dictionary should be expected length and have
#         # the correct keys
#         assert(len(metrics) == filedata['parse_len'])
#         assert(set(metrics.keys()) == set(['fastq_total_reads',
#                                            'reads_aligned_sam', 'aligned',
#                                            'reads_with_mult_align',
#                                            'algn_seg_with_mult_algn']))
#
#     def test_parse(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN file is parsed
#         metrics = testfile.parse()
#
#         # THEN output dictionary should be expected length
#         assert(len(metrics) == filedata['parse_len'])
#
# @pytest.mark.usefixtures('mock_genomics_server', 'testproject')
# class TestHtseqMetricsFile:
#     @pytest.fixture(
#         scope='class',
#         params=[(source, {'samplenum': s})
#                 for s in range(3)
#                 for source in
#                 ['htseq']]
#     )
#     def testfiledata(self, request, mock_genomics_server, testproject):
#         # GIVEN a HtseqMetricsFile for one of 3 example samples from a
#         # project, with known details about file path, length, etc.
#         sourcedata = testproject['metrics']['sources'][request.param[0]]
#         samplefile = sourcedata[request.param[1]['samplenum']]
#         logger.debug("[setup] HtseqMetricsFile test instance "
#                      "for file type '{}' for sample {}"
#                      .format(request.param[0], samplefile['sample']))
#
#         testfile = io.HtseqMetricsFile(path=samplefile['path'])
#         filedata = (mock_genomics_server['out_types']['metrics']
#                     [request.param[0]])
#         yield testfile, filedata
#         logger.debug("[teardown] HtseqMetricsFile mock instance")
#
#     def test_read_file(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN the file specified by path is read
#         testfile._read_file()
#         raw_text = testfile.data['raw']
#
#         # THEN class should have raw text stored in data attribute and raw
#         # text should be a list of expected length
#         assert(raw_text)
#         assert(len(raw_text) == filedata['raw_len'])
#
#     def test_parse_lines(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN text lines are parsed into key-value pairs based on column
#         metrics = testfile._parse_lines()
#
#         # THEN output dictionary should be expected length and have
#         # the correct keys
#         assert(len(metrics) == filedata['parse_len'])
#         assert(set(metrics.keys()) == set(['no_feature', 'ambiguous',
#                                            'too_low_aQual', 'not_aligned',
#                                            'alignment_not_unique']))
#
#     def test_parse(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN file is parsed
#         metrics = testfile.parse()
#
#         # THEN output dictionary should be expected length
#         assert(len(metrics) == filedata['parse_len'])
#
#
# @pytest.mark.usefixtures('mock_genomics_server', 'testproject')
# class TestSexcheckFile:
#     @pytest.fixture(
#         scope='class',
#         params=[(source, {'samplenum': s})
#                 for s in range(3)
#                 for source in
#                 ['sexcheck']]
#     )
#     def testfiledata(self, request, mock_genomics_server, testproject):
#         # GIVEN a SexCheckFile for one of 3 example samples from a
#         # project, with known details about file path, length, etc.
#         sourcedata = testproject['validation']['sources'][request.param[0]]
#         samplefile = sourcedata[request.param[1]['samplenum']]
#         logger.debug("[setup] SexcheckFile test instance "
#                      "for file type '{}' for sample {}"
#                      .format(request.param[0], samplefile['sample']))
#
#         testfile = io.SexcheckFile(path=samplefile['path'])
#         filedata = (mock_genomics_server['qc_types']['validation']
#                     [request.param[0]])
#         yield testfile, filedata
#         logger.debug("[teardown] SexcheckFile mock instance")
#
#     def test_read_file(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN the file specified by path is read
#         testfile._read_file()
#         raw_text = testfile.data['raw']
#
#         # THEN class should have raw text stored in data attribute and raw
#         # text should be a list of expected length
#         assert(raw_text)
#         assert(len(raw_text) == filedata['raw_len'])
#
#     def test_parse_lines(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN text lines are parsed into key-value pairs based on column
#         data = testfile._parse_lines()
#
#         # THEN output dictionary should have the correct keys
#         assert(len(data) == filedata['parse_len'])
#         assert(all(
#             [field in data
#              for field in ['x_genes', 'y_genes', 'x_counts', 'y_counts',
#                            'total_counts', 'y_x_gene_ratio', 'y_x_count_ratio',
#                            'predicted_sex', 'sex_check']]))
#
#     def test_parse(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN file is parsed
#         data = testfile.parse()
#
#         # THEN output dictionary should be expected length
#         assert(len(data) == filedata['parse_len'])
#
#
# @pytest.mark.usefixtures('mock_genomics_server', 'testproject')
# class TestHtseqCountsFile:
#     @pytest.fixture(
#         scope='class',
#         params=[(source, {'samplenum': s})
#                 for s in range(3)
#                 for source in
#                 ['htseq']]
#     )
#     def testfiledata(self, request, mock_genomics_server, testproject):
#         # GIVEN a HtseqCountsFile for one of 3 example samples from a
#         # project, with known details about file path, length, etc.
#         sourcedata = testproject['counts']['sources'][request.param[0]]
#         samplefile = sourcedata[request.param[1]['samplenum']]
#         logger.info("[setup] HtseqCountsFile test instance "
#                     "for file type '{}' for sample {}"
#                     .format(request.param[0], samplefile['sample']))
#
#         testfile = io.HtseqCountsFile(path=samplefile['path'])
#         filedata = (mock_genomics_server['out_types']['counts']
#                     [request.param[0]])
#         yield testfile, filedata
#         logger.info("[teardown] HtseqCountsFile mock instance")
#
#     def test_read_file(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN the file specified by path is read
#         testfile._read_file()
#         counts_df = testfile.data['raw']
#
#         # THEN class should have counts stored in a data frame with
#         # expected number of rows and two columns
#         assert(len(counts_df) == filedata['raw_len'])
#         assert(len(counts_df.columns) == 2)
#
#     def test_parse(self, testfiledata):
#         # (GIVEN)
#         testfile, filedata = testfiledata
#
#         # WHEN file is parsed
#         data = testfile.parse()
#
#         # THEN output data frame should be expected length
#         assert(len(data) == filedata['parse_len'])
#
#
# @pytest.mark.usefixtures('mock_genomics_server', 'testproject')
# class TestFastQCFile:
#     @pytest.fixture(
#         scope='class',
#         params=[(source, {'samplenum': s})
#                 for s in range(3)
#                 for source in
#                 ['fastqc']]
#     )
#     def testfiledata(self, request, mock_genomics_server, testproject):
#         # GIVEN a FastQCFile for one of 3 example samples from a
#         # project, with known details about file path, length, etc.
#         sourcedata = testproject['qc']['sources'][request.param[0]]
#         samplefile = sourcedata[request.param[1]['samplenum']]
#
#         logger.info("[setup] FastQCFile test instance "
#                     "for file type '{}' for sample {}"
#                     .format(request.param[0], samplefile['sample']))
#
#         testfile = io.FastQCFile(path=samplefile['path'])
#         filedata = (mock_genomics_server['out_types']['qc']
#                     [request.param[0]])
#         yield testfile, samplefile, filedata
#         logger.info("[teardown] FastQCFile mock instance")
#
#     def test_read_file(self, testfiledata):
#         # (GIVEN)
#         testfile, samplefile, filedata = testfiledata
#
#         # WHEN the file specified by path is read
#         testfile._read_file()
#         raw_text = testfile.data['raw']
#
#         # THEN class should have raw text stored in data attribute and raw
#         # text should be a list of expected length
#         assert(raw_text)
#         assert(len(raw_text) == samplefile['num_lines'])
#
#     def test_clean_header(self, testfiledata):
#         # (GIVEN)
#         testfile, _, _ = testfiledata
#
#         # WHEN header is cleaned of extra characters and converted to
#         # snake case
#
#         # THEN cleaned header should match expected result
#         assert(testfile._clean_header('>>HEADER One') == 'header_one')
#         assert(testfile._clean_header('#HEADER Two') == 'header_two')
#
#     def test_locate_sections(self, testfiledata):
#         # (GIVEN)
#         testfile, samplefile, filedata = testfiledata
#
#         # WHEN sections are located in the file
#         sections = testfile._locate_sections()
#
#         # THEN should be dictionary of length 12 with correct structure
#         assert(len(sections) == 12)
#         assert(sections['basic_statistics'] == (1, 10))
#
#     def test_get_section_status(self, testfiledata):
#         # (GIVEN)
#         testfile, samplefile, filedata = testfiledata
#
#         # WHEN section header line is parsed to retrieve status
#         (section_name, section_status) = testfile._get_section_status(
#             'basic_statistics', (1, 10))
#
#         # THEN should return a tuple with the expected status
#         assert((section_name, section_status) == ('basic_statistics', 'pass'))
#
#     def test_parse_section_table(self, testfiledata):
#         # (GIVEN)
#         testfile, samplefile, filedata = testfiledata
#
#         # WHEN a table of key-value pairs within a section is parsed
#         section_data = testfile._parse_section_table((1, 10))
#
#         # THEN should return a list of expected length
#         assert(len(section_data) == 7)
#
#     def test_parse(self, testfiledata):
#         # (GIVEN)
#         testfile, samplefile, filedata = testfiledata
#
#         # WHEN FastQC file is parsed
#         fastqcdata = testfile.parse()
#
#         # THEN should return a dictionary of expected length
#         assert(isinstance(fastqcdata, dict))
#         assert(len(fastqcdata) == 20)
#
#     def test_parse_overrepresented_seqs(self, testfiledata):
#         # (GIVEN)
#         testfile, samplefile, filedata = testfiledata
#
#         # WHEN FastQC file is parsed and overrepresented sequences are present
#         overrepseqs = testfile.parse_overrepresented_seqs()
#
#         # THEN should return a list of dictionaries with overrepresented
#         # sequence info
#         assert(isinstance(overrepseqs, list))
#         assert(len(overrepseqs) == samplefile['num_overrep_seqs'])
#         if samplefile['num_overrep_seqs']:
#             assert(isinstance(overrepseqs[0], dict))
#             assert(len(overrepseqs[0]) == 4)
#
#
# # TODO: clean up old testing setup for workflow batch file IO!
#
# @pytest.fixture(
#     scope='module',
#     params=[{'runnum': r, 'batchnum': b}
#             for r in range(1)
#             for b in range(2)]
# )
# def testbatch(request, mock_genomics_server):
#     # GIVEN processing data for one of 2 example batches from a flowcell run
#     runs = mock_genomics_server['root']['genomics']['illumina']['runs']
#     rundata = runs[request.param['runnum']]
#     batches = rundata['submitted']['batches']
#     yield batches[request.param['batchnum']]
#
#
# class TestWorkflowBatchFile:
#     @pytest.fixture(
#         scope='class'
#     )
#     def testfiledata(self, testbatch):
#         # GIVEN a WorkflowBatchFile for a processing batch, with
#         # known details about file path, length, etc.
#         logger.info("[setup] WorkflowBatchFile test instance")
#
#         testfile = io.WorkflowBatchFile(path=testbatch['path'])
#         # filedata = (mock_genomics_server['out_types']['qc']
#         #             [request.param[0]])
#         yield testfile, testbatch
#         logger.info("[teardown] WorkflowBatchFile mock instance")
#
#     def test_locate_workflow_name_line(self, testfiledata):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         assert(testfile._locate_workflow_name_line()
#                == 29)
#
#     def test_locate_batch_name_line(self, testfiledata):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         assert(testfile._locate_batch_name_line()
#                == 31)
#
#     def test_locate_param_line(self, testfiledata):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         assert(testfile._locate_param_line()
#                == 37)
#
#     def test_locate_sample_start_line(self, testfiledata):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         assert(testfile._locate_sample_start_line()
#                == 38)
#
#     def test_get_workflow_name(self, testfiledata):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         assert(testfile.get_workflow_name()
#                == batchdata['workflow'])
#
#     def test_get_batch_name(self, testfiledata):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         assert(testfile.get_batch_name()
#                == batchdata['name'])
#
#     @pytest.mark.parametrize(
#         'test_input, expected_result',
#         [
#             ('SampleName', {'tag': 'SampleName',
#                             'type': 'sample',
#                             'name': 'SampleName'}),
#             ('annotation_tag##_::_::param_name', {'tag': 'annotation_tag',
#                                                   'type': 'annotation',
#                                                   'name': 'param_name'}),
#             ('in_tag##_::_::_::param_name', {'tag': 'in_tag',
#                                              'type': 'input',
#                                              'name': 'param_name'}),
#             ('out_tag##_::_::_::param_name', {'tag': 'out_tag',
#                                               'type': 'output',
#                                               'name': 'param_name'}),
#         ]
#     )
#     def test_parse_param(self, testfiledata, test_input, expected_result):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         assert(testfile._parse_param(test_input) == expected_result)
#
#
#     def test_get_params(self, testfiledata):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         assert(testfile.get_params()[1]
#                == {'tag': 'fastq_in',
#                    'type': 'input',
#                    'name': 'from_endpoint'})
#
#     def test_get_sample_params(self, testfiledata):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         # wbf = workflow_batch_file()
#         assert(testfile.get_sample_params(
#             'lib6839_C6VG0ANXX\tjeddy#srvgridftp01\n')
#                == [{'tag': 'SampleName',
#                     'type': 'sample',
#                     'name': 'SampleName',
#                     'value': 'lib6839_C6VG0ANXX'},
#                    {'tag': 'fastq_in',
#                     'type': 'input',
#                     'name': 'from_endpoint',
#                     'value': 'jeddy#srvgridftp01'}])
#
#     def test_parse_template(self, testfiledata):
#         # (GIVEN)
#         testfile, batchdata = testfiledata
#
#         # wbf = workflow_batch_file()
#         assert(testfile.parse()['workflow_name']
#                == batchdata['workflow'])
#         assert(testfile.parse()['parameters'][1]
#                == {'tag': 'fastq_in',
#                    'type': 'input',
#                    'name': 'from_endpoint'})

    # def test_parse_submit(self, testfiledata):
    #     # (GIVEN)
    #     testfile, batchdata = testfiledata
    #
    #     wbf = workflow_batch_file(state='submit')
    #     assert(wbf.state == 'submit')
    #     assert(wbf.parse()['workflow_name']
    #            == 'optimized_truseq_unstrand_sr_grch38_v0.1_complete')
    #     assert(wbf.parse()['parameters'][1]
    #            == {'tag': 'fastq_in',
    #                'type': 'input',
    #                'name': 'from_endpoint'})
    #     assert(wbf.parse()['samples'][0][1]
    #            == {'tag': 'fastq_in',
    #                'type': 'input',
    #                'name': 'from_endpoint',
    #                'value': 'jeddy#srvgridftp01'})
    #     assert(len(wbf.parse()['parameters'])
    #            == len(wbf.parse()['samples'][0]))
    #
    # def test_write_submit(self):
    #     wbf = workflow_batch_file(state='submit')
    #     path = os.path.join(TEST_FLOWCELL_DIR,
    #             'globus_batch_submission', 'foo.txt')
    #     wbf.write(path)
    #     assert(workflow_batch_file(path).data['raw'] == wbf.data['raw'])
