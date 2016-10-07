"""
Clean up & organize outputs from processing workflow batch.
"""
import logging
logger = logging.getLogger(__name__)
import os
import re
import zipfile
import shutil


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
                for f in files
                if not re.search('(DS_Store|_old)', f)]

    def _unzip_output(self, path):
        """
        Unzip the contents of a compressed output file.
        """
        logging.debug("extracting contents of {} to {}"
                      .format(path, os.path.dirname(path)))
        paths = []
        with zipfile.ZipFile(path) as zf:
            for f in zf.namelist()[1:]:
                paths.append(zf.extract(f, os.path.dirname(path)))
        logging.debug("unzipped the following files: {}".format(paths))
        return paths

    def _unnest_output(self, path):
        """
        Unnest files in a subfolder by concatenating filenames and
        moving up one level.
        """
        logging.debug("unnesting output {} from subfolder {}"
                      .format(path, os.path.dirname(path)))
        prefix = os.path.dirname(path)
        if re.search('.zip$', path):
            logging.debug("unzipping contents of {} before unnesting"
                          .format(path))
            for p in self._unzip_output(path):
                shutil.move(p, '{}_{}'.format(prefix, os.path.basename(p)))
            try:
                shutil.rmtree(os.path.splitext(path)[0])
            except OSError:
                pass
        else:
            shutil.move(path, '{}_{}'.format(prefix, os.path.basename(path)))

    def _recode_output(self, path, output_type):
        """
        Rename file according to template.
        """
        filename_map = {'QC': ('fastqc_data.txt', 'fastqc_qc.txt')}
        swap = filename_map[output_type]
        newpath = re.sub(swap[0], swap[1], path)
        logging.debug("renaming {} to {}".format(path, newpath))
        shutil.move(path, newpath)
        return newpath

    def clean_outputs(self):
        """
        Walk through output types to unzip, unnest, and rename files.
        """
        for output_type in self.output_types:
            if output_type == 'QC':
                outputs = self._get_output_paths(output_type)
                for o in outputs:
                    outregex = re.compile(output_type + '$')
                    if not outregex.search(os.path.dirname(o)):
                        self._unnest_output(o)
                for o in os.listdir(os.path.join(self.path, output_type)):
                    self._recode_output(os.path.join(self.path, output_type, o),
                                        output_type)
