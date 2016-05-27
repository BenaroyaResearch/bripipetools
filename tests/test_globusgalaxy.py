import os
import sys

import pytest
import mock

# TODO: might be worthwhile to test import, since I'm still changing module
# names occasionally
from bripipetools.globusgalaxy import submission

TEST_ROOT_DIR = './tests/test-data/'
TEST_GENOMICS_DIR = os.path.join(TEST_ROOT_DIR, 'genomics')
TEST_FLOWCELL_DIR = os.path.join(TEST_GENOMICS_DIR,
                                 'Illumina/150615_D00565_0087_AC6VG0ANXX')
TEST_UNALIGNED_DIR = os.path.join(TEST_FLOWCELL_DIR, 'Unaligned')
TEST_WORKFLOW_DIR = os.path.join(TEST_GENOMICS_DIR, 'galaxy_workflows')

@pytest.fixture(scope="class")
def globus_submit_manager():
    flowcell_dir = TEST_FLOWCELL_DIR
    workflow_dir = TEST_WORKFLOW_DIR
    endpoint = 'jeddy#srvgridftp01'
    return submission.GlobusSubmitManager(flowcell_dir, workflow_dir, endpoint)

class TestGlobusSubmitManager:
    def test_init(self):
        assert(globus_submit_manager())
        assert('flowcell_dir' in dir(globus_submit_manager()))
        assert('workflow_dir' in dir(globus_submit_manager()))
        assert('endpoint' in dir(globus_submit_manager()))
        assert('projects' in dir(globus_submit_manager()))
        assert('workflows' in dir(globus_submit_manager()))

    def test_set_projects(self):
        gsm = globus_submit_manager()
        gsm._set_projects()
        assert(isinstance(gsm.projects, list))
        assert(len(gsm.projects) == 8)
        assert(gsm.projects[0] ==
               {'name': 'P109-1-21113094',
                'path': os.path.join(TEST_UNALIGNED_DIR,
                                     'P109-1-21113094')})

    def test_set_workflows(self):
        gsm = globus_submit_manager()
        gsm._set_workflows()
        assert(isinstance(gsm.workflows, list))
        assert(len(gsm.workflows) == 6)
        assert(gsm.workflows[0] ==
               {'name': 'nextera_sr_grch38_v0.1_complete.txt',
                'path': os.path.join(TEST_WORKFLOW_DIR,
                                     'nextera_sr_grch38_v0.1_complete.txt'),
                'projects': []})

    def test_add_workflow_project_association(self):
        assert((globus_submit_manager()
                ._add_workflow_project_association({'name': 'foo'},
                                                   {'name': 'bar'})) ==
               {'name': 'foo',
                'projects': [{'name': 'bar'}]})

    def test_format_project_choice(self):
        assert((globus_submit_manager()
                ._format_project_choice(
                {'name': 'foo'}, [{'projects': [{'name': 'foo'}]}]) ==
               'foo [0]'))

    def test_select_project_0(self):
        with mock.patch('__builtin__.raw_input', return_value="0"):
            assert(globus_submit_manager()._select_project() ==
                   {'name': 'P109-1-21113094',
                    'path': os.path.join(TEST_UNALIGNED_DIR,
                                         'P109-1-21113094')})

    def test_select_workflow_0(self):
        with mock.patch('__builtin__.raw_input', return_value="0"):
            assert(globus_submit_manager()._select_workflow() ==
                   {'name': 'nextera_sr_grch38_v0.1_complete.txt',
                    'path': os.path.join(TEST_WORKFLOW_DIR,
                                         'nextera_sr_grch38_v0.1_complete.txt'),
                    'projects': []})

    # def test_update_batch_workflows_0_0_break(self):
    #     with mock.patch('__builtin__.raw_input', side_effect=iter(["0", ""])):
    #         gsm = globus_submit_manager()
    #         assert(gsm._update_batch_workflows() is None)
    #         # print(gsm.workflows[0]['projects'])
    #         # assert(gsm.workflows[0]['projects'])


from bripipetools.globusgalaxy import postprocessing

@pytest.fixture(scope="class")
def globus_output_manager(batch_list='foo,bar'):
    flowcell_dir = TEST_FLOWCELL_DIR
    return postprocessing.GlobusOutputManager(flowcell_dir, batch_list)

class TestGlobusOutputManager:
    def test_init_w_batch_list(self):
        assert(globus_output_manager())
        assert('flowcell_dir' in dir(globus_output_manager()))
        assert('batch_submit_dir' in dir(globus_output_manager()))
        assert(globus_output_manager().batch_list ==
               [os.path.join(TEST_FLOWCELL_DIR,
                             'globus_batch_submission/foo'),
                os.path.join(TEST_FLOWCELL_DIR,
                             'globus_batch_submission/bar')])

    def test_select_batches_0(self):
        with mock.patch('__builtin__.raw_input', return_value="0"):
            assert(globus_output_manager()._select_batches() ==
                   [('160216_P109-1_P14-12_C6VG0ANXX_'
                     'optimized_truseq_unstrand_sr_grch38_v0.1_complete.txt')])

    def test_select_date_batches_1(self):
        with mock.patch('__builtin__.raw_input', return_value="1"):
            assert(globus_output_manager()._select_date_batches() ==
                   [('160411_P43-12_C6VG0ANXX_'
                     'optimized_nextera_sr_grch38_v0.1_complete.txt')])

    def test_get_batch_file_path_dummy_file(self):
        assert(globus_output_manager()._get_batch_file_path('dummy.txt') ==
               os.path.join(TEST_FLOWCELL_DIR,
                            'globus_batch_submission/dummy.txt'))

    def test_get_select_func_each(self):
        assert(globus_output_manager()._get_select_func('each').__name__ ==
               '_select_batches')

    def test_get_select_func_date(self):
        assert(globus_output_manager()._get_select_func('date').__name__ ==
               '_select_date_batches')

    def test_init_no_batch_list(self):
        with mock.patch('__builtin__.raw_input', return_value="0"):
            assert(globus_output_manager(batch_list=None).batch_list ==
                   [os.path.join(TEST_FLOWCELL_DIR,
                        'globus_batch_submission/'
                        '160216_P109-1_P14-12_C6VG0ANXX_'
                        'optimized_truseq_unstrand_sr_grch38_v0.1_complete.txt')])

    def test_curate_batches_dummy(self):
        with pytest.raises(IOError):
            assert(globus_output_manager().curate_batches())
