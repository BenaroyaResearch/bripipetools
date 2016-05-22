"""
Create batch submission instructions for data processing jobs on Globus Galaxy.
"""

import os
import sys

class GlobusSubmitManager(object):
    def __init__(self, flowcell_dir, workflow_dir, endpoint):
        """
        Prepares batch processing parameters (saved in a batch submit file) for
        one or more projects in an RNA-seq flowcell folder.

        :type flowcell_dir: str
        :param flowcell_dir: Path to flowcell folder where raw data (FASTQs) of
            projects to be processed in Globus Galaxy are stored.
        :type workflow_dir: str
        :param workflow_dir: Path to folder where empty/template batch submit
            files are stored for existing Globus Galaxy workflows.
        :endpoint: str
        :param endpoint: Globus endpoint where input data is stored and outputs
            are to be sent.
        """

        self.flowcell_dir = flowcell_dir
        self.workflow_dir = workflow_dir
        self.endpoint = endpoint
