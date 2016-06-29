"""
Classes for reading, parsing, and writing workflow batch submit files for
Globus Galaxy.
"""
import os
import sys
import re
from collections import OrderedDict

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
        self.state = state
        self.data = {}
        self._read_file()

    def _read_file(self):
        """
        Read and store lines from batch submit file.
        """
        path = self.path
        with open(path) as f:
            self.data['raw'] = f.readlines()

    def _locate_workflow_name_line(self):
        """
        Identify batch file metadata line with name of workflow; return
        line number.
        """
        return [idx for idx, l in enumerate(self.data['raw'])
                if 'Workflow Name' in l][0]

    def _locate_batch_name_line(self):
        """
        Identify batch file metadata line with place-holder for project name;
        return line number. Note: batch submissions can include multiple
        projects, so the 'batch name' label is more appropriate.
        """
        return [idx for idx, l in enumerate(self.data['raw'])
                if 'Project Name' in l][0]

    def _locate_param_line(self):
        """
        Identify batch file header line with parameter names; return line
        number.
        """
        return [idx for idx, l in enumerate(self.data['raw'])
                if 'SampleName' in l][0]

    def _locate_sample_start_line(self):
        """
        Identify batch file line where sample parameter info begins; return
        line number. Note: should immediately follow parameter header line.
        """
        return [idx for idx, l in enumerate(self.data['raw'])
                if 'SampleName' in l][0] + 1

    def get_workflow_name(self):
        """
        Return name of workflow for batch submit file.
        """
        workflow_name_line = (self.data['raw']
                              [self._locate_workflow_name_line()])
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
        param_line = self.data['raw'][self._locate_param_line()]
        return OrderedDict((idx, self._parse_param(p))
                for idx, p in enumerate(param_line.strip().split('\t'))
                if p != 'SampleName')

    def get_sample_params(self, sample_line):
        """
        Collect the parameter details for each input sample; store the index
        and input for each parameter.

        :type sample_line: str
        :param sample_line: Raw, tab-delimited line of text from workflow
            batch submit file describing the paramaters for a single sample.

        :rtype: list
        :return: A list of dicts, one for each sample.
        """
        parameters_ordered = self.get_params()

        sample_line_parts = sample_line.strip().split('\t')
        sample_parameters = [parameters_ordered[idx]
                             for idx, sp in enumerate(sample_line_parts)
                             if idx > 0]
        for idx, sp in enumerate(sample_line_parts):
            sample_parameters[idx - 1]['value'] = sp
        return sample_parameters

    def parse(self):
        """
        Parse workflow batch file and return dict.
        """
        self.data['workflow_name'] = self.get_workflow_name()
        self.data['parameters'] = [v for k, v in self.get_params().items()]
        if self.state == 'submit':
            sample_lines = self.data['raw'][self._locate_sample_start_line():]
            self.data['samples'] = [self.get_sample_params(l)
                                    for l in sample_lines]
        return self.data
