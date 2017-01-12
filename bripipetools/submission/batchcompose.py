import os
import re

from .. import io


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

    # def _format_endpoint_root(local_dir):
    #     # endpoint_dir = re.sub('.*(?=(/genomics))', '/~', local_dir)
    #     endpoint_dir = re.sub('.*(?=(/genomics))', '/mnt', local_dir)
    #
    #     return endpoint_dir

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
