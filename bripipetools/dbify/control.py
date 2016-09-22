"""
Parse arguments to determine and select appropriate importer class.
"""
import logging
logger = logging.getLogger(__name__)
import re

from . import SequencingImporter, ProcessingImporter

class ImportManager(object):
    """
    Takes an input argument (path) from script or module specifying
    a scope of data to be imported into GenLIMS; selects the
    appropriate importer class and makes insert command available.
    """
    def __init__(self, path, db):
        logger.info("creating an instance of ImportManager")
        logger.debug("...with arguments (path: {}, db: {})"
                     .format(path, db.name))
        self.path = path
        self.db = db
        self._init_importer()

    def _sniff_path(self, path):
        """
        Check path for known patterns and return path type for importer.
        """
        path_types = {
            'flowcell_path': re.compile('Illumina/.*XX$'),
            'workflowbatch_file': re.compile('batch_submission.*\.txt$')
        }
        return [k for k, v in path_types.items()
                if v.search(path.rstrip('/'))][0]

    def _init_importer(self):
        """
        Initialize the appropriate importer for the provided path.
        """
        path_type = self._sniff_path(self.path)
        importer_opts = {
            'flowcell_path': SequencingImporter,
            'workflowbatch_file': ProcessingImporter
        }
        importer = importer_opts[path_type]
        self.importer = importer(path=self.path, db=self.db)

    def run(self):
        """
        Execute the insert method of the selected importer.
        """
        self.importer.insert()
