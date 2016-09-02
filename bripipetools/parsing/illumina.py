import datetime

from bripipetools.util import strings, files

### file/path/string parsing functions ###
def get_project_label(str):
    return strings.matchdefault('P+[0-9]+(-[0-9]+){,1}', str)

def parse_project_label(project_label):
    """
    Parse a Genomics Core project label (e.g., P00-0) and return
    individual components indicating project ID and subproject ID.

    :type project_label: str
    :param project_label: String following Genomics Core convention for
        project labels, P<project ID>-<subproject ID>.

    :rtype: dict
    :return: A dict with fields for 'project_id' and 'subproject_id'.
    """
    project_id = int(strings.matchdefault('(?<=P)[0-9]+', project_label))
    subproject_id = int(strings.matchdefault('(?<=-)[0-9]+', project_label))

    return {'project_id': project_id, 'subproject_id': subproject_id}

def get_library_id(str):
    """
    Return library ID.

    :type str: str
    :param str: Any string that might contain a library ID of the format
        'lib1234'.

    :rtype: str
    :return: The matching substring representing the library ID or an empty
        sting ('') if no match found.
    """
    return strings.matchdefault('lib[1-9]+[0-9]*', str)

def parse_flowcell_run_id(run_id):
    """
    Parse Illumina flowcell run ID (or folder name) and return individual
    components indicating date, instrument ID, run number, flowcell ID, and
    flowcell position.

    :type run_id: str
    :param run_id: String adhering to standard Illumina format (e.g.,
        '150615_D00565_0087_AC6VG0ANXX') for a sequencing run.

    :rtype: dict
    :return: A dict with fields for 'date', 'instrument_id', 'run_number',
        'flowcell_id', and 'flowcell_position'.
    """
    id_parts = run_id.split('_')

    d = datetime.datetime.strptime(id_parts[0], '%y%m%d')
    date = datetime.date.isoformat(d)
    instr_id = id_parts[1]
    run_num = int(id_parts[2])
    fc_id = strings.matchdefault('(?<=(_(A|B|D)))([A-Z]|[0-9])*XX', run_id)
    fc_pos = strings.matchdefault('.{1}(?=%s)' % fc_id, run_id)

    return {'date': date, 'instrument_id': instr_id, 'run_number': run_num,
            'flowcell_id': fc_id, 'flowcell_position': fc_pos}

def parse_fastq_filename(path):
    """
    Parse standard Illumina FASTQ filename and return individual
    components indicating generic path, lane ID, read ID, and
    sample number.

    :type path: str
    :param path: Full path to FASTQ file with filename adhering to
        standard Illumina format (e.g.,
        '1D-HC29-C04_S27_L001_R1_001.fastq.gz').

    :rtype: dict
    :return: A dict with fields for 'path' (with root removed),
        'lane_id', 'read_id', and 'sample_number'.
    """
    path = files.swap_root(path, 'genomics', '/')
    lane_id = strings.matchdefault('(?<=_)L00[1-8]', path)
    read_id = strings.matchdefault('(?<=_)R[1-2]', path)
    sample_num = int(strings.matchdefault('(?<=_S)[0-9]+', path))

    return {'path': path, 'lane_id': lane_id, 'read_id': read_id,
            'sample_number': sample_num}
