import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
import sys

import pytest

from bripipetools import io

@pytest.mark.usefixtures('mock_genomics_server')
class TestPicardMetricsFile:
    @pytest.fixture(
        scope='class',
        params=[(source, {'runnum': r, 'projectnum': p, 'samplenum': s})
                for r in range(1)
                for p in range(1)
                for s in range(3)
                for source in
                ['picard_align', 'picard_markdups', 'picard_rnaseq']])
    def metricsfiledata(self, request, mock_genomics_server):
        # GIVEN a PicardMetricsFile with mock 'genomics' server path to
        # a metrics file
        filedata = (mock_genomics_server['out_types']['metrics']
                    [request.param[0]])
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param[1]['runnum']]
        projects = rundata['processed']['projects']
        projectdata = projects[request.param[1]['projectnum']]
        sources = projectdata['metrics']['sources']
        sourcedata = sources[request.param[0]]
        samplefile = sourcedata[request.param[1]['samplenum']]

        logger.info("[setup] PicardMetricsFile test instance "
                    "for file type '{}' for sample {}"
                    .format(request.param[0], samplefile['sample']))

        picardmetricsfile = io.PicardMetricsFile(path=samplefile['path'])

        def fin():
            logger.info("[teardown] PicardMetricsFile mock instance")
        request.addfinalizer(fin)
        return (picardmetricsfile, filedata)

    def test_read_file(self, metricsfiledata):
        # (GIVEN)
        metricsfile, _ = metricsfiledata

        logger.info("test `_read_file()`")

        # WHEN the file specified by path is read
        metricsfile._read_file()
        raw_html = metricsfile.data['raw']

        # THEN class should have raw HTML stored in data attribute and raw
        # HTML should be a single string
        assert(raw_html)
        assert(type(raw_html) is str)

    def test_get_table(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_get_table()`")

        # WHEN metrics table is found in raw HTML
        metrics_table = metricsfile._get_table()

        # THEN the first table found should have the expected number of rows
        assert(len(metrics_table) == filedata['raw_len'])

    def test_check_table_format(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_get_table()`")

        # WHEN checking whether table in metrics HTML is long or wide
        table_format = metricsfile._check_table_format()

        # THEN should return the expected format
        assert(table_format == filedata['format'])

    def test_parse_long(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_parse_long()`")

        # WHEN parsing long format table
        metrics = metricsfile._parse_long()

        # THEN should return parsed dict from long-formatted table with
        # expected length
        assert(len(metrics) == filedata['parse_len_long'])

    def test_parse_wide(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_parse_wide()`")

        # WHEN parsing wide format table
        metrics = metricsfile._parse_wide()

        # THEN should return parsed dict from wide-formatted table with
        # expected length
        assert(len(metrics) == filedata['parse_len_wide'])

    def test_parse(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `parse()`")

        # WHEN parsing metrics table
        metrics = metricsfile.parse()

        # THEN should return parsed dict from table with expected length
        assert(len(metrics) == filedata['parse_len'])


@pytest.mark.usefixtures('mock_genomics_server')
class TestTophatStatsFile:
    @pytest.fixture(
        scope='class',
        params=[(source, {'runnum': r, 'projectnum': p, 'samplenum': s})
                for r in range(1)
                for p in range(1)
                for s in range(3)
                for source in ['tophat_stats']])

    def metricsfiledata(self, request, mock_genomics_server):
        # GIVEN a TophatStatsFile with mock 'genomics' server path to
        # a metrics file
        filedata = (mock_genomics_server['out_types']['metrics']
                    [request.param[0]])
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param[1]['runnum']]
        projects = rundata['processed']['projects']
        projectdata = projects[request.param[1]['projectnum']]
        sourcedata = projectdata['metrics']['sources'][request.param[0]]
        samplefile = sourcedata[request.param[1]['samplenum']]

        logger.info("[setup] TophatStatsFile test instance "
                    "for file type '{}' for sample {}"
                    .format(request.param[0], samplefile['sample']))

        tophatstatsfile = io.TophatStatsFile(path=samplefile['path'])

        def fin():
            logger.info("[teardown] TophatStatsFile mock instance")
        request.addfinalizer(fin)
        return (tophatstatsfile, filedata)

    def test_read_file(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_read_file()`")

        # WHEN the file specified by path is read
        metricsfile._read_file()
        raw_text = metricsfile.data['raw']

        # THEN class should have raw text stored in data attribute and raw
        # text should be a list of length 5
        assert(raw_text)
        assert(len(raw_text) == filedata['raw_len'])

    def test_parse_lines(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_parse_lines()`")

        # WHEN text lines are parsed into key-value pairs based on column
        metrics = metricsfile._parse_lines()

        # THEN output dictionary should be length 5 and have the correct keys
        assert(len(metrics) == filedata['parse_len'])
        assert(set(metrics.keys()) == set(['fastq_total_reads',
                                           'reads_aligned_sam', 'aligned',
                                           'reads_with_mult_align',
                                           'algn_seg_with_mult_algn']))

    def test_parse(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_parse()`")

        # WHEN file is parsed
        metrics = metricsfile.parse()

        # THEN output dictionary should be length 5
        assert(len(metrics) == filedata['parse_len'])

@pytest.mark.usefixtures('mock_genomics_server')
class TestHtseqMetricsFile:
    @pytest.fixture(
        scope='class',
        params=[(source, {'runnum': r, 'projectnum': p, 'samplenum': s})
                for r in range(1)
                for p in range(1)
                for s in range(3)
                for source in ['htseq']])
    def metricsfiledata(self, request, mock_genomics_server):
        # GIVEN a HtseqMetricsFile with mock 'genomics' server path to
        # a metrics file
        filedata = (mock_genomics_server['out_types']['metrics']
                    [request.param[0]])
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param[1]['runnum']]
        projects = rundata['processed']['projects']
        projectdata = projects[request.param[1]['projectnum']]
        sourcedata = projectdata['metrics']['sources'][request.param[0]]
        samplefile = sourcedata[request.param[1]['samplenum']]

        logger.info("[setup] HtseqMetricsFile test instance "
                    "for file type '{}' for sample {}"
                    .format(request.param[0], samplefile['sample']))

        htseqmetricsfile = io.HtseqMetricsFile(path=samplefile['path'])

        def fin():
            logger.info("[teardown] HtseqMetricsFile mock instance")
        request.addfinalizer(fin)
        return (htseqmetricsfile, filedata)

    def test_read_file(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_read_file()`")

        # WHEN the file specified by path is read
        metricsfile._read_file()
        raw_text = metricsfile.data['raw']

        # THEN class should have raw text stored in data attribute and raw
        # text should be a list of length 5
        assert(raw_text)
        assert(len(raw_text) == filedata['raw_len'])

    def test_parse_lines(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_parse_lines()`")

        # WHEN text lines are parsed into key-value pairs based on column
        metrics = metricsfile._parse_lines()

        # THEN output dictionary should be length 5 and have the correct keys
        assert(len(metrics) == filedata['parse_len'])
        assert(set(metrics.keys()) == set(['no_feature', 'ambiguous',
                                           'too_low_aQual', 'not_aligned',
                                           'alignment_not_unique']))

    def test_parse(self, metricsfiledata):
        # (GIVEN)
        metricsfile, filedata = metricsfiledata

        logger.info("test `_parse()`")

        # WHEN file is parsed
        metrics = metricsfile.parse()

        # THEN output dictionary should be length 5
        assert(len(metrics) == filedata['parse_len'])


@pytest.mark.usefixtures('mock_genomics_server')
class TestHtseqCountsFile:
    @pytest.fixture(
        scope='class',
        params=[(source, {'runnum': r, 'projectnum': p, 'samplenum': s})
                for r in range(1)
                for p in range(1)
                for s in range(3)
                for source in ['htseq']])
    def countsfiledata(self, request, mock_genomics_server):
        # GIVEN a HtseqCountsFile with mock 'genomics' server path to
        # a counts file
        filedata = (mock_genomics_server['out_types']['counts']
                    [request.param[0]])
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param[1]['runnum']]
        projects = rundata['processed']['projects']
        projectdata = projects[request.param[1]['projectnum']]
        sourcedata = projectdata['counts']['sources'][request.param[0]]
        samplefile = sourcedata[request.param[1]['samplenum']]

        logger.info("[setup] HtseqCountsFile test instance "
                    "for file type '{}' for sample {}"
                    .format(request.param[0], samplefile['sample']))

        htseqcountsfile = io.HtseqCountsFile(path=samplefile['path'])

        def fin():
            logger.info("[teardown] HtseqCountsFile mock instance")
        request.addfinalizer(fin)
        return (htseqcountsfile, filedata)

    def test_read_file(self, countsfiledata):
        # (GIVEN)
        countsfile, filedata = countsfiledata

        logger.info("test `_read_file()`")

        # WHEN the file specified by path is read
        countsfile._read_file()
        counts_df = countsfile.data['raw']

        # THEN class should have counts stored in a data frame with 100 rows
        # and two columns
        assert(len(counts_df) == filedata['raw_len'])
        assert(len(counts_df.columns) == 2)


@pytest.mark.usefixtures('mock_genomics_server')
class TestFastQCFile:
    @pytest.fixture(
        scope='class',
        params=[(source, {'runnum': r, 'projectnum': p, 'samplenum': s})
                for r in range(1)
                for p in range(1)
                for s in range(3)
                for source in ['fastqc']])
    def qcfiledata(self, request, mock_genomics_server):
        # GIVEN a FastQCFile with mock 'genomics' server path to
        # a QC file
        filedata = (mock_genomics_server['out_types']['qc']
                    [request.param[0]])
        runs = mock_genomics_server['root']['genomics']['illumina']['runs']
        rundata = runs[request.param[1]['runnum']]
        projects = rundata['processed']['projects']
        projectdata = projects[request.param[1]['projectnum']]
        sourcedata = projectdata['qc']['sources'][request.param[0]]
        samplefile = sourcedata[request.param[1]['samplenum']]

        logger.info("[setup] HtseqCountsFile test instance "
                    "for file type '{}' for sample {}"
                    .format(request.param[0], samplefile['sample']))

        fastqcfile = io.FastQCFile(path=samplefile['path'])

        def fin():
            logger.info("[teardown] FastQCFile mock instance")
        request.addfinalizer(fin)
        return (fastqcfile, samplefile, filedata)

    def test_read_file(self, qcfiledata):
        # (GIVEN)
        qcfile, samplefile, filedata = qcfiledata

        logger.info("test `_read_file()`")

        # WHEN the file specified by path is read
        qcfile._read_file()
        raw_text = qcfile.data['raw']

        # THEN class should have raw text stored in data attribute and raw
        # text should be a list of length 5
        assert(raw_text)
        assert(len(raw_text) == samplefile['num_lines'])

    def test_clean_header(self, qcfiledata):
        # (GIVEN)
        qcfile, _, _ = qcfiledata

        logger.info("test `_clean_header()`")

        # WHEN header is cleaned of extra characters and converted to
        # snake case

        # THEN cleaned header should match expected result
        assert(qcfile._clean_header('>>HEADER One') == 'header_one')
        assert(qcfile._clean_header('#HEADER Two') == 'header_two')

    def test_locate_sections(self, qcfiledata):
        # (GIVEN)
        qcfile, samplefile, filedata = qcfiledata

        logger.info("test `_locate_sections()`")

        # WHEN sections are located in the file
        sections = qcfile._locate_sections()

        # THEN should be dictionary of length 12 with correct structure
        assert(len(sections) == 12)
        assert(sections['basic_statistics'] == (1, 10))

    def test_get_section_status(self, qcfiledata):
        # (GIVEN)
        qcfile, samplefile, filedata = qcfiledata

        logger.info("test `_get_section_status()`")

        # WHEN section header line is parsed to retrieve status
        (section_name, section_status) = qcfile._get_section_status(
            'basic_statistics', (1, 10))

        # THEN should return a tuple with the expected status
        assert((section_name, section_status) == ('basic_statistics', 'pass'))

    def test_parse_section_table(self, qcfiledata):
        # (GIVEN)
        qcfile, samplefile, filedata = qcfiledata

        logger.info("test `_parse_section_table()`")

        # WHEN a table of key-value pairs within a section is parsed
        section_data = qcfile._parse_section_table((1, 10))

        # THEN should return a list of expected length
        assert(len(section_data) == 7)

    def test_parse(self, qcfiledata):
        # (GIVEN)
        qcfile, samplefile, filedata = qcfiledata

        logger.info("test `parse()`")

        # WHEN FastQC file is parsed
        fastqcdata = qcfile.parse()

        # THEN should return a dictionary of expected length
        assert(isinstance(fastqcdata, dict))
        assert(len(fastqcdata) == 20)

    def test_parse_overrepresented_seqs(self, qcfiledata):
        # (GIVEN)
        qcfile, samplefile, filedata = qcfiledata

        logger.info("test `parse_overrepresented_seqs()`")

        # WHEN FastQC file is parsed and overrepresented sequences are present
        overrepseqs = qcfile.parse_overrepresented_seqs()

        # THEN should return a list of dictionaries with overrepresented
        # sequence info
        assert(isinstance(overrepseqs, list))
        assert(len(overrepseqs) == samplefile['num_overrep_seqs'])
        if samplefile['num_overrep_seqs']:
            assert(isinstance(overrepseqs[0], dict))
            assert(len(overrepseqs[0]) == 4)


# TODO: clean up old testing setup for workflow batch file IO!

TEST_ROOT_DIR = './tests/test-data/'
TEST_GENOMICS_DIR = os.path.join(TEST_ROOT_DIR, 'genomics')
TEST_FLOWCELL_DIR = os.path.join(TEST_GENOMICS_DIR,
                                 'Illumina/150615_D00565_0087_AC6VG0ANXX')
TEST_UNALIGNED_DIR = os.path.join(TEST_FLOWCELL_DIR, 'Unaligned')
TEST_WORKFLOW_DIR = os.path.join(TEST_GENOMICS_DIR, 'galaxy_workflows')

@pytest.fixture(scope='class')
def workflow_batch_file(state='template', path=None):
    if path is None:
        if state == "template":
            path = os.path.join(TEST_WORKFLOW_DIR,
                                'nextera_sr_grch38_v0.1_complete_plus_trinity.txt')
        else:
            path = os.path.join(TEST_FLOWCELL_DIR,
                    'globus_batch_submission',
                    ('160929_P109-1_P14-12_C6VG0ANXX_'
                     'optimized_truseq_unstrand_sr_grch38_v0.1_complete.txt'))

    return io.WorkflowBatchFile(path, state=state)

class TestWorkflowBatchFile:
    def test_init(self):
        assert(workflow_batch_file())
        assert('path' in dir(workflow_batch_file()))
        assert('data' in dir(workflow_batch_file()))

    def test_locate_workflow_name_line(self):
        assert(workflow_batch_file()._locate_workflow_name_line()
               == 29)

    def test_locate_batch_name_line(self):
        assert(workflow_batch_file()._locate_batch_name_line()
               == 31)

    def test_locate_param_line(self):
        assert(workflow_batch_file()._locate_param_line()
               == 37)

    def test_locate_sample_start_line(self):
        assert(workflow_batch_file()._locate_sample_start_line()
               == 38)

    def test_get_workflow_name(self):
        assert(workflow_batch_file().get_workflow_name()
               == 'nextera_sr_grch38_v0.1_complete_plus_trinity')

    def test_get_batch_name(self):
        assert(workflow_batch_file(state='submit').get_batch_name()
               == '160929_P109-1_P14-12_C6VG0ANXX')

    def test_parse_param_samplename(self):
        assert(workflow_batch_file()
               ._parse_param('SampleName')
               == {'tag': 'SampleName',
                   'type': 'sample',
                   'name': 'SampleName'})

    def test_parse_param_annotation(self):
        assert(workflow_batch_file()
               ._parse_param('annotation_tag##_::_::param_name')
               == {'tag': 'annotation_tag',
                   'type': 'annotation',
                   'name': 'param_name'})

    def test_parse_param_input(self):
        assert(workflow_batch_file()
               ._parse_param('in_tag##_::_::_::param_name')
               == {'tag': 'in_tag',
                   'type': 'input',
                   'name': 'param_name'})

    def test_parse_param_output(self):
        assert(workflow_batch_file()
               ._parse_param('out_tag##_::_::_::param_name')
               == {'tag': 'out_tag',
                   'type': 'output',
                   'name': 'param_name'})

    def test_get_params_1(self):
        assert(workflow_batch_file().get_params()[1]
               == {'tag': 'fastq_in',
                   'type': 'input',
                   'name': 'from_endpoint'})

    def test_get_sample_params(self):
        wbf = workflow_batch_file()
        assert(wbf.get_sample_params('lib6839_C6VG0ANXX\tjeddy#srvgridftp01\n')
               == [{'tag': 'SampleName',
                    'type': 'sample',
                    'name': 'SampleName',
                    'value': 'lib6839_C6VG0ANXX'},
                   {'tag': 'fastq_in',
                    'type': 'input',
                    'name': 'from_endpoint',
                    'value': 'jeddy#srvgridftp01'}])

    def test_parse_template(self):
        wbf = workflow_batch_file()
        assert(wbf.parse()['workflow_name']
               == 'nextera_sr_grch38_v0.1_complete_plus_trinity')
        assert(wbf.parse()['parameters'][1]
               == {'tag': 'fastq_in',
                   'type': 'input',
                   'name': 'from_endpoint'})

    def test_parse_submit(self):
        wbf = workflow_batch_file(state='submit')
        assert(wbf.state == 'submit')
        assert(wbf.parse()['workflow_name']
               == 'optimized_truseq_unstrand_sr_grch38_v0.1_complete')
        assert(wbf.parse()['parameters'][1]
               == {'tag': 'fastq_in',
                   'type': 'input',
                   'name': 'from_endpoint'})
        assert(wbf.parse()['samples'][0][1]
               == {'tag': 'fastq_in',
                   'type': 'input',
                   'name': 'from_endpoint',
                   'value': 'jeddy#srvgridftp01'})
        assert(len(wbf.parse()['parameters'])
               == len(wbf.parse()['samples'][0]))

    def test_write_submit(self):
        wbf = workflow_batch_file(state='submit')
        path = os.path.join(TEST_FLOWCELL_DIR,
                'globus_batch_submission', 'foo.txt')
        wbf.write(path)
        assert(workflow_batch_file(path).data['raw'] == wbf.data['raw'])
