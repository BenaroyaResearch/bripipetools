import logging
import os
import re

from .. import util
from .. import parsing
from .. import io

logger = logging.getLogger(__name__)


class BatchComposer(object):
    def __init__(self, sample_paths, workflow_template, endpoint, target_dir,
                 build=None):
        self.sample_paths = sample_paths
        self.workflow_template = workflow_template
        self.workflowbatch_file = io.WorkflowBatchFile(
            path=self.workflow_template,
            state='template'
        )
        self.workflow_data = self.workflowbatch_file.parse()
        self.endpoint = endpoint
        self.target_dir = target_dir
        if build is not None:
            self.build = build

    def _get_lane_order(self):
        return [re.search('[1-8]', p['name']).group()
                for p in self.workflow_data['parameters']
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

    def _build_output_path(self, sample_name, parameter):
        # output_types = ['trimmed', 'counts', 'alignments', 'metrics',
        #                 'QC', 'Trinity', 'log']
        output_type_map = {'counts': 'counts',
                           'alignments': 'alignments',
                           'metrics': 'metrics',
                           'qc': 'QC',
                           'trinity': 'Trinity',
                           'log': 'logs'}

        logger.debug("building output path of parameter '{}' for sample '{}'"
                     .format(parameter['tag'], sample_name))
        output_items = parsing.parse_output_name(parameter['tag'])
        output_dir = os.path.join(self.target_dir,
                                  output_type_map[output_items['type']])

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

        sample_params = []
        for param in self.workflow_data['parameters']:
            if param['type'] == 'sample':
                sample_params.append(sample_name)
            elif param['type'] == 'input':
                if re.search('from_endpoint', param['name']):
                    sample_params.append(self.endpoint)
                elif re.search('from_path', param['name']):
                    lane = re.search('[1-8]', param['name']).group()
                    # for lane in self._get_lane_order():
                    sample_params.append(
                        util.swap_root(
                            self._get_lane_fastq(sample_path, lane),
                            'genomics', '/mnt/'
                        )
                    )
            # elif 'annotation' in param:
            #     ref_path = build_ref_path(param, self.build)
            #     sample_params.append(ref_path)
            elif param['type'] == 'output':
                if re.search('to_endpoint', param['name']):
                    sample_params.append(self.endpoint)
                elif re.search('to_path', param['name']):
                    if re.search('^fastq_out', param['tag']):
                        final_fastq = '%s_R1-final.fastq.gz' % sample_name
                        output_path = os.path.join(
                            util.swap_root(self.target_dir, 'genomics', '/mnt/'),
                            'inputFastqs', final_fastq)
                    else:
                        output_path = self._build_output_path(sample_name,
                                                              param)
                    sample_params.append(output_path)

        return sample_params

    # def _build_ref_path(param, build='GRCh38'):
    #     ref_dict = {}
    #     ref_dict['GRCh38'] = dict([('gtf', 'GRCh38/Homo_sapiens.GRCh38.77.gtf'),
    #                                ('refflat',
    #                                 'GRCh38/Homo_sapiens.GRCh38.77.refflat.txt'),
    #                                ('ribosomal_intervals',
    #                                 'GRCh38/Homo_sapiens.GRCh38.77.ribosomalIntervalsWheader_reorder.txt'),
    #                                ('adapters',
    #                                 'adapters/smarter_adapter_seqs_3p_5p.fasta')])
    #     ref_dict['NCBIM37'] = dict(
    #         [('gtf', 'NCBIM37/Mus_musculus.NCBIM37.67.gtf'),
    #          ('refflat', 'NCBIM37/Mus_musculus.NCBIM37.67.refflat.txt'),
    #          ('ribosomal_intervals',
    #           'NCBIM37/Mus_musculus.NCBIM37.67.ribosomalIntervalsWheader_reorder.txt'),
    #          ('adapters', 'adapters/smarter_adapter_seqs_3p_5p.fasta')])
    #     ref_type = re.sub('^annotation_', '', param)
    #     ref_path = 'library::annotation::' + ref_dict[build].get(ref_type)
    #
    #     return ref_path

    def prep_output_dir(self, output_type):

        output_dir = os.path.join(self.target_dir, output_type)

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        return output_dir
