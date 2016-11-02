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


def get_flowcell_id(string):
    """
    Return flowcell ID.

    :type string: str
    :param string: any string that might contain an Illumina flowcell
        ID (e.g., C6VG0ANXX)

    :rtype: str
    :return: the matching substring representing the flowcell ID or an
        empty string ('') if no match found
    """
    return util.matchdefault('(?<=(_(A|B|D)))([A-Z]|[0-9])*X(X|Y)', string)


def parse_flowcell_run_id(run_id):
    """
    Parse Illumina flowcell run ID (or folder name) and return
    individual components indicating date, instrument ID, run number,
    flowcell ID, and flowcell position.

    :type run_id: str
    :param run_id: string adhering to standard Illumina format (e.g.,
        '150615_D00565_0087_AC6VG0ANXX') for a sequencing run

    :rtype: dict
    :return: a dict with fields for 'date', 'instrument_id',
        'run_number', 'flowcell_id', and 'flowcell_position'
    """
    id_parts = run_id.split('_')
    logger.debug("collecting the following parts from run ID {}: {}"
                 .format(run_id, id_parts))

    try:
        d = datetime.datetime.strptime(id_parts[0], '%y%m%d')
        date = datetime.date.isoformat(d)
    except ValueError:
        logger.warning("input string does not appear to contain a valid date")
        date = None

    instr_id = id_parts[1]

    try:
        run_num = int(id_parts[2])
    except IndexError:
        logger.warning("input string does not appear to contain a valid "
                       "run number")
        run_num = None

    fc_id = util.matchdefault('(?<=(_(A|B|D)))([A-Z]|[0-9])*X(X|Y)', run_id)
    fc_pos = util.matchdefault('.{1}(?=%s)' % fc_id, run_id)

    return {'date': date, 'instrument_id': instr_id, 'run_number': run_num,
            'flowcell_id': fc_id, 'flowcell_position': fc_pos}


def parse_fastq_filename(path):
    """
    Parse standard Illumina FASTQ filename and return individual
    components indicating generic path, lane ID, read ID, and
    sample number.

    :type path: str
    :param path: full path to FASTQ file with filename adhering to
        standard Illumina format (e.g.,
        '1D-HC29-C04_S27_L001_R1_001.fastq.gz')

    :rtype: dict
    :return: a dict with fields for 'path' (with root removed),
        'lane_id', 'read_id', and 'sample_number'
    """
    path = util.swap_root(path, 'genomics', '/')
    lane_id = util.matchdefault('(?<=_)L00[1-8]', path)
    read_id = util.matchdefault('(?<=_)R[1-2]', path)
    sample_num = int(util.matchdefault('(?<=_S)[0-9]+', path))

    return {'path': path, 'lane_id': lane_id, 'read_id': read_id,
            'sample_number': sample_num}
