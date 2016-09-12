import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os

import pytest

@pytest.fixture(scope='class')
def mock_genomics_server(request):
    logger.info(("[setup] mock 'genomics' server, connect "
                 "to mock 'genomics' server"))
    run_id = '150615_D00565_0087_AC6VG0ANXX'
    mock_genomics_root = './tests/test-data/'
    mock_genomics_path = os.path.join(mock_genomics_root, 'genomics')
    mock_flowcell_path = os.path.join(mock_genomics_path, 'Illumina', run_id)
    mock_unaligned_path = os.path.join(mock_flowcell_path, 'Unaligned')
    mock_batch_submit_path = os.path.join(mock_flowcell_path,
                                          'globus_batch_submission')
    mock_workflow_batch_file = os.path.join(
        mock_flowcell_path, 'globus_batch_submission',
        ("160412_P109-1_P14-12_C6VG0ANXX_"
         "optimized_truseq_unstrand_sr_grch38_v0.1_complete.txt"))
    mock_processed_project_path = os.path.join(
        mock_flowcell_path, 'Project_P14-12Processed_160412')
    mock_metrics_path = os.path.join(mock_processed_project_path, 'metrics')
    mock_picard_markdups_file = os.path.join(
        mock_metrics_path, 'lib7294_C6VG0ANXX_picard_markdups_metrics.html')
    mock_picard_align_file = os.path.join(
        mock_metrics_path, 'lib7294_C6VG0ANXX_picard_align_metrics.html')
    mock_picard_rnaseq_file = os.path.join(
        mock_metrics_path, 'lib7294_C6VG0ANXX_picard_rnaseq_metrics.html')

    data = {'run_id': run_id,
            'genomics_root': mock_genomics_root,
            'genomics_path': mock_genomics_path,
            'flowcell_path': mock_flowcell_path,
            'unaligned_path': mock_unaligned_path,
            'project_p14_12': 'P14-12-23221204',
            'project_p109_1': 'P109-1-21113094',
            'lib7293': 'lib7293-25920016',
            'lib7293_fastq': 'MXU01-CO072_S1_L001_R1_001.fastq.gz',
            'batch_submit_path': mock_batch_submit_path,
            'workflowbatch_file': mock_workflow_batch_file,
            'batch_name': '160412_P109-1_P14-12_C6VG0ANXX',
            'processed_project_path': mock_processed_project_path,
            'metrics_path': mock_metrics_path,
            'picard_markdups_file': mock_picard_markdups_file,
            'picard_align_file': mock_picard_align_file,
            'picard_rnaseq_file': mock_picard_rnaseq_file}
    def fin():
        logger.info(("[teardown] mock 'genomics' server, disconnect "
                     "from mock 'genomics' server"))
    request.addfinalizer(fin)
    return data
