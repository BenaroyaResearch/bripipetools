import re, os

from bripipetools.io import labels

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


class WorkflowParser(object):
    def __init__(self, batch_file):
        """
        A parser to map input sample names to expected output files based on a
        completed Globus Galaxy batch submit file.

        :type batch_file: str
        :param batch_file: File path of batch submit file.
        """
        self.batch_file = batch_file
        self._read_batch_file()

    def _read_batch_file(self):
        """
        Read and store lines from batch submit file.
        """
        batch_file = self.batch_file
        with open(batch_file) as f:
            batch_lines = f.readlines()

        self.batch_lines = batch_lines

    def get_workflow_name(self):
        """
        Identify metadata line indicating workflow name; return name.

        :rtype: str
        :return: The name of the current workflow.
        """
        batch_lines = self.batch_lines

        name_line = [l for l in batch_lines if 'Workflow Name' in l][0]
        return name_line.strip().split('\t')[-1]

    def get_params(self):
        """
        Identify header line with parameter names; store the index and name of
        each parameter.

        :rtype: dict
        :return: A dict with parameter number (index) and paramter name as
            key-value pairs.
        """
        batch_lines = self.batch_lines

        param_line = [l for l in batch_lines if 'SampleName' in l][0]
        return {idx: re.sub('##.*', '', p) \
                for idx,p in enumerate(param_line.strip().split('\t'))}

    def get_sample_lines(self):
        """
        Extract the batch file lines containing paramters for each sample.
        """
        batch_lines = self.batch_lines

        param_idx = [idx for idx,l in enumerate(batch_lines)
                     if 'SampleName' in l][0]
        return batch_lines[param_idx + 1:len(batch_lines)]

    def get_sample_params(self, sample_line):
        """
        Collect the parameter details for each input sample; store the index
        and input for each parameter.

        :type sample_line: str
        :param sample_line: Raw, tab-delimited line of text from workflow
            batch submit file describing the paramaters for a single sample.

        :rtype: dict
        :return: A dict, where for the sample name is a key and the value is
            another dict with output ID and output path as key-value pairs.
        """
        batch_lines = self.batch_lines

        param_dict = self.get_params()
        return {param_dict[i]: p
                for i,p in enumerate(sample_line.strip().split('\t'))}

    def get_batch_outputs(self):
        """
        Build the mapping between each input sample and its expected output
        files.

        :rtype: dict
        :return: A dict of dicts, where the value stored for each input sample
            key is a dictionary with parameter name (output ID) and output
            file path as key-value pairs.
        """

        sample_lines = self.get_sample_lines()
        sample_output_map = {}
        for sample in sample_lines:
            sample_params = self.get_sample_params(sample)
            sample_output_map[sample_params['SampleName']] = \
                {re.sub('_out', '', output_name): output_value
                 for (output_name, output_value) in sample_params.items()
                 if 'out' in output_name}
        return sample_output_map
