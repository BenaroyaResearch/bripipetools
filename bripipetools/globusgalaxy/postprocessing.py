"""
Organize, format, and clean up outputs from a Globus Galaxy processing run.
"""

import os
import re

from bripipetools.util import ui
from bripipetools.globusgalaxy import curation

class GlobusOutputManager(object):
    def __init__(self, flowcell_dir, batch_list=None, select_type='each'):
        """
        For one or more batches processed from a given flowcell, this object
        controls the curation, stitching, and cleanup of all output files.

        :type flowcell_dir: str
        :param flowcell_dir: Path to flowcell folder where outputs of one or
            more Globus Galaxy batch processing jobs should be stored.
        :type batch_list: str
        :param batch_list: Comma-separated list of batches (or single batch),
            as represented by batch submit files, on which to perform curation
            & cleanup operations.
        :type select_type: str
        :param select_type: If list of batches not provided, this argument
            specifies which method to use for interactive selection; options
            should be either 'each' or 'date'.
        """
        self.flowcell_dir = flowcell_dir
        self.batch_submit_dir = os.path.join(self.flowcell_dir,
                                             "globus_batch_submission")

        if batch_list is None:
            batch_list = self._get_select_func(select_type)()
        else:
            batch_list = batch_list.split(',')
        self.batch_list = [self._get_batch_file_path(os.path.basename(f))
                           for f in batch_list]

    def _select_batch_prompt(self):
        """
        Display the command-line prompt for selecting an individual batch file.

        :rtype: str
        :return: String collected from ``raw_input`` in response to the prompt.
        """
        return ui.prompt_raw("Select batch to process: ")

    def _select_batch_date_prompt(self):
        """
        Display command-line prompt for selecting batches by date.

        :rtype: str
        :return: String collected from ``raw_input`` in response to the prompt.
        """
        return ui.prompt_raw("Select date of batch(es) to process: ")

    def _select_batches(self):
        """
        Select and store names of batch submit file(s) from among list of
        batches found in the 'globus_batch_submission' folder.

        :rtype: list
        :return: A list with the name of the batch file corresponding to user
            command-line selection.
        """
        # TODO: add multi-select
        batch_submit_dir = self.batch_submit_dir
        batch_files = [f for f in os.listdir(batch_submit_dir)
                       if not re.search('^\.', f)]
        print "\nFound the following Globus Genomics Galaxy batches:"
        ui.list_options(batch_files)
        batch_i = ui.input_to_int(self._select_batch_prompt)
        batch_file = batch_files[batch_i]
        return [batch_file]

    def _select_date_batches(self):
        """
        Select and store names of batch submit file(s) corresponding to a
        specified date among batches found in the 'globus_batch_submission'
        folder.

        :rtype: list
        :return: A list with the name of the batch file corresponding to user
            command-line selection.
        """
        batch_submit_dir = self.batch_submit_dir
        batch_dates = list(set(f.split('_')[0]
                               for f in os.listdir(batch_submit_dir)
                               if not re.search('^\.', f)))

        print "\nFound Globus Genomics Galaxy batches from the following dates:"
        ui.list_options(batch_dates)
        batch_i = ui.input_to_int(self._select_batch_date_prompt)
        batch_date = batch_dates[batch_i]

        return [f for f in os.listdir(batch_submit_dir)
                if f.split('_')[0] in batch_date]

    def _get_batch_file_path(self, batch_file_name):
        """
        Return full path for batch file by joining with ``batch_submit_dir``.

        :type batch_file_name: str
        :param batch_file_name: File name for a batch submit file.

        :rtype: str
        :return: Full path to batch file.
        """
        batch_submit_dir = self.batch_submit_dir
        return os.path.join(batch_submit_dir, batch_file_name)

    def _get_select_func(self, select_type):
        """
        Return the appropriate batch selection function based on specified
        selection type.

        :type select_type: str
        :param select_type: Selection method to use: 'each' for selecting
            batches individually, or 'date' to select all batches for a
            specified date.

        :rtype: func
        :return: Bound method, which, when called, interactively prompts user
            to select batches.
        """
        select_dict = {'each': self._select_batches,
                       'date': self._select_date_batches}
        return select_dict[select_type]

    def check_batches(self):
        """
        For batches in ``batch_list``, check for any missing or
        problematic outputs.
        """
        flowcell_dir = self.flowcell_dir
        batch_list = self.batch_list
        for batch_file in batch_list:
            bc = curation.BatchCurator(batch_file, flowcell_dir)
            if bc.report_problem_outputs():
                print("Problems with outputs for {}".format(batch_file))
            else:
                print("No problem outputs for {}".format(batch_file))

    def curate_batches(self, dry_run=False):
        """
        For batches in ``batch_list``, organize all output files.

        :type dry_run: bool
        :param dry_run: If flag is ``True``, only print what would be done.
        """
        flowcell_dir = self.flowcell_dir
        batch_list = self.batch_list
        for batch_file in batch_list:
            bc = curation.BatchCurator(batch_file, flowcell_dir)
            bc.organize_files(dry_run=dry_run)
