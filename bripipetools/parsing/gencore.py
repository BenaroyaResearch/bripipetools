import logging
import datetime

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