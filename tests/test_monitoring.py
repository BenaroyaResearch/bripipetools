import logging

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


class TestWorkflowBatchMonitor:
    @pytest.fixture(
        scope='class'
    )
    def testmonitordata(self, mock_genomics_server, testbatch):
        # GIVEN a WorkflowBatchMonitor for a processing batch
        logger.info("[setup] WorkflowBatchMonitor test instance")

        testmonitor = monitoring.WorkflowBatchMonitor(
            workflowbatch_file=testbatch['path'],
            genomics_root=mock_genomics_server['root']['path'])

        yield testmonitor
        logger.info("[teardown] WorkflowBatchMonitor mock instance")

    def test_init(self, testmonitordata):
        # (GIVEN)
        testmonitor = testmonitordata
        assert(hasattr(testmonitor, 'workflowbatch_data'))