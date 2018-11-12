import logging
import datetime

from .. import util

logger = logging.getLogger(__name__)


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
    return util.matchdefault('(?<=(_(A|B|D)))([A-Z]|[0-9])*X(X|Y|2)', string)


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

    try:
        instr_id = id_parts[1]
    except IndexError:
        logger.warning("input string does not contain a vaild instrument number")
        instr_id = None

    try:
        run_num = int(id_parts[2])
    except IndexError:
        logger.warning("input string does not appear to contain a valid "
                       "run number")
        run_num = None

    fc_id = util.matchdefault('(?<=(_(A|B|D)))([A-Z]|[0-9])*X(X|Y|2)', run_id)
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
    path = util.swap_root(path, 'bioinformatics', '/')
    # Note use of matchlastdefault here to accomodate new basespace dir structs
    lane_id = util.matchlastdefault('(?<=_|-)L00[1-8]', path)
    read_id = util.matchdefault('(?<=_)R[1-2]', path)
    sample_num_str = util.matchdefault('(?<=_S)[0-9]+', path)
    if sample_num_str == "": sample_num_str = "0"
    sample_num = int(sample_num_str)
    
    logger.debug("Found fastq file {} for lane {} with read {} and sample {}"
                 .format(path, lane_id, read_id, sample_num))

    return {'path': path, 'lane_id': lane_id, 'read_id': read_id,
            'sample_number': sample_num}


