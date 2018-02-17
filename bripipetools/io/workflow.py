"""
Class for reading and parsing Galaxy workflow files.
"""
import logging

import json

logger = logging.getLogger(__name__)


class WorkflowFile(object):
    """
    Parser to exported workflow descriptions from Galaxy, stored in
    a JSON-like format with extension `.ga`.
    """
    def __init__(self, path):
        self.path = path
        self.data = {}
        
        self._read_file()

    def _read_file(self):
        """
        Read file into dictionary.
        """
        logger.debug("reading file '{}' to dictionary".format(self.path))
        with open(self.path) as f:
            self.data['raw'] = json.load(f)

    def parse(self):
        """
        Parse workflow file and return dictionary.
        """
        self.get_workflow_name()
        self.get_tool_info()
        return self.data
        
    def get_workflow_name(self):
        """
        Retrieve the workflow name
        """
        self.data['name'] = self.data['raw']['name']
        return self.data['name']
        
    def get_tool_info(self):
        """
        Retrieve tools and versions from a workflow as a dictionary
        """
        steps = self.data['raw']['steps']
            
        self.data['tools'] = {steps[s]['tool_id'] : steps[s]['tool_version'] 
            for s in steps if 
            (steps[s]['tool_id'] is not None) and
            (steps[s]['tool_version'] is not None)}
        return self.data['tools']
