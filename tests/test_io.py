import logging
from collections import OrderedDict

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
    """
    Tests class for reading and parsing data from Picard metrics
    files, which are typically in HTML format.
    """
    def test_read_file(self, tmpdir):
        # GIVEN some file exists with arbitrary contents
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)

        # AND an io class object is created for that file
        testfile = io.PicardMetricsFile(path=testpath)

        # WHEN the contents of the file are read and stored
        testfile._read_file()

        # THEN the unformatted contents should be stored in the raw
        # field of the file object's data attribute
        assert(len(testfile.data['raw']))

    def test_get_table(self):
        # GIVEN some HTML file content with at least one table with the
        # expected formatting tag (i.e., 'cellpadding="3"')
        testcontents = (
            """
            <html>
            <body>
            <table cellpadding="3" ><tr><td></td></tr></table>
            </body>
            </html>
            """
            )

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.PicardMetricsFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN metrics table is retrieved from the raw HTML
        testfile._get_table()

        # THEN the table should be the expected length; in this case
        # a single row
        assert(len(testfile.data['table']) == 1)

    def test_check_table_format_long(self):
        # GIVEN some HTML file content with at least one table with the
        # expected formatting and cell contents that indicate data is
        # reported as two columns per row, with each row containing
        # fields and values in respective columns
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

        # AND an io class object with the table contents stored in the
        # table field of its data attribute
        testfile = io.PicardMetricsFile(path='')
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN checking whether the table is 'long' or 'wide' format
        table_format = testfile._check_table_format()

        # THEN should return 'long'
        assert(table_format == 'long')

    def test_check_table_format_wide(self):
        # GIVEN some HTML file content with at least one table with the
        # expected formatting and cell contents that indicate data is
        # reported as two rows, with tab-separated fields in the first row
        # and tab-separated values in the second row
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

        # AND an io class object with the table contents stored in the
        # table field of its data attribute
        testfile = io.PicardMetricsFile(path='')
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN checking whether the table is 'long' or 'wide' format
        table_format = testfile._check_table_format()

        # THEN should return 'wide'
        assert(table_format == 'wide')

    def test_parse_long(self):
        # GIVEN some HTML file content with at least one table with the
        # expected formatting and cell contents that indicate data is
        # reported as two columns per row, with each row containing
        # fields and values in respective columns - i.e., 'long' format
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

        # AND an io class object with the table contents stored in the
        # table field of its data attribute
        testfile = io.PicardMetricsFile(path='')
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN the table is parsed
        table_data = testfile._parse_long()

        # THEN should return a dict with fields and values stored as
        # key-value pairs
        assert(table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

    def test_parse_wide(self):
        # GIVEN some HTML file content with at least one table with the
        # expected formatting and cell contents that indicate data is
        # reported as two rows, with tab-separated fields in the first row
        # and tab-separated values in the second row - i.e., 'wide' format
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

        # AND an io class object with the table contents stored in the
        # table field of its data attribute
        testfile = io.PicardMetricsFile(path='')
        testfile.data['table'] = bsoup(testcontents, 'html.parser').table

        # WHEN the table is parsed
        table_data = testfile._parse_wide()

        # THEN should return a dict with fields and values stored as
        # key-value pairs
        assert(table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

    def test_parse_w_long_table(self, tmpdir):
        # GIVEN an HTML file with at least one table with the
        # expected formatting and cell contents that indicate data is
        # reported as two columns per row, with each row containing
        # fields and values in respective columns - i.e., 'long' format
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

        # AND an io class object is created for that file
        testfile = io.PicardMetricsFile(path=testpath)

        # WHEN parsing metrics table
        table_data = testfile.parse()

        # THEN should return parsed dict
        assert(table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

    def test_parse_w_wide_table(self, tmpdir):
        # GIVEN an HTML file with at least one table with the
        # expected formatting and cell contents that indicate data is
        # reported as two rows, with tab-separated fields in the first row
        # and tab-separated values in the second row - i.e., 'wide' format
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

        # AND an io class object is created for that file
        testfile = io.PicardMetricsFile(path=testpath)

        # WHEN parsing metrics table
        table_data = testfile.parse()

        # THEN should return parsed dict
        assert(table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})


class TestTophatStatsFile:
    """
    Tests class for reading and parsing data from Tophat stats
    metrics files, which are typically in tab-delimited text format.
    """
    def test_read_file(self, tmpdir):
        # GIVEN some file exists with arbitrary contents
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)

        # AND an io class object is created for that file
        testfile = io.TophatStatsFile(path=testpath)

        # WHEN the contents of the file are read and stored
        testfile._read_file()

        # THEN the unformatted contents should be stored in the raw
        # field of the file object's data attribute
        assert(len(testfile.data['raw']))

    def test_parse_lines(self):
        # GIVEN some file content, where data is reported in a table
        # with each row containing value and field (separated by tab)
        testcontents = ['value1\ttotal reads in fastq file\n',
                        'value2\treads aligned in sam file\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.TophatStatsFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN contents are parsed line-by-line and stored in the
        # table field of the object's data attribute
        testfile._parse_lines()
        table_data = testfile.data['table']

        # THEN the table should include key-value pairs for each
        # field, stored in a dict
        assert(table_data == {'fastq_total_reads': 'value1',
                              'reads_aligned_sam': 'value2'})

    def test_parse(self, tmpdir):
        # GIVEN a file, where data is reported in a table
        # with each row containing value and field (separated by tab)
        testcontents = ('value1\ttotal reads in fastq file\n'
                        'value2\treads aligned in sam file\n')
        testpath = mockstringfile(testcontents, tmpdir)

        # AND an io class object is created for that file
        testfile = io.TophatStatsFile(path=testpath)

        # WHEN contents are read and parsed
        table_data = testfile.parse()

        # THEN the table should include key-value pairs for each
        # field, stored in a dict
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

        assert(len(testfile.data['raw']))

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

class TestWorkflowBatchFile:

    def test_read_file(self, tmpdir):
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)
        testfile = io.WorkflowBatchFile(path=testpath)

        testfile._read_file()

        assert(len(testfile.data['raw']))

    def test_locate_workflow_name_line(self):
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Workflow Name\toptimized_workflow_1\n']
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN
        line = testfile._locate_workflow_name_line()

        # THEN
        assert(line == 2)

    def test_locate_batch_name_line(self):
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Project Name\tDATE_P00-00_FLOWCELL\n']
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN
        line = testfile._locate_batch_name_line()

        # THEN
        assert(line == 2)

    def test_locate_param_line(self):
        testcontents = ['###TABLE DATA\n',
                        '#############\n',
                        'SampleName\n']
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN
        line = testfile._locate_param_line()

        # THEN
        assert(line == 2)

    def test_locate_sample_start_line(self):
        testcontents = ['###TABLE DATA\n',
                        '#############\n',
                        'SampleName\n',
                        'sample1\n']
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN
        line = testfile._locate_sample_start_line()

        # THEN
        assert(line == 3)

    def test_get_workflow_name(self):
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Workflow Name\toptimized_workflow_1\n']
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN
        workflow_name = testfile.get_workflow_name()

        # THEN
        assert(workflow_name == 'optimized_workflow_1')

    def test_get_batch_name(self):
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Project Name\tDATE_P00-00_FLOWCELL\n']
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN
        batch_name = testfile.get_batch_name()

        # THEN
        assert(batch_name == 'DATE_P00-00_FLOWCELL')

    @pytest.mark.parametrize(
        'test_input, expected_result',
        [
            ('SampleName', {'tag': 'SampleName',
                            'type': 'sample',
                            'name': 'SampleName'}),
            ('annotation_tag##_::_::param_name', {'tag': 'annotation_tag',
                                                  'type': 'annotation',
                                                  'name': 'param_name'}),
            ('in_tag##_::_::_::param_name', {'tag': 'in_tag',
                                             'type': 'input',
                                             'name': 'param_name'}),
            ('out_tag##_::_::_::param_name', {'tag': 'out_tag',
                                              'type': 'output',
                                              'name': 'param_name'}),
        ]
    )
    def test_parse_param(self, test_input, expected_result):
        testfile = io.WorkflowBatchFile(path='')

        assert(testfile._parse_param(test_input) == expected_result)

    def test_get_params(self):
        testcontents = ['###TABLE DATA\n',
                        '#############\n',
                        'SampleName\tin_tag##_::_::_::param_name\n',
                        'sample1\tin_value1\n']
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        test_params = testfile.get_params()

        assert(test_params[0] == {'tag': 'SampleName',
                                  'type': 'sample',
                                  'name': 'SampleName'})
        assert(test_params[1] == {'tag': 'in_tag',
                                  'type': 'input',
                                  'name': 'param_name'})

    def test_get_sample_params(self):
        testcontents = ['###TABLE DATA\n',
                        '#############\n',
                        'SampleName\tin_tag##_::_::_::param_name\n',
                        'sample1\tin_value1\n',
                        'sample2\tin_value2\n']
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        test_sample_params = testfile.get_sample_params(testcontents[3])

        assert(test_sample_params == [
            {'name': 'SampleName',
             'tag': 'SampleName',
             'type': 'sample',
             'value': 'sample1'},
            {'name': 'param_name',
             'tag': 'in_tag',
             'type': 'input',
             'value': 'in_value1'}
            ])

    def test_parse_submit(self, tmpdir):
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Workflow Name\toptimized_workflow_1\n',
                        'Project Name\tDATE_P00-00_FLOWCELL\n',
                        '###TABLE DATA\n',
                        '#############\n',
                        'SampleName\tin_tag##_::_::_::param_name\n',
                        'sample1\tin_value1\n',
                        'sample2\tin_value2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.WorkflowBatchFile(path=testpath, state='submit')

        test_data = testfile.parse()

        assert(test_data == {
            'workflow_name': 'optimized_workflow_1',
            'batch_name': 'DATE_P00-00_FLOWCELL',
            'raw': testcontents,
            'parameters': [
                {'name': 'SampleName', 'tag': 'SampleName', 'type': 'sample'},
                {'name': 'param_name', 'tag': 'in_tag', 'type': 'input'}
            ],
            'samples': [
                [
                    {'tag': 'SampleName',
                     'type': 'sample',
                     'name': 'SampleName',
                     'value': 'sample1'},
                    {'tag': 'in_tag',
                     'type': 'input',
                     'name': 'param_name',
                     'value': 'in_value1'}
                ],
                [
                    {'tag': 'SampleName',
                     'type': 'sample',
                     'name': 'SampleName',
                     'value': 'sample2'},
                    {'tag': 'in_tag',
                     'type': 'input',
                     'name': 'param_name',
                     'value': 'in_value2'}
                ]
            ]
        })

    def test_write(self, tmpdir):
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Workflow Name\toptimized_workflow_1\n',
                        'Project Name\tDATE_P00-00_FLOWCELL\n',
                        '###TABLE DATA\n',
                        '#############\n',
                        'SampleName\tin_tag##_::_::_::param_name\n',
                        'sample1\tin_value1\n',
                        'sample2\tin_value2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)
        testfile = io.WorkflowBatchFile(path=testpath, state='submit')

        outfile = tmpdir.join("newfile")

        testfile.write(str(outfile))

        assert(outfile.readlines() == testcontents)

