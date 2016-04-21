import datetime

from bripipetools.util import strings

### file/path/string parsing functions ###

def get_lib_id(lib_str):
    """
    Return library ID.

    :type lib_str: str
    :param lib_str: Any string that might contain a library ID of the format
        'lib1234'.

    :rtype: str
    :return: The matching substring representing the library ID or an empty
        sting ('') if no match found.
    """
    return strings.matchdefault('lib[1-9]+[0-9]*', lib_str)

def parse_fc_run_id(fc_run_id):
    """
    Parse Illumina flowcell run ID (or folder name) and return individual
    components indicating date, instrument ID, run number, flowcell ID, and
    flowcell position.

    :type fc_run_id: str
    :param fc_run_id: String adhering to standard Illumina format (e.g.,
        '150615_D00565_0087_AC6VG0ANXX') for a sequencing run.

    :rtype: (str, str, str, str, str)
    :return: 
    """
    fc_parts = fc_run_id.split('_')

    d = datetime.datetime.strptime(fc_parts[0], '%y%m%d')

    date = datetime.date.isoformat(d)
    instrument_id = fc_parts[1]
    run_num = int(fc_parts[2])

    fc_id = strings.matchdefault('(?<=(_(A|B|D)))([A-Z]|[0-9])*XX', fc_run_id)
    fc_pos = strings.matchdefault('.{1}(?=%s)' % fc_id, fc_run_id)

    return (date, instrument_id, run_num, fc_id, fc_pos)

def get_project_id(project_str):
    project_name = strings.matchdefault('P+[0-9]+(-[0-9]+){,1}', project_str)
    project_id = strings.matchdefault('(?<=P)[0-9]+', project_name)
    subproject_id = strings.matchdefault('(?<=-)[0-9]+', project_name)

    return (project_id, subproject_id)

def get_fastq_source(file_path):
    lane_id = strings.matchdefault('(?<=_)L00[1-8]', file_path)
    read_id = strings.matchdefault('(?<=_)R[1-2]', file_path)
    sample_num = int(strings.matchdefault('(?<=_S)[0-9]+', file_path))

    return lane_id, read_id, sample_num
