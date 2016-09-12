import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
import sys

import pytest

from bripipetools import io

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
                    ('160216_P109-1_P14-12_C6VG0ANXX_'
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
               == '160216_P109-1_P14-12_C6VG0ANXX')

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


@pytest.mark.usefixtures('mock_genomics_server')
class TestPicardMetrics:
    @pytest.fixture(scope='class',
                    params=[('picard_markdups_file', {'len': 24,
                                                      'format': 'long',
                                                      'len_long': 9,
                                                      'len_wide': 0,
                                                      'len_parse': 9}),
                            ('picard_align_file', {'len': 56,
                                                   'format': 'long',
                                                   'len_long': 24,
                                                   'len_wide': 0,
                                                   'len_parse': 24}),
                            ('picard_rnaseq_file', {'len': 215,
                                                    'format': 'wide',
                                                    'len_long': 0,
                                                    'len_wide': 22,
                                                    'len_parse': 22})
                            ])
    def metricsfiledata(self, request, mock_genomics_server):
        logger.info("[setup] PicardMetricsFile test instance "
                    "for file type '{}'".format(request.param))

        # GIVEN a PicardMetricsFile with mock 'genomics' server path to
        # a metrics file
        picardmetricsfile = io.PicardMetricsFile(
            path=mock_genomics_server[request.param[0]]
        )
        def fin():
            logger.info("[teardown] PicardMetricsFile mock instance")
        request.addfinalizer(fin)
        return (picardmetricsfile, request.param[1])

    def test_read_file(self, metricsfiledata):
        logger.info("test `_read_file()`")
        (metricsfile, _) = metricsfiledata

        # WHEN the file specified by path is read
        metricsfile._read_file()
        raw_html = metricsfile.data['raw']

        # THEN class should have raw HTML stored in data attribute and raw
        # HTML should be a single string
        assert(raw_html)
        assert(type(raw_html) == str)

    def test_get_table(self, metricsfiledata):
        logger.info("test `_get_table()`")
        (metricsfile, expected_output) = metricsfiledata

        # WHEN metrics table is found in raw HTML
        metrics_table = metricsfile._get_table()

        # THEN the first table found should have the expected number of rows
        assert(len(metrics_table[0]) == expected_output['len'])
    #
    def test_check_table_format(self, metricsfiledata):
        logger.info("test `_get_table()`")
        (metricsfile, expected_output) = metricsfiledata

        # WHEN checking whether table in metrics HTML is long or wide
        table_format = metricsfile._check_table_format()

        # THEN should return the expected format
        assert(table_format == expected_output['format'])

    def test_parse_long(self, metricsfiledata):
        logger.info("test `_parse_long()`")
        (metricsfile, expected_output) = metricsfiledata

        # WHEN parsing long format table
        metrics = metricsfile._parse_long()

        # THEN should return parsed dict from long-formatted table with
        # expected length
        assert(len(metrics) == expected_output['len_long'])

    def test_parse_wide(self, metricsfiledata):
        logger.info("test `_parse_wide()`")
        (metricsfile, expected_output) = metricsfiledata

        # WHEN parsing wide format table
        metrics = metricsfile._parse_wide()

        # THEN should return parsed dict from wide-formatted table with
        # expected length
        assert(len(metrics) == expected_output['len_wide'])

    def test_parse(self, metricsfiledata):
        logger.info("test `parse()`")
        (metricsfile, expected_output) = metricsfiledata

        # WHEN parsing metrics table
        metrics = metricsfile.parse()

        # THEN should return parsed dict from table with expected length
        assert(len(metrics) == expected_output['len_parse'])


@pytest.mark.usefixtures('mock_genomics_server')
class TestTophatStatsFile:
    @pytest.fixture(scope='class')
    def metricsfile(self, request, mock_genomics_server):
        logger.info("[setup] TophatStatsFile test instance")

        # GIVEN a TophatStatsFile with mock 'genomics' server path to
        # a metrics file
        tophatstatsfile = io.TophatStatsFile(
            path=mock_genomics_server['tophat_stats_file']
        )
        def fin():
            logger.info("[teardown] TophatStatsFile mock instance")
        request.addfinalizer(fin)
        return tophatstatsfile

    def test_read_file(self, metricsfile):
        logger.info("test `_read_file()`")

        # WHEN the file specified by path is read
        metricsfile._read_file()
        raw_text = metricsfile.data['raw']

        # THEN class should have raw text stored in data attribute and raw
        # text should be a list of length 5
        assert(raw_text)
        assert(len(raw_text) == 5)

    def test_parse_lines(self, metricsfile):
        logger.info("test `_parse_lines()`")

        # WHEN text lines are parsed into key-value pairs based on column
        metrics = metricsfile._parse_lines()

        # THEN output dictionary should be length 5
        assert(len(metrics) == 5)

    def test_parse(self, metricsfile):
        logger.info("test `_parse()`")

        # WHEN file is parsed
        metrics = metricsfile.parse()

        # THEN output dictionary should be length 5
        assert(len(metrics) == 5)
