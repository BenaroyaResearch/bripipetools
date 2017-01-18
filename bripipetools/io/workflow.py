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
        self._read_file()
        return self.data['raw']
