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

    def test_init_attr(self):
        assert('flowcell_dir' in dir(globus_output_manager()))
        assert('batch_submit_dir' in dir(globus_output_manager()))
