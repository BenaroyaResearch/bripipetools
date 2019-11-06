import logging
import os

from .. import util

logger = logging.getLogger(__name__)


def get_project_label(string):
    """
    Return a Genomics Core project label matched in input string.

    :type string: str
    :param string: any string

    :rtype: str
    :return: Genomics Core project label (e.g., P00-0) substring or
        empty string, if no match found
    """
    return util.matchdefault('P+[0-9]+(-[0-9]+){,1}', string)


def parse_project_label(project_label):
    """
    Parse a Genomics Core project label (e.g., P00-0) and return
    individual components indicating project ID and subproject ID.

    :type project_label: str
    :param project_label: String following Genomics Core convention for
        project labels, P<project ID>-<subproject ID>

    :rtype: dict
    :return: a dict with fields for 'project_id' and 'subproject_id'
    """
    project_id = int(util.matchdefault('(?<=P)[0-9]+', project_label))
    subproject_id = int(util.matchdefault('(?<=-)[0-9]+', project_label))

    return {'project_id': project_id, 'subproject_id': subproject_id}


def get_library_id(string):
    """
    Return library ID matched in input string.

    :type string: str
    :param string: any string that might contain a library ID of the
        format 'lib1234'

    :rtype: str
    :return: the matching substring representing the library ID or an
        empty string ('') if no match found
    """
    return util.matchdefault('lib[1-9]+[0-9]*', string)


def get_sample_id(string):
    """
    More general than library ID; returns either library ID (if
    present), or any word starting with 'Sample_', ends in a number,
    and preceeds any non-alphanumeric characters.

    :type string: str
    :param string: any string that might contain a form of sample ID

    :rtype: str
    :return: the matching substring representing the sample ID or an
        empty string ('') if no match found
    """
    sample_id = util.matchdefault('lib[0-9]+', string)
    if not len(sample_id):
        sample_id = util.matchdefault('Sample_.*[0-9]+', string)

    return sample_id


def parse_flowcell_path(flowcell_path):
    """
    Return 'genomics' root and run ID based on directory path.
    """
    # TODO: raise some sort of exception, if path doesn't end in valid run id
    # return {'genomics_root': util.matchdefault('.*(?=genomics)', flowcell_path),
    #         'run_id': os.path.basename(flowcell_path.rstrip('/'))}
    # Upon move to Isilon, "genomics" root is now "bioinformatics/pipeline" root
    return {'pipeline_root': util.matchdefault('.*(?=pipeline)', flowcell_path),
            'run_id': os.path.basename(flowcell_path.rstrip('/'))}


def parse_batch_file_path(batchfile_path):
    """
    Return 'genomics' root and batch file name based on directory path.
    """
    # return {'genomics_root': util.matchdefault('.*(?=genomics)',
    #                                            batchfile_path),
    #         'workflowbatch_filename': os.path.basename(batchfile_path)}
    # Upon move to Isilon, "genomics" root is now "bioinformatics/pipeline" root
    return {'pipeline_root': util.matchdefault('.*(?=pipeline)',
                                               batchfile_path),
            'workflowbatch_filename': os.path.basename(batchfile_path)}

