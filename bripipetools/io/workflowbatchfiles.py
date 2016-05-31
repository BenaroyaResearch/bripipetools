"""
Classes for reading, parsing, and writing workflow batch submit files for
Globus Galaxy.
"""
import os
import sys
import re

class WorkflowBatchFile(object):
    def __init__(self, path, state='template'):
        """
        A parser to map input sample names to expected output files based on a
        completed Globus Galaxy batch submit file.

        :type path: str
        :param path: File path of batch submit file.
        :type state: str
        :param state: String indicating the current state of the batch submit
            file; either `template` or `submit` (if populated with project and
            sample information).
        """
        self.path = path
        self._read_file()

    def _read_file(self):
        """
        Read and store lines from batch submit file.
        """
        path = self.path
        with open(path) as f:
            self.data = f.readlines()

    def _locate_workflow_name_line(self):
        """
        Identify batch file metadata line with name of workflow; return
        line number.
        """
        return [idx for idx, l in enumerate(self.data)
                if 'Workflow Name' in l][0]

    def _locate_batch_name_line(self):
        """
        Identify batch file metadata line with place-holder for project name;
        return line number. Note: batch submissions can include multiple
        projects, so the 'batch name' label is more appropriate.
        """
        return [idx for idx, l in enumerate(self.data)
                if 'Project Name' in l][0]

    def _locate_param_line(self):
        """
        Identify batch file header line with parameter names; return line
        number.
        """
        return [idx for idx, l in enumerate(self.data)
                if 'SampleName' in l][0]

    def _locate_sample_start_line(self):
        """
        Identify batch file line where sample parameter info begins; return
        line number. Note: should immediately follow parameter header line.
        """
        return [idx for idx, l in enumerate(self.data)
                if 'SampleName' in l][0] + 1

    def get_workflow_name(self):
        """
        Return name of workflow for batch submit file.
        """
        workflow_name_line = self.data[self._locate_workflow_name_line()]
        return workflow_name_line.strip().split('\t')[-1]

    def _parse_param(self, param):
        """
        Break parameter into components.
        """
        param_tag = param.split('##')[0]
        if re.search('annotation', param_tag):
            param_type = 'annotation'
        elif re.search('in', param_tag):
            param_type = 'input'
        else:
            param_type = 'output'

        return {'tag': param_tag,
                'type': param_type,
                'name': param.split('::')[-1]}

    def get_params(self):
        """
        Return the parameters defined for the current workflow.

        :rtype: list
        :return: A list of tuples with number (index) and dict with details
        for each parameter.
        """
        param_line = self.data[self._locate_param_line()]
        return [(idx, self._parse_param(p))
                for idx, p in enumerate(param_line.strip().split('\t'))
                if p != 'SampleName']

    def parse(self):
        return {'workflow_name': self.get_workflow_name(),
                'parmeters': self.get_params()}
