import logging
import os
import re

from .. import util
from .. import parsing
from .. import io

logger = logging.getLogger(__name__)


class BatchParameterizer(object):
    def __init__(self, sample_paths, parameters, endpoint, target_dir,
                 build=None):
        self.sample_paths = sample_paths
        self.parameters = parameters
        self.endpoint = endpoint
        self.target_dir = target_dir
        if build is not None:
            self.build = build
        else:
            self.build = 'GRCh38'

    def _get_lane_order(self):
        return [re.search('[1-8]', p['name']).group()
                for p in self.parameters
                if p['tag'] == 'fastq_in'
                and re.search('from_path', p['name'])]

    def _get_lane_fastq(self, sample_path, lane):
        fastq_paths = [os.path.join(sample_path, f)
                       for f in os.listdir(sample_path)
                       if re.search(r'L00{}'.format(lane), f)]
        if len(fastq_paths):
            fastq_path = fastq_paths[0]
        # create empty file if no FASTQ exists for current lane
        else:
            empty_fastq = 'empty_L00{}.fastq.gz'.format(lane)
            fastq_path = os.path.join(sample_path, empty_fastq)

            if not os.path.exists(fastq_path):
                open(fastq_path, 'a').close()

        return fastq_path

    def _build_reference_path(self, parameter):
        ref_dict = {
            'GRCh38': {
                'gtf': 'GRCh38/Homo_sapiens.GRCh38.77.gtf',
                'refflat': 'GRCh38/Homo_sapiens.GRCh38.77.refflat.txt',
                'ribosomal_intervals':
                    ('GRCh38/Homo_sapiens.GRCh38.77'
                     '.ribosomalIntervalsWheader_reorder.txt'),
                'adapters': 'adapters/smarter_adapter_seqs_3p_5p.fasta'
            },
            'NCBIM37': {
                'gtf': 'NCBIM37/Mus_musculus.NCBIM37.67.gtf',
                'refflat': 'NCBIM37/Mus_musculus.NCBIM37.67.refflat.txt',
                'ribosmal_intervals':
                    ('NCBIM37/Mus_musculus.NCBIM37.67'
                     '.ribosomalIntervalsWheader_reorder.txt'),
                'adapters': 'adapters/smarter_adapter_seqs_3p_5p.fasta'
            }
        }

        ref_type = re.sub('^annotation_', '', parameter['tag'])
        return 'library::annotation::{}'.format(
            ref_dict[self.build].get(ref_type)
        )

    def _prep_output_dir(self, output_type):

        output_dir = os.path.join(self.target_dir, output_type)

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        return output_dir

    def _build_output_path(self, sample_name, parameter):
        output_type_map = {'trimmed': 'TrimmedFastqs',
                           'counts': 'counts',
                           'alignments': 'alignments',
                           'metrics': 'metrics',
                           'qc': 'QC',
                           'trinity': 'Trinity',
                           'log': 'logs'}

        logger.debug("building output path of parameter '{}' for sample '{}'"
                     .format(parameter['tag'], sample_name))
        output_items = parsing.parse_output_name(parameter['tag'])
        output_dir = self._prep_output_dir(
            output_type_map[output_items['type']]
        )

        out_file = '{}_{}_{}.{}'.format(
            sample_name, output_items['source'], output_items['type'],
            output_items['extension']
        )

        return util.swap_root(os.path.join(output_dir, out_file),
                              'genomics', '/mnt/')

    def _build_sample_parameters(self, sample_path):
        sample_id = parsing.get_sample_id(sample_path)
        fc_id = parsing.get_flowcell_id(sample_path)
        sample_name = '{}_{}'.format(sample_id, fc_id).rstrip('_')

        param_values = []
        for param in self.parameters:
            if re.search('endpoint', param['name']):
                param_values.append(self.endpoint)

            elif param['type'] == 'sample':
                param_values.append(sample_name)
            elif param['type'] == 'input':
                lane = re.search('[1-8]', param['name']).group()
                param_values.append(
                    util.swap_root(
                        self._get_lane_fastq(sample_path, lane),
                        'genomics', '/mnt/'
                    )
                )
            elif param['type'] == 'annotation':
                param_values.append(self._build_reference_path(param))
            elif param['type'] == 'output':
                if re.search('^fastq_out', param['tag']):
                    final_fastq = '{}_R1-final.fastq.gz'.format(sample_name)
                    output_path = os.path.join(
                        util.swap_root(self.target_dir, 'genomics', '/mnt/'),
                        'inputFastqs', final_fastq
                    )
                else:
                    output_path = self._build_output_path(sample_name, param)
                param_values.append(output_path)

        return param_values

    def parameterize(self):
        sample_params = []
        for s in self.sample_paths:
            logger.debug("setting parameters for input sample file {}"
                         .format(s))
            s_values = self._build_sample_parameters(s)
            s_params = []
            for idx, v in enumerate(s_values):
                s_param = self.parameters[idx].copy()
                s_param['value'] = s_values[idx]
                s_params.append(s_param)
            sample_params.append(s_params)
        self.samples = sample_params








