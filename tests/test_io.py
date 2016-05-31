import os
import sys

import pytest
import mock

from bripipetools.io import workflowbatchfiles

TEST_ROOT_DIR = './tests/test-data/'
TEST_GENOMICS_DIR = os.path.join(TEST_ROOT_DIR, 'genomics')
TEST_FLOWCELL_DIR = os.path.join(TEST_GENOMICS_DIR,
                                 'Illumina/150615_D00565_0087_AC6VG0ANXX')
TEST_UNALIGNED_DIR = os.path.join(TEST_FLOWCELL_DIR, 'Unaligned')
TEST_WORKFLOW_DIR = os.path.join(TEST_GENOMICS_DIR, 'galaxy_workflows')

@pytest.fixture(scope="class")
def workflow_batch_file():
    path = os.path.join(TEST_WORKFLOW_DIR,
                        'nextera_sr_grch38_v0.1_complete_plus_trinity.txt')
    return workflowbatchfiles.WorkflowBatchFile(path)

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

    def test_parse_param_annotation(self):
        assert(workflow_batch_file()._parse_param(
            'annotation_refflat##SourceType::SourceName::refflatFile'
            ) == {'tag': 'annotation_refflat',
                  'type': 'annotation',
                  'name': 'refflatFile'})

    def test_parse_param_input(self):
        assert(workflow_batch_file()._parse_param(
            'fastq_in##Param::2373::globus_get_data_flowcell_text::from_endpoint'
            ) == {'tag': 'fastq_in',
                  'type': 'input',
                  'name': 'from_endpoint'})

    def test_parse_param_output(self):
        assert(workflow_batch_file()._parse_param(
            'htseq_metrics_txt_out##Param::2391::globus_send_data::to_path'
            ) == {'tag': 'htseq_metrics_txt_out',
                  'type': 'output',
                  'name': 'to_path'})

    def test_get_params_0(self):
        assert(workflow_batch_file().get_params()[0]
               == (1, {'tag': 'fastq_in',
                       'type': 'input',
                       'name': 'from_endpoint'}))
