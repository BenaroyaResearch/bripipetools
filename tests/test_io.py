import os
import sys

import pytest
import mock

from bripipetools.io import globusgalaxy

TEST_ROOT_DIR = './tests/test-data/'
TEST_GENOMICS_DIR = os.path.join(TEST_ROOT_DIR, 'genomics')
TEST_FLOWCELL_DIR = os.path.join(TEST_GENOMICS_DIR,
                                 'Illumina/150615_D00565_0087_AC6VG0ANXX')
TEST_UNALIGNED_DIR = os.path.join(TEST_FLOWCELL_DIR, 'Unaligned')
TEST_WORKFLOW_DIR = os.path.join(TEST_GENOMICS_DIR, 'galaxy_workflows')

@pytest.fixture(scope="class")
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

    return globusgalaxy.WorkflowBatchFile(path, state=state)

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
