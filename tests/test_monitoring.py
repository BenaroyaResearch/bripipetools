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
    logger.debug(("[setup] test projects data"))

    yield projects
    logger.debug(("[teardown] test projects data"))


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

    def test_init(self, testmonitordata):
        # (GIVEN)
        testmonitor, batchdata, projectdata = testmonitordata

        # WHEN

        # THEN
        assert(hasattr(testmonitor, 'workflowbatch_data'))

    def test_get_outputs(selfself, testmonitordata):
        # (GIVEN)
        testmonitor, batchdata, projectdata = testmonitordata

        # WHEN
        testoutputs = testmonitor._get_outputs()

        # THEN
        assert(all(len(sampleoutputs) == batchdata['num_outputs']
                   for sampleoutputs in testoutputs))

    def test_clean_output_paths(self, testmonitordata):
        # (GIVEN)
        testmonitor, batchdata, projectdata = testmonitordata

        # WHEN
        testoutputs = testmonitor._clean_output_paths()

        # THEN
        assert (all(len(sampleoutputs) == batchdata['num_outputs']
                    for sampleoutputs in testoutputs))
