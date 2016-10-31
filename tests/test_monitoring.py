import logging
import re

import pytest

from bripipetools import monitoring

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(
    scope='module',
    params=[{'runnum': r, 'batchnum': b}
            for r in range(1)
            for b in range(2)]
)
def testbatch(request, mock_genomics_server):
    # GIVEN processing data for one of 2 example batches from a flowcell run
    runs = mock_genomics_server['root']['genomics']['illumina']['runs']
    rundata = runs[request.param['runnum']]
    batches = rundata['submitted']['batches']
    yield batches[request.param['batchnum']]


@pytest.fixture(scope='module')
def testprojects(request, mock_genomics_server):
    # GIVEN processing data for one of 3 example projects from a flowcell run
    rundata = mock_genomics_server['root']['genomics']['illumina']['runs'][0]
    projects = rundata['processed']['projects']
    logger.debug("[setup] test projects data")

    yield projects
    logger.debug("[teardown] test projects data")


class TestWorkflowBatchMonitor:
    @pytest.fixture(
        scope='class'
    )
    def testmonitordata(self, mock_genomics_server, testbatch, testprojects):
        # GIVEN a WorkflowBatchMonitor for a processing batch
        logger.debug("[setup] WorkflowBatchMonitor test instance")

        testmonitor = monitoring.WorkflowBatchMonitor(
            workflowbatch_file=testbatch['path'],
            genomics_root=mock_genomics_server['root']['path'])

        # AND output file data for projects processed in the current
        # workflow batch
        projectdata = [p for p in testprojects
                       for batch_p in testbatch['projects']
                       if re.search(batch_p, p['path'])]

        yield testmonitor, testbatch, projectdata
        logger.debug("[teardown] WorkflowBatchMonitor test instance")

    def test_get_outputs(self, testmonitordata):
        # (GIVEN)
        testmonitor, batchdata, projectdata = testmonitordata

        # WHEN expected output files are collected for the workflow batch,
        # based on the parameters for each sample with type 'output'
        testoutputs = testmonitor._get_outputs()

        # THEN each sample should have the expected number of outputs
        assert(all(len(sampleoutputs) == batchdata['num_outputs']
                   for sampleoutputs in testoutputs))

    def test_clean_output_paths(self, testmonitordata, mock_genomics_server):
        # (GIVEN)
        testmonitor, batchdata, projectdata = testmonitordata

        # AND a mock list of outputs with expected format
        outputs = [{'output1': '/mockroot/genomics/path-to-output1',
                    'output2': '/mockroot/genomics/path-to-output2'},
                   {'output1': '/mockroot/genomics/path-to-output1',
                    'output2': '/mockroot/genomics/path-to-output2'}]

        # WHEN the root of each output file path (i.e., the top level
        # directory containing 'genomics') is replaced with the current
        # 'genomics' root for the system
        testoutputs = testmonitor._clean_output_paths(outputs)

        # THEN each output file path should have the expected 'genomics' root
        root_regex = re.compile('^{}genomics/'.format(
            mock_genomics_server['root']['path']
        ))
        assert(all(root_regex.search(path)
                   for sampleoutputs in testoutputs
                   for path in sampleoutputs.values()))

    def test_check_outputs(self, testmonitordata):
        # (GIVEN)
        testmonitor, batchdata, projectdata = testmonitordata

        # WHEN the status of each output file in the workflow batch is
        # checked based on presence and size
        outputstatus = testmonitor.check_outputs()

        # THEN the dict describing status for each output file should include
        # fields for 'exists', 'size', and 'status'; for the test batches on
        # the mock 'genomics' server, FASTQ files should be missing, BAM files
        # should be empty, and all other files should be OK
        assert(all(field in outinfo
                   for field in ['exists', 'size', 'status']
                   for outinfo in outputstatus.values()))
        assert(all(outinfo['status'] == 'missing'
                   for outpath, outinfo in outputstatus.items()
                   if re.search('\.fastq', outpath)))
        assert (all(outinfo['status'] == 'empty'
                    for outpath, outinfo in outputstatus.items()
                    if re.search('\.bam', outpath)))
        assert (all(outinfo['status'] == 'ok'
                    for outpath, outinfo in outputstatus.items()
                    if not re.search('\.(fastq|bam)', outpath)))


