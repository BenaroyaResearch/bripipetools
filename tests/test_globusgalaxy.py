import os
import sys

import pytest
import mock

from bripipetools.globusgalaxy import postprocessing

@pytest.fixture(scope="class")
def globus_output_manager():
    flowcell_dir = "/Volumes/genomics/Illumina/150615_D00565_0087_AC6VG0ANXX"
    return postprocessing.GlobusOutputManager(flowcell_dir)

class TestGlobusOutputManager:
    def test_init(self):
        assert(globus_output_manager())
        assert('flowcell_dir' in dir(globus_output_manager()))
        assert('batch_submit_dir' in dir(globus_output_manager()))

    def test_select_batch_prompt(self, capsys):
        with mock.patch('__builtin__.raw_input', return_value=""):
            globus_output_manager()._select_batch_prompt()
            out, err = capsys.readouterr()
            assert(err == "Select batch to process: \n")

    def test_select_batch_date_prompt(self, capsys):
        with mock.patch('__builtin__.raw_input', return_value=""):
            globus_output_manager()._select_batch_date_prompt()
            out, err = capsys.readouterr()
            assert(err == "Select date of batch(es) to process: \n")

    def test_select_batches_0(self, capsys):
        with mock.patch('__builtin__.raw_input', return_value="0"):
            assert(globus_output_manager()._select_batches() == 0)
