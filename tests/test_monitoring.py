import logging

import pytest

from bripipetools import monitoring

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


#@pytest.fixture(scope='function')
def mock_batchfile(filename, tmpdir):
    # GIVEN a simplified workflow batch content with protypical contents
    mock_contents = ['###METADATA\n',
                     '#############\n',
                     'Workflow Name\toptimized_workflow_1\n',
                     'Project Name\t161231_P00-00_C00000XX\n',
                     '###TABLE DATA\n',
                     '#############\n',
                     'SampleName\tmock_out##_::_::_::to_path\n',
                     'sample1\t/mnt/bioinformatics/pipeline/out_file1\n',
                     'sample2\t/mnt/bioinformatics/pipeline/out_file2\n']
    mock_file = tmpdir.join(filename)
    mock_file.write(''.join(mock_contents))
    return str(mock_file)


class TestWorkflowBatchMonitor:
    """
    Tests methods for the `WorkflowBatchMonitor` class in the
    `bripipetools.monitoring.workflowbatches` module.
    """
    def test_get_outputs(self, tmpdir):
        # GIVEN a path to a workflow batch file
        mock_filename = '161231_P00-00_C00000XX_workflow-name.txt'
        mock_path = mock_batchfile(mock_filename, tmpdir)

        # AND a monitor object is created for the workflow batch
        monitor = monitoring.WorkflowBatchMonitor(
            workflowbatch_file=mock_path,
            pipeline_root=str(tmpdir)
        )

        # WHEN the list of annotated outputs are retrieved for the
        # workflow batch, grouped as a dict for each sample, with
        # output names and output paths as key-value pairs
        test_outputs = monitor._get_outputs()

        # THEN the outputs should match the expected result
        assert (test_outputs == 
                [{'mock_out': '/mnt/bioinformatics/pipeline/out_file1'},
                 {'mock_out': '/mnt/bioinformatics/pipeline/out_file2'}])

    def test_clean_output_paths(self, tmpdir):
        # GIVEN a path to a workflow batch file
        mock_pipelineroot = tmpdir.mkdir('bioinformatics')
        mock_pipelinedir = mock_pipelineroot.mkdir('pipeline')
        mock_filename = '161231_P00-00_C00000XX_workflow-name.txt'
        mock_path = mock_batchfile(mock_filename, mock_pipelinedir)

        # AND a monitor object is created for the workflow batch
        monitor = monitoring.WorkflowBatchMonitor(
            workflowbatch_file=mock_path,
            pipeline_root=str(mock_pipelineroot)
        )

        # AND a list of annotated outputs in the format returned by
        # the `_get_outputs()` method above
        mock_outputs = [{'mock_out': '/mnt/bioinformatics/pipeline/out_file1'},
                        {'mock_out': '/mnt/bioinformatics/pipeline/out_file2'}]

        # WHEN the 'pipeline' root used during batch processing is
        # replaced with the full path to the 'pipeline' root relative
        # to the current file system
        test_outputs = monitor._clean_output_paths(mock_outputs)

        # THEN the cleaned output paths should match the expected result
        assert (test_outputs
                == [{'mock_out': '{}/out_file1'.format(str(mock_pipelinedir))},
                    {'mock_out': '{}/out_file2'.format(str(mock_pipelinedir))}])

    @pytest.mark.parametrize(
        'mock_status', ['ok', 'empty', 'missing']
    )
    def test_check_outputs(self, tmpdir, mock_status):
        # GIVEN a path to a workflow batch file
        mock_pipelinedir = tmpdir.mkdir('pipeline')
        mock_filename = '161231_P00-00_C00000XX_workflow-name.txt'
        mock_path = mock_batchfile(mock_filename, mock_pipelinedir)

        # AND a monitor object is created for the workflow batch
        monitor = monitoring.WorkflowBatchMonitor(
            workflowbatch_file=mock_path,
            pipeline_root=str(tmpdir)
        )

        # AND a path to 'out_file1', where the file itself is either
        # 'missing' (no file exists), 'empty' (file exists, but size is
        # zero), or 'ok' (file exists and is non-empty
        mock_outfile = mock_pipelinedir.join('out_file1')

        if mock_status in ['ok', 'empty']:
            mock_outfile = mock_pipelinedir.ensure('out_file1')

        if mock_status == 'ok':
            mock_outfile.write('mock_contents')

        # WHEN the status of each output file in the workflow batch is
        # checked based on presence and size
        test_status = monitor.check_outputs()

        # THEN the dict describing status for each output file should include
        # fields for 'exists', 'size', and 'status' and the status for mocked
        # 'out_file1' should match expected result
        assert (all(field in status_fields
                for field in ['exists', 'size', 'status']
                for status_fields in list(test_status.values())))
        assert (test_status[str(mock_outfile)]['status'] == mock_status)



