import logging
import re

import mock
import mongomock
import pytest

from bripipetools import annotation
from bripipetools import submission

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def mock_db():
    # GIVEN a mock_ed version of the TG3 Mongo database
    logger.info(("[setup] mock_ database, connect "
                 "to mock Mongo database"))

    yield mongomock.MongoClient().db
    logger.debug(("[teardown] mock_ database, disconnect "
                  "from mock Mongo database"))


class TestSubmissionBuilder:
    """

    """
    def test_init_annotator(self, mock_db):
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = '/mnt/genomics/Illumina/{}'.format(mock_runid)
        mock_endpoint = 'jeddy#srvgridftp01'

        builder = submission.SubmissionBuilder(
            path=mock_path,
            endpoint=mock_endpoint,
            db=mock_db
        )

        builder._init_annotator()

        assert (type(builder.annotator == annotation.FlowcellRunAnnotator))

    def test_get_workflow_options_for_all_workflows(self, mock_db, tmpdir):
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = '/mnt/genomics/Illumina/{}'.format(mock_runid)
        mock_endpoint = 'jeddy#srvgridftp01'

        mock_workflowdir = tmpdir.mkdir('galaxy_workflows')
        mock_workflows = ['workflow1.txt', 'optimized_workflow1.txt']
        mock_workflowopts = [str(mock_workflowdir.mkdir(w))
                             for w in mock_workflows]
        mock_workflowopts.sort()

        builder = submission.SubmissionBuilder(
            path=mock_path,
            endpoint=mock_endpoint,
            db=mock_db,
            workflow_dir=str(mock_workflowdir)
        )

        test_workflowopts = builder.get_workflow_options(optimized_only=False)

        assert (test_workflowopts == mock_workflowopts)

    def test_get_workflow_options_for_optimized_workflows(self, mock_db,
                                                          tmpdir):
        mock_runid = '161231_INSTID_0001_AC00000XX'
        mock_path = '/mnt/genomics/Illumina/{}'.format(mock_runid)
        mock_endpoint = 'jeddy#srvgridftp01'

        mock_workflowdir = tmpdir.mkdir('galaxy_workflows')
        mock_workflows = ['workflow1.txt', 'optimized_workflow1.txt']
        mock_workflowopts = [str(mock_workflowdir.mkdir(w))
                             for w in mock_workflows
                             if re.search('optimized', w)]
        mock_workflowopts.sort()

        builder = submission.SubmissionBuilder(
            path=mock_path,
            endpoint=mock_endpoint,
            db=mock_db,
            workflow_dir=str(mock_workflowdir)
        )

        test_workflowopts = builder.get_workflow_options()

        assert (test_workflowopts == mock_workflowopts)

    def test_get_projects(self, mock_db, tmpdir):
        # GIVEN a flowcell run ID and an arbitrary root directory,
        # under which a folder exists at 'genomics/Illumina/<run_id>',
        # and that folder contains a subfolder named 'Unaligned'
        mock_id = '161231_INSTID_0001_AC00000XX'
        mock_endpoint = 'jeddy#srvgridftp01'

        # AND the unaligned folder includes multiple project folders
        mock_projects = ['P1-1-11111111', 'P99-99-99999999']
        mock_path = tmpdir.mkdir('genomics').mkdir('Illumina').mkdir(mock_id)
        mock_unaligndir = mock_path.mkdir('Unaligned')
        mock_paths = [mock_unaligndir.mkdir(p) for p in mock_projects]

        builder = submission.SubmissionBuilder(
            path=str(mock_path),
            endpoint=mock_endpoint,
            db=mock_db
        )

        builder._get_project_paths()

        assert (builder.project_paths == mock_paths)

