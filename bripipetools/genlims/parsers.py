from bripipetools.util import label_munging as labels


class LibListParser(object):

    def __init__(self, lib_list_file):

        self.lib_list_file = lib_list_file

    def _parse_lib_line(self, line):
        l_parts = line.strip().split('\t')

        lib_id = labels.get_lib_id(l_parts[0])

        project_id, subproject_id = labels.get_proj_id(l_parts[3])
        fastq_dir = l_parts[-1]

        lib_packet = {'project_id': project_id,
                      'subproject_id': subproject_id,
                      'fastq_dir': fastq_dir}

        flowcell_run_id = l_parts[2]
        fc_dir = l_parts[4]
        fc_date, instr, run_num, fc_id, fc_pos = labels.parse_fc_run_id(flowcell_run_id)

        flowcell_packet = {'date': fc_date,
                           'instrument': instr,
                           'run_number': run_num,
                           'flowcell_id': fc_id,
                           'flowcell_pos': fc_pos,
                           'flowcell_dir': fc_dir}

        return lib_id, lib_packet, flowcell_run_id, flowcell_packet

    # read and extract info from library list file
    def read_lib_list(self):
        lib_dict = {}
        fc_dict = {}
        with open(self.lib_list_file) as f:
            for i, l in enumerate(f):
                if i > 0:
                    lib_id, lib_packet, fc_run_id, fc_packet = self._parse_lib_line(l)
                    lib_packet['run_id'] = fc_run_id
                    lib_packet['run_tag'] = fc_packet.get('flowcell_id')

                    lib_dict.setdefault(lib_id, []).append(lib_packet)

                    if fc_run_id not in fc_dict:
                        fc_dict[fc_run_id] = fc_packet

        return fc_dict, lib_dict
