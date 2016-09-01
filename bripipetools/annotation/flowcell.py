
import os
import re
import bripipetools.model as docs
from bripipetools.util import files

class FlowcellRunAnnotator(object):
    """
    Identifies, stores, and updates information about a flowcell run.
    """
    def __init__(self, run_id, genomics_root=None):
        self.run_id = run_id
        self.flowcellrun = self._init_flowcellrun(run_id)
        if genomics_root is None:
            self.genomics_root = os.path.join(
                os.path.abspath(self._get_genomics_root()),
                'genomics'
            )
        else:
            self.genomics_root = os.path.join(genomics_root, 'genomics')

    def _get_genomics_root(self):
        """
        Locate the root directory preceding 'genomics' in the system
        path.
        """
        return files.locate_root_folder('genomics')

    def _init_flowcellrun(self, run_id):
        """
        Try to retrieve data for the flowcell run from GenLIMS; if
        unsuccessful, create new ``FlowcellRun`` object.
        """
        try:
            return genlims.get_run(_id=run_id)
        except:
            return docs.FlowcellRun(_id=run_id)

    def _get_flowcell_path(self):
        """
        Find path to flowcell folder on the server.
        """
        illumina_root = os.path.join(self.genomics_root, 'Illumina')
        return [os.path.join(illumina_root, p)
                for p in os.listdir(illumina_root)
                if p == self.flowcellrun._id][0]

    # def _get_unaligned_folder(self):
