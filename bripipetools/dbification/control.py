"""
Parse arguments to determine and select appropriate importer class.
"""
import logging
import re

from . import FlowcellRunImporter, WorkflowBatchImporter

logger = logging.getLogger(__name__)


class ImportManager(object):
    """
    Takes an input argument (path) from script or module specifying
    a scope of data to be imported into GenLIMS; selects the
    appropriate importer class and makes insert command available.
    """
    def __init__(self, path, db, run_opts):
        logger.debug("creating `ImportManager` instance")
        logger.debug("...with arguments (path: '{}', db: '{}')"
                     .format(path, db.name))
        self.path = path
        self.db = db
        self.run_opts = run_opts

    def _sniff_path(self):
        """
        Check path for known patterns and return path type for importer.
        """
        path_types = {
            'flowcell_path': re.compile('Illumina/.*((X(X|Y|2|3|F))|(000000000-C[A-Z0-9]{4})|(A[0-9a-zA-Z]+(M5|HV)))$'),
            'workflowbatch_file': re.compile(r'batch_submission.*\.txt$')
        }
        return [k for k, v in list(path_types.items())
                if v.search(self.path.rstrip('/'))][0]

    def _init_importer(self):
        """
        Initialize the appropriate importer for the provided path.
        """
        path_type = self._sniff_path()
        importer_opts = {
            'flowcell_path': FlowcellRunImporter,
            'workflowbatch_file': WorkflowBatchImporter
        }
        importer = importer_opts[path_type]
        self.importer = importer(path=self.path, db=self.db, 
                                 run_opts=self.run_opts)

    def run(self, collections='all'):
        """
        Execute the insert method of the selected importer.
        """
        self._init_importer()
        self.importer.insert(collections)
