import logging

import pytest
from bs4 import BeautifulSoup as bsoup

from bripipetools import io

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def mockstringfile(s, tmpdir):
    """
    Given a 'tmpdir' object and an input string, return a
    temporary file object with string written as contents.
    """
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
        assert (len(testfile.data['raw']))

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
        assert (len(testfile.data['table']) == 1)

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
        assert (table_format == 'long')

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
        assert (table_format == 'wide')

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
        assert (table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

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
        assert (table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

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
        assert (table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})

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
        assert (table_data == {'FIELD1': 'value1', 'FIELD2': 'value2'})


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
        assert (len(testfile.data['raw']))

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
        assert (table_data == {'fastq_total_reads': 'value1',
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
        assert (table_data == {'fastq_total_reads': 'value1',
                               'reads_aligned_sam': 'value2'})


class TestHtseqMetricsFile:
    """
    Tests class for reading and parsing data from htseq-count
    metrics files, which are typically in tab-delimited text format.
    """
    def test_read_file(self, tmpdir):
        # GIVEN some file exists with arbitrary contents
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)

        # AND an io class object is created for that file
        testfile = io.HtseqMetricsFile(path=testpath)

        # WHEN the contents of the file are read and stored
        testfile._read_file()

        # THEN the unformatted contents should be stored in the raw
        # field of the file object's data attribute
        assert (len(testfile.data['raw']))

    def test_parse_lines(self, tmpdir):
        # GIVEN some file content, where data is reported in a table
        # with each row containing field and value (separated by tab)
        testcontents = ['__field_1\tvalue1\n',
                        '__field_2\tvalue2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.HtseqMetricsFile(path=testpath)
        testfile.data['raw'] = testcontents

        # WHEN contents are parsed line-by-line and stored in the
        # table field of the object's data attribute
        testfile._parse_lines()
        table_data = testfile.data['table']

        # THEN the table should include key-value pairs for each
        # field, stored in a dict
        assert (table_data == {'field_1': 'value1',
                               'field_2': 'value2'})

    def test_parse(self, tmpdir):
        # GIVEN a file, where data is reported in a table
        # with each row containing field and value (separated by tab)
        testcontents = ['__field_1\tvalue1\n',
                        '__field_2\tvalue2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object is created for that file
        testfile = io.HtseqMetricsFile(path=testpath)

        # WHEN contents are read and parsed
        table_data = testfile.parse()

        # THEN the table should include key-value pairs for each
        # field, stored in a dict
        assert (table_data == {'field_1': 'value1',
                               'field_2': 'value2'})


class TestSexcheckFile:
    """
    Tests class for reading and parsing data from sample sex check
    validation files, which are in comma-separated text format.
    """
    def test_read_file(self, tmpdir):
        # GIVEN some file exists with arbitrary contents
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)

        # AND an io class object is created for that file
        testfile = io.SexcheckFile(path=testpath)

        # WHEN the contents of the file are read and stored
        testfile._read_file()

        # THEN the unformatted contents should be stored in the raw
        # field of the file object's data attribute
        assert (len(testfile.data['raw']))

    def test_parse_lines(self, tmpdir):
        # GIVEN some file content, where data is reported in a table
        # with each row containing field and value (separated by comma)
        testcontents = ['field1,field2\n',
                        'value1,value2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.SexcheckFile(path=testpath)
        testfile.data['raw'] = testcontents

        # WHEN contents are parsed line-by-line and stored in the
        # table field of the object's data attribute
        testfile._parse_lines()
        table_data = testfile.data['table']

        # THEN the table should include key-value pairs for each
        # field, stored in a dict
        assert (table_data == {'field1': 'value1',
                               'field2': 'value2'})

    def test_parse(self, tmpdir):
        # GIVEN a file, where data is reported in a table
        # with each row containing field and value (separated by comma)
        testcontents = ['field1,field2\n',
                        'value1,value2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object is created for that file
        testfile = io.SexcheckFile(path=testpath)

        # WHEN contents are read and parsed
        table_data = testfile.parse()

        # THEN the table should include key-value pairs for each
        # field, stored in a dict
        assert (table_data == {'field1': 'value1',
                               'field2': 'value2'})


class TestHtseqCountsFile:
    """
    Tests class for reading and parsing data from htseq-count
    count files, which are typically in tab-delimited text format.
    """
    def test_read_file(self, tmpdir):
        # GIVEN some file exists with arbitrary contents
        testcontents = ['variable1\tvalue1\n',
                        'variable2\tvalue2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object is created for that file
        testfile = io.HtseqCountsFile(path=testpath)

        # WHEN the contents of the file are read and stored
        testfile._read_file()

        # THEN the contents should be stored as a data frame in the
        # table field of the file object's data attribute
        assert (len(testfile.data['table']) == 2)
        assert (len(testfile.data['table'].columns) == 2)

    def test_parse(self, tmpdir):
        # GIVEN a file, where data is reported in a table
        # with each row containing a variable (e.g., a gene name)
        # and value (separated by tab)
        testcontents = ['variable1\tvalue1\n',
                        'variable2\tvalue2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object is created for that file
        testfile = io.HtseqCountsFile(path=testpath)

        # WHEN the contents of the file are read and stored
        table_data = testfile.parse()

        # THEN the contents should be stored as a data frame in the
        # table field of the file object's data attribute; the data frame
        # should have 2 columns and the expected number of rows
        assert (len(table_data) == 2)
        assert (len(table_data.columns) == 2)


class TestFastQCFile:
    """
    Tests class for reading and parsing data from FastQC quality
    control files, which are in a custom text format, but include
    some useful reference features (e.g., consistently formatted sections
    and headers, tab-delimited tables in selected sections).
    """
    def test_read_file(self, tmpdir):
        # GIVEN some file exists with arbitrary contents
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)

        # AND an io class object is created for that file
        testfile = io.FastQCFile(path=testpath)

        # WHEN the contents of the file are read and stored
        testfile._read_file()

        # THEN the unformatted contents should be stored in the raw
        # field of the file object's data attribute
        assert (len(testfile.data['raw']))

    def test_clean_header(self):
        # GIVEN an io class object for an arbitrary file
        testfile = io.FastQCFile(path='')

        # WHEN header is cleaned of extra characters and converted to
        # snake case

        # THEN cleaned header should match expected result
        assert (testfile._clean_header('>>HEADER One') == 'header_one')
        assert (testfile._clean_header('#HEADER Two') == 'header_two')

    def test_clean_value(self):
        # GIVEN an io class object for an arbitrary file
        testfile = io.FastQCFile(path='')

        # WHEN value is cleaned to convert completely numeric data to float

        # THEN cleaned value should match expected result
        assert (testfile._clean_value('1.0') == 1.0)
        assert (testfile._clean_value('value1') == 'value1')
        assert (testfile._clean_value('') == '')

    def test_locate_sections(self):
        # GIVEN some file content, where data is divided into sections
        # demarcated by '>>' characters followed by module name and
        # module status (separated by tab) on the same line, one to many
        # lines of module content, and a terminating line ('>>END_MODULE')
        testcontents = ['##FastQC\t0.11.3\n',
                        '>>Module Header 1\tpass\n',
                        'module line\n',
                        '>>END_MODULE\n',
                        '>>Module Header 2\tfail\n',
                        'module line\n',
                        '>>END_MODULE\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.FastQCFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN sections are located in the file
        sections = testfile._locate_sections()

        # THEN should be dictionary with a tuple for each section
        # indicating the the start and end lines of the section/module
        assert (sections == {'module_header_1': (1, 3),
                             'module_header_2': (4, 6)})

    def test_get_section_status(self):
        # GIVEN some file content representing the typical format of a
        # section header, where sections contain results from modules
        testcontents = ['>>Module Header 1\tpass\n',
                        '>>END_MODULE\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.FastQCFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN section header line is parsed to retrieve status
        (section_name, section_status) = testfile._get_section_status(
            'module_header_1', (0, 1)
        )

        # THEN should return a tuple with module name and expected status
        assert ((section_name, section_status) == ('module_header_1', 'pass'))

    def test_parse_section_table(self):
        # GIVEN some file content representing the typical format of a
        # section with data organized in a tab-delimited table
        testcontents = ['>>Module Header 1\tpass\n',
                        'field1\tvalue1\n',
                        'field2\t1.0\n',
                        '>>END_MODULE\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.FastQCFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN the table of key-value pairs within a section is parsed
        section_data = testfile._parse_section_table((0, 3))

        # THEN should return a list of expected length, where each item
        # is a tuple of field and value from the table
        assert(section_data == [('field1', 'value1'),
                                ('field2', 1.0)])

    def test_parse(self, tmpdir):
        # GIVEN a file, where data is divided into sections, and at least
        # one section contains module results in a tab-delimited table
        testcontents = ['##FastQC\t0.11.3\n',
                        '>>Basic Statistics\tpass\n',
                        'field1\tvalue1\n',
                        'field2\t1.0\n',
                        '>>END_MODULE\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object is created for that file
        testfile = io.FastQCFile(path=testpath)

        # WHEN the contents of the file are read and stored
        table_data = testfile.parse()

        # THEN the table should include key-value pairs for each
        # section indicating module name and status, as well as each
        # key-value pair for fields and values from any module tables
        assert (table_data == {'basic_statistics': 'pass',
                               'field1': 'value1',
                               'field2': 1.0})

    def test_parse_overrepresented_seqs(self, tmpdir):
        # GIVEN a file, where data is divided into sections, and the
        # 'Overrepresented sequences' section has a non-passing status,
        # i.e., includes tab-delimited data for one or more sequence
        testcontents = [
            '##FastQC\t0.11.3\n'
            '>>Overrepresented sequences\twarn\n',
            '#Sequence\tCount\tPercentage\tPossible Source\n',
            'ACGT\t10\t0.10\tType, Number 1 (10% over 10 bp)\n',
            '>>END_MODULE\n'
        ]
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object is created for that file
        testfile = io.FastQCFile(path=testpath)

        # WHEN the contents of the file are read and stored
        table_data = testfile.parse_overrepresented_seqs()

        # THEN the table should be a list of dicts, where each dict
        # contains key-value pairs for tab-separated data from each
        # overrepresented sequence
        assert (table_data == [{'sequence': 'ACGT',
                                'count': 10,
                                'percentage': 0.1,
                                'possible_source':
                                    'Type, Number 1 (10% over 10 bp)'}])

    def test_parse_overrepresented_seqs_pass(self, tmpdir):
        # GIVEN a file, where data is divided into sections, and the
        # 'Overrepresented sequences' section has passing status,
        # i.e., no overrepresented sequences
        testcontents = [
            '##FastQC\t0.11.3\n'
            '>>Overrepresented sequences\tpass\n',
            '>>END_MODULE\n'
        ]
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object is created for that file
        testfile = io.FastQCFile(path=testpath)

        # WHEN the contents of the file are read and stored
        table_data = testfile.parse_overrepresented_seqs()

        # THEN the table should be an empty list
        assert (table_data == [])


class TestWorkflowFile:
    """
    Tests class for reading and parsing data from Galaxy or Globus
    Galaxy workflow files, typically in JSON format.
    """
    def test_read_file(self, tmpdir):
        # GIVEN some file exists with arbitrary contents
        testcontents = '{"field": "value"}'
        testpath = mockstringfile(testcontents, tmpdir)

        # AND an io class object is created for that file
        testfile = io.WorkflowFile(path=testpath)

        # WHEN the contents of the file are read and stored
        testfile._read_file()

        # THEN the contents should be stored as a dictionary in the
        # raw field of the file object's data attribute
        assert len(testfile.data['raw'])


    def test_parse(self, tmpdir):
        # GIVEN a file, where data is reported in a JSON-like
        # map of key-value pairs
        testname = "wkflow_name"
        testtoolname = "globus_tool"
        testversion = "1.0.0"
        testcontents = ('{"name": "' + testname + '",' +
                        '"steps":{' +
                        '"0":{' +
                        '"tool_id": "' + testtoolname + '",' +
                        '"tool_version": "' + testversion + '"}}}')
        testpath = mockstringfile(testcontents, tmpdir)

        # AND an io class object is created for that file
        testfile = io.WorkflowFile(path=testpath)

        # WHEN the contents of the file are read and stored
        testdata = testfile.parse()

        # THEN the contents should be stored as a dictionary in the
        # raw field of the file object's data attribute
        assert len(testdata)
        
        # AND workflow name and tool information should be stored as dicts in
        # the name and tools fields of the file object's data attribute
        assert (testdata['name'] == testname and
                testdata['tools'][testtoolname] == testversion)


class TestWorkflowBatchFile:
    """
    Tests class for reading and parsing data from Globus Galaxy
    workflow batch submission files, which contain instructions in
    comment lines, a tab-delimited table with workflow batch
    metadata values, and a tab-delimited table with workflow
    parameters for each sample in the batch.
    """
    def test_read_file(self, tmpdir):
        # GIVEN some file exists with arbitrary contents
        testcontents = 'testline\n'
        testpath = mockstringfile(testcontents, tmpdir)

        # AND an io class object is created for that file
        testfile = io.WorkflowBatchFile(path=testpath)

        # WHEN the contents of the file are read and stored
        testfile._read_file()

        # THEN the unformatted contents should be stored in the raw
        # field of the file object's data attribute
        assert (len(testfile.data['raw']))

    def test_locate_workflow_name_line(self):
        # GIVEN some file content representing the typical format of a
        # a metadata table, where data is with each row containing
        # field and value (separated by tab)
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Workflow Name\toptimized_workflow_1\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN content is searched to find the metadata line with
        # workflow name
        line = testfile._locate_workflow_name_line()

        # THEN should be the expected line number
        assert (line == 2)

    def test_locate_batch_name_line(self):
        # GIVEN some file content representing the typical format of a
        # a metadata table, where data is reported with each row containing
        # field and value (separated by tab)
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Project Name\tDATE_P00-00_FLOWCELL\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN content is searched to find the metadata line with
        # batch name (stored in the 'project name' field)
        line = testfile._locate_batch_name_line()

        # THEN should be the expected line number
        assert (line == 2)

    def test_locate_param_line(self):
        # GIVEN some file content representing the typical format of a
        # a sample parameter table, parameters names are listed in the
        # header row (separated by tab), sample data listed in each
        # subsequent row (separated by tab)
        testcontents = ['###TABLE DATA\n',
                        '#############\n',
                        'SampleName\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN content is searched to find the sample table line with
        # parameter names (which always includes 'SampleName')
        line = testfile._locate_param_line()

        # THEN should be the expected line number
        assert (line == 2)

    def test_locate_sample_start_line(self):
        # GIVEN some file content representing the typical format of a
        # a sample parameter table, parameters names are listed in the
        # header row (separated by tab), sample data listed in each
        # subsequent row (separated by tab)
        testcontents = ['###TABLE DATA\n',
                        '#############\n',
                        'SampleName\n',
                        'sample1\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN content is searched to find the sample table line where
        # sample-specific parameters start
        line = testfile._locate_sample_start_line()

        # THEN should be the expected line number
        assert (line == 3)

    def test_get_workflow_name(self):
        # GIVEN some file content representing the typical format of a
        # a metadata table, where data is with each row containing
        # field and value (separated by tab)
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Workflow Name\toptimized_workflow_1\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN content is parsed to retrieve workflow name
        workflow_name = testfile.get_workflow_name()

        # THEN should be expected result
        assert (workflow_name == 'optimized_workflow_1')

    def test_get_batch_name(self):
        # GIVEN some file content representing the typical format of a
        # a metadata table, where data is reported with each row containing
        # field and value (separated by tab)
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Project Name\tDATE_P00-00_FLOWCELL\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN content is parsed to retrieve batch name
        batch_name = testfile.get_batch_name()

        # THEN should be expected result
        assert (batch_name == 'DATE_P00-00_FLOWCELL')

    def test_get_params(self):
        # GIVEN some file content representing the typical format of a
        # a sample parameter table, parameters names are listed in the
        # header row (separated by tab), sample data listed in each
        # subsequent row (separated by tab)
        testcontents = ['###TABLE DATA\n',
                        '#############\n',
                        'SampleName\tmock_in##_::_::_::param_name\n',
                        'sample1\tin_value1\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN contents are parsed to collect details for each parameter
        # in the workflow
        test_params = testfile.get_params()

        # THEN params should be stored in a list of dicts, where each
        # dict should contain the expected parsed details of a parameter;
        # parameters should also be in the original order
        assert (test_params[0] == {'tag': 'SampleName',
                                   'type': 'sample',
                                   'name': 'SampleName'})
        assert (test_params[1] == {'tag': 'mock_in',
                                   'type': 'input',
                                   'name': 'param_name'})

    def test_get_sample_params(self):
        # GIVEN some file content representing the typical format of a
        # a sample parameter table, parameters names are listed in the
        # header row (separated by tab), sample data listed in each
        # subsequent row (separated by tab)
        testcontents = ['###TABLE DATA\n',
                        '#############\n',
                        'SampleName\tmock_in##_::_::_::param_name\n',
                        'sample1\tin_value1\n',
                        'sample2\tin_value2\n']

        # AND an io class object with the file contents stored in the
        # raw field of its data attribute
        testfile = io.WorkflowBatchFile(path='')
        testfile.data['raw'] = testcontents

        # WHEN parameters for one of the sample lines is parsed, and
        # parameter values are mapped to parameter details
        test_sample_params = testfile.get_sample_params(testcontents[3])

        # THEN parameter values for the current sample should be stored
        # in a list of dicts, matching the structure of parsed parameters
        # but with the additional 'value' field
        assert (test_sample_params == [
            {'name': 'SampleName',
             'tag': 'SampleName',
             'type': 'sample',
             'value': 'sample1'},
            {'name': 'param_name',
             'tag': 'mock_in',
             'type': 'input',
             'value': 'in_value1'}
        ])

    def test_parse_submit(self, tmpdir):
        # GIVEN a file containing a typically formatted metadata table,
        # with each row containing field and value (separated by tab)
        # as well as a sample parameter table, where parameters names are
        # listed in the header row (separated by tab), and sample data listed
        # in each subsequent row (separated by tab)
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Workflow Name\toptimized_workflow_1\n',
                        'Project Name\tDATE_P00-00_FLOWCELL\n',
                        '###TABLE DATA\n',
                        '#############\n',
                        'SampleName\tmock_in##_::_::_::param_name\n',
                        'sample1\tin_value1\n',
                        'sample2\tin_value2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object is created for that file with
        # 'state' option set to 'submit'
        testfile = io.WorkflowBatchFile(path=testpath, state='submit')

        # WHEN contents are read and parsed
        test_data = testfile.parse()

        # THEN parsed data should include key-value pairs for all metadata
        # fields, component details for each workflow parameter, and lists
        # of mapped parameter values for each sample
        assert (test_data == {
            'workflow_name': 'optimized_workflow_1',
            'batch_name': 'DATE_P00-00_FLOWCELL',
            'raw': testcontents,
            'parameters': [
                {'name': 'SampleName', 'tag': 'SampleName', 'type': 'sample'},
                {'name': 'param_name', 'tag': 'mock_in', 'type': 'input'}
            ],
            'samples': [
                [
                    {'tag': 'SampleName',
                     'type': 'sample',
                     'name': 'SampleName',
                     'value': 'sample1'},
                    {'tag': 'mock_in',
                     'type': 'input',
                     'name': 'param_name',
                     'value': 'in_value1'}
                ],
                [
                    {'tag': 'SampleName',
                     'type': 'sample',
                     'name': 'SampleName',
                     'value': 'sample2'},
                    {'tag': 'mock_in',
                     'type': 'input',
                     'name': 'param_name',
                     'value': 'in_value2'}
                ]
            ]
        })

    def test_write(self, tmpdir):
        # GIVEN a file containing a typically formatted metadata table,
        # with each row containing field and value (separated by tab)
        # as well as a sample parameter table, where parameters names are
        # listed in the header row (separated by tab), and sample data listed
        # in each subsequent row (separated by tab)
        testcontents = ['###METADATA\n',
                        '#############\n',
                        'Workflow Name\toptimized_workflow_1\n',
                        'Project Name\tDATE_P00-00_FLOWCELL\n',
                        '###TABLE DATA\n',
                        '#############\n',
                        'SampleName\tmock_in##_::_::_::param_name\n',
                        'sample1\tin_value1\n',
                        'sample2\tin_value2\n']
        testpath = mockstringfile(''.join(testcontents), tmpdir)

        # AND an io class object is created for that file with
        # 'state' option set to 'submit'
        testfile = io.WorkflowBatchFile(path=testpath, state='submit')

        # AND a new temporary file object
        outfile = tmpdir.join("newfile")

        # WHEN contents are read, parsed, and written to a new file
        testfile.write(str(outfile))

        # THEN contents of the new file should match expected results
        assert (outfile.readlines() == testcontents)

