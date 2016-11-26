import logging

import pytest
from bs4 import BeautifulSoup as bsoup

from bripipetools import io

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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

        testfile._read_file()

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
        testfile.data['raw'] = testcontents


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
        assert(table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

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
        assert(table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})


class TestTophatStatsFile:

    def test_read_file(self, tmpdir):
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.TophatStatsFile(path=testpath)

        testfile._read_file()

        assert(len(testfile.data['raw']))

    def test_parse_lines(self, tmpdir):
        testcontents = ['value1\ttotal reads in fastq file\n',
                        'value2\treads aligned in sam file\n']

        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.TophatStatsFile(path=testpath)
        testfile.data['raw'] = testcontents

        # WHEN parsing
        testfile._parse_lines()
        table_data = testfile.data['table']

        # THEN should return parsed dict
        assert(table_data == {'fastq_total_reads': 'value1',
                              'reads_aligned_sam': 'value2'})

    def test_parse(self, tmpdir):
        testcontents = ('value1\ttotal reads in fastq file\n'
                        'value2\treads aligned in sam file\n')

        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.TophatStatsFile(path=testpath)

        # WHEN parsing
        table_data = testfile.parse()

        # THEN should return parsed dict
        assert(table_data == {'fastq_total_reads': 'value1',
                              'reads_aligned_sam': 'value2'})


class TestHtseqMetricsFile:

    def test_read_file(self, tmpdir):
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.HtseqMetricsFile(path=testpath)

        testfile._read_file()

        assert(len(testfile.data['raw']))

    def test_parse_lines(self, tmpdir):
        testcontents = ['__field_1\tvalue1\n',
                        '__field_2\tvalue2\n']

        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.HtseqMetricsFile(path=testpath)
        testfile.data['raw'] = testcontents

        # WHEN parsing
        testfile._parse_lines()
        table_data = testfile.data['table']

        # THEN should return parsed dict
        assert(table_data == {'field_1': 'value1',
                              'field_2': 'value2'})

    def test_parse(self, tmpdir):
        testcontents = ['__field_1\tvalue1\n',
                        '__field_2\tvalue2\n']

        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.HtseqMetricsFile(path=testpath)

        # WHEN parsing
        table_data = testfile.parse()

        # THEN should return parsed dict
        assert(table_data == {'field_1': 'value1',
                              'field_2': 'value2'})

class TestSexcheckFile:

    def test_read_file(self, tmpdir):
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.SexcheckFile(path=testpath)

        testfile._read_file()

        assert(len(testfile.data['raw']))

    def test_parse_lines(self, tmpdir):
        testcontents = ['field1,field2\n',
                        'value1,value2\n']

        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.SexcheckFile(path=testpath)
        testfile.data['raw'] = testcontents

        # WHEN parsing
        testfile._parse_lines()
        table_data = testfile.data['table']

        # THEN should return parsed dict
        assert(table_data == {'field1': 'value1',
                              'field2': 'value2'})

    def test_parse(self, tmpdir):
        testcontents = ['field1,field2\n',
                        'value1,value2\n']

        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.SexcheckFile(path=testpath)

        # WHEN parsing
        table_data = testfile.parse()

        # THEN should return parsed dict
        assert(table_data == {'field1': 'value1',
                              'field2': 'value2'})


class TestHtseqCountsFile:

    def test_read_file(self, tmpdir):
        testcontents = ['variable1\tvalue1\n',
                        'variable2\tvalue2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.HtseqCountsFile(path=testpath)

        testfile._read_file()

        assert(len(testfile.data['table']) == 2)
        assert(len(testfile.data['table'].columns) == 2)

    def test_parse(self, tmpdir):
        testcontents = ['variable1\tvalue1\n',
                        'variable2\tvalue2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.HtseqCountsFile(path=testpath)

        table_data = testfile.parse()

        assert(len(table_data) == 2)
        assert(len(table_data.columns) == 2)


class TestFastQCFile:

    def test_read_file(self, tmpdir):
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.FastQCFile(path=testpath)

        testfile._read_file()

        assert (len(testfile.data['raw']))

    def test_clean_header(self):
        testfile = io.FastQCFile(path='')

        # WHEN header is cleaned of extra characters and converted to
        # snake case

        # THEN cleaned header should match expected result
        assert(testfile._clean_header('>>HEADER One') == 'header_one')
        assert(testfile._clean_header('#HEADER Two') == 'header_two')

    def test_clean_value(self):
        testfile = io.FastQCFile(path='')

        # WHEN value is cleaned

        # THEN cleaned value should match expected result
        assert(testfile._clean_value('1.0') == 1.0)
        assert(testfile._clean_value('value1') == 'value1')
        assert(testfile._clean_value('') == '')

    def test_locate_sections(self):
        testcontents = ['##FastQC\t0.11.3\n',
                        '>>Module Header 1\tpass\n',
                        'module line\n',
                        '>>END_MODULE\n',
                        '>>Module Header 2\tfail\n',
                        'module line\n',
                        '>>END_MODULE\n']
        testfile = io.FastQCFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN sections are located in the file
        sections = testfile._locate_sections()

        # THEN should be dictionary of expected format
        assert(sections == {'module_header_1': (1, 3),
                            'module_header_2': (4, 6)})

    def test_get_section_status(self):
        testcontents = ['>>Module Header 1\tpass\n',
                        '>>END_MODULE\n']
        testfile = io.FastQCFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN section header line is parsed to retrieve status
        (section_name, section_status) = testfile._get_section_status(
            'module_header_1', (0, 1))

        # THEN should return a tuple with the expected status
        assert((section_name, section_status) == ('module_header_1', 'pass'))

    def test_parse_section_table(self):
        testcontents = ['>>Module Header 1\tpass\n',
                        'field1\tvalue1\n',
                        'field2\t1.0\n',
                        '>>END_MODULE\n']
        testfile = io.FastQCFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN a table of key-value pairs within a section is parsed
        section_data = testfile._parse_section_table((0, 3))

        # THEN should return a list of expected length
        assert(section_data == [('field1', 'value1'),
                                ('field2', 1.0)])

    def test_parse(self, tmpdir):
        testcontents = ['##FastQC\t0.11.3\n',
                        '>>Basic Statistics\tpass\n',
                        'field1\tvalue1\n',
                        'field2\t1.0\n',
                        '>>END_MODULE\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.FastQCFile(path=testpath)

        table_data = testfile.parse()

        assert(table_data == {'basic_statistics': 'pass',
                              'field1': 'value1',
                              'field2': 1.0})

    def test_parse_overrepresented_seqs(self, tmpdir):
        testcontents = [
            '##FastQC\t0.11.3\n'
            '>>Overrepresented sequences\twarn\n',
            '#Sequence\tCount\tPercentage\tPossible Source\n',
            'ACGT\t10\t0.10\tType, Number 1 (10% over 10 bp)\n',
            '>>END_MODULE\n'
            ]
        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.FastQCFile(path=testpath)

        table_data = testfile.parse_overrepresented_seqs()

        assert(table_data == [{'sequence': 'ACGT',
                               'count': 10,
                               'percentage': 0.1,
                               'possible_source':
                                   'Type, Number 1 (10% over 10 bp)'}])

    def test_parse_overrepresented_seqs_pass(self, tmpdir):
        testcontents = [
            '##FastQC\t0.11.3\n'
            '>>Overrepresented sequences\tpass\n',
            '>>END_MODULE\n'
            ]
        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.FastQCFile(path=testpath)

        table_data = testfile.parse_overrepresented_seqs()

        assert(table_data == [])

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
