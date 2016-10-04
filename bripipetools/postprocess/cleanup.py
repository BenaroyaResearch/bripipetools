"""
Clean up & organize outputs from processing workflow batch.
"""
import logging
logger = logging.getLogger(__name__)
import os
import re
import zipfile
import shutil

from .. import util
from .. import parsing
from .. import genlims
from .. import model as docs

class OutputCleaner(object):
    """
    Moves, renames, and deletes individual output files from a workflow
    processing batch for a selected project.
    """
    def __init__(self, path):
        logger.info("creating instance of OutputCleaner")
        self.path = path
        self.output_types = self._get_output_types()

    def _get_output_types(self):
        """
        Identify the types of outputs included for the project.
        """
        OUT_TYPES = ['qc', 'metrics', 'counts', 'alignments', 'logs']

        logging.debug("subfolders in project folder: {}"
                      .format(os.listdir(self.path)))
        return [f for f in os.listdir(self.path)
                if f.lower() in OUT_TYPES]

    def _get_output_paths(self, output_type):
        """
        Return full path for individual output files.
        """
        logging.debug("locating output files of type {}".format(output_type))
        output_root = os.path.join(self.path, output_type)
        return [os.path.join(self.path, root, f)
                for root, dirs, files in os.walk(output_root)
                for f in files]

    def _unzip_output(self, path):
        """
        Unzip the contents of a compressed output file.
        """
        logging.debug("extracting contents of {} to {}"
                      .format(path, os.path.dirname(path)))
        with zipfile.ZipFile(path) as zf:
            zf.extractall(os.path.dirname(path))

        # plist = []
        # with zipfile.ZipFile(path) as zf:
        #     for f in zf.namelist():
        #         plist.append(zf.extract(f))
        # return plist

    def _unnest_output(self, path):
        """
        Unnest files in a subfolder by concatenating filenames and
        moving up one level.
        """
        logging.debug("unnesting output {} from subfolder {}"
                      .format(path, os.path.dirname(path)))
        prefix = os.path.dirname(path)
        shutil.move(path, '{}_{}'.format(prefix, os.path.basename(path)))

    # def clean_outputs(self):
    #     """
    #     Walk through output types to unzip and unnest files.
    #     """
    #     for output_type in self.output_types:
    #         if output_type == 'QC':
    #             outputs = self._get_output_paths(output_type)
    #             for o in outputs:
    # QC/
    # |-lib10516_C8HAWANXX/
    #   |-----------------qcR1.zip/
    #                     |-------(fastqc_data.txt)
    #                     |-------(fastqc_report.html)




    # def _uzip_output(self, output):
