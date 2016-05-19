"""
Organize, format, and clean up outputs from a Globus Galaxy processing run.
"""

import os

from bripipetools.globusgalaxy import curation

class GlobusOutputManager(object):
    def __init__(self, flowcell_dir):
        """
        For one or more batches processed from a given flowcell, this object
        controls the curation, stitching, and cleanup of all output files.
        """
        self.flowcell_dir = flowcell_dir
        self.batch_submit_dir = os.path.join(self.flowcell_dir,
                                             "globus_batch_submission")

    def _select_batches(self):
        """
        Select and store path to batch submit file(s) from among list of
        batches found in the 'globus_batch_submission' folder. 
        """
        # TODO: add multi-select
        batch_submit_dir = self.batch_submit_dir
        batch_files = os.listdir(batch_submit_dir)
        print "\nFound the following Globus Genomics Galaxy batches:"
        for i, d in enumerate(batch_files):
            print "%3d : %s" % (i, d)
        batch_i = raw_input("Select a batch to compile: ")
        batch_file = batch_files[int(batch_i)]

        return [os.path.join(batch_submit_dir, f)
                for f in os.listdir(batch_submit_dir)
                if f.split('_')[0] in batch_files]

    def _select_date_batches(self):
        batch_submit_dir = self.batch_submit_dir
        batch_dates = list(set(f.split('_')[0]
                               for f in os.listdir(batch_submit_dir)))

        print "\nFound Globus Genomics Galaxy batches from the following dates:"
        for i, d in enumerate(batch_dates):
            print "%3d : %s" % (i, d)
        batch_i = raw_input("Select the date of flowcell batches to compile: ")
        batch_date = batch_dates[int(batch_i)]

        return [os.path.join(batch_submit_dir, f)
                for f in os.listdir(batch_submit_dir)
                if f.split('_')[0] in batch_date]
