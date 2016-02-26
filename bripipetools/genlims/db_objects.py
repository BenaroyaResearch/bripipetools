import os, re
import xml.etree.ElementTree as et

from bripipetools.util import string_ops as so
from bripipetools.util import file_ops as files
from bripipetools.util import label_munging as labels

def convert_keys(obj):
    if isinstance(obj, list):
        return [convert_keys(i) for i in obj]
    elif isinstance(obj, dict):
        return {so.to_camel_case(k): convert_keys(obj[k])
                for k in obj}
    else:
        return obj

def read_fc_run_params(run_params_file):
    tree = et.parse(run_params_file)
    return {param.tag: param.text.rstrip() for param in tree.getroot()[0]
            if param.text is not None}

def collect_fastq_info(file_path):
    file_type,compression = files.get_file_type(file_path)

    if file_type == 'fastq':
        lane_id, read_id, sample_num = labels.get_fastq_source(file_path)

    file_path = re.sub('.*(?=/genomics)', '', file_path)

    return {'path': file_path, 'lane_id': lane_id,
            'read_id': read_id, 'sample_number': sample_num}

# describe raw files for current lib
def get_lib_fastqs(fastq_dir):
    # check if logged into server or accessing mounted volume
    if not os.path.isdir(fastq_dir):
        fastq_dir = re.sub('mnt', 'Volumes', fastq_dir)

    return [collect_fastq_info(os.path.join(fastq_dir, f))
            for f in os.listdir(fastq_dir)]


class TG3Object(dict):
    '''
    Generic functions for objects in TG3 collections.
    '''

    def __init__(self, _id=None, type=None):

        self._id = _id
        self.type = type

    def to_db(self):
        return convert_keys(self.__dict__)


class Run(TG3Object):
    '''
    GenLIMS object in the 'runs' collection
    '''

    def __init__(self, *args, **kwargs):
        if 'protocol_id' in kwargs:
            self.protocol_id = kwargs.pop('procedure_id')
        else:
            self.protocol_id = None
        TG3Object.__init__(self, *args, **kwargs)


class FlowcellRun(Run):
    '''
    GenLIMS object in 'runs' collection of type 'flowcell'
    '''

    def __init__(self, *args, **kwargs):
        Run.__init__(self, *args, **kwargs)

        # overwrite sample type
        self.type = 'flowcell'

    def _init_from_fc_packet(self, fc_run_id, fc_packet):
        self._id = fc_run_id

        fc_dir = fc_packet.pop('flowcell_dir')
        for k, v in fc_packet.items():
            setattr(self, k, v)

        self._get_fc_params(fc_dir)
        self._get_fc_protocol()

    def _get_fc_params(self, fc_dir):
        root_dir = files.find_dir('/', 'genomics', 3)
        local_fc_dir = re.sub('.*genomics', root_dir, fc_dir)
        run_params_file = os.path.join(local_fc_dir, self._id, 'runParameters.xml')

        self.parameters = read_fc_run_params(run_params_file)

    def _get_fc_protocol(self):

        instrument_dict = {'D00565': 'HiSeq2500',
                           'H135': 'HiScanSQ'}

        fc_param = self.parameters.get('Flowcell')
        is_rapid = 'rapid' in fc_param.lower()
        version = so.matchdefault('v[0-9]+', fc_param)
        if is_rapid:
            self.protocol_id = '_'.join([instrument_dict[self.instrument],
                                     'rapid', version])
        else:
            self.protocol_id = '_'.join([instrument_dict[self.instrument],
                                      version])


class Sample(TG3Object):
    '''
    GenLIMS object in the 'samples' collection
    '''

    def __init__(self, *args, **kwargs):

        sample_fields = ['protocol_id', 'project_id', 'subproject_id']
        for field in sample_fields:
            if field in kwargs:
                setattr(self, field, kwargs.pop('protocol_id'))
            else:
                setattr(self, field, None)
        TG3Object.__init__(self, *args, **kwargs)


class SequencedLibrarySample(Sample):
    '''
    GenLIMS object in 'samples' collection of type 'sequenced library'
    '''

    def __init__(self, *args, **kwargs):

        if 'parent_id' in kwargs:
            self.parent_id = kwargs.pop('parent_id')
        else:
            self.parent_id = None
        Sample.__init__(self, *args, **kwargs)

        # overwrite sample type
        self.type = 'sequenced library'

    def _init_from_lib_packet(self, lib_id, lib_packet):
        self.parent_id = lib_id
        self.run_id = lib_packet.get('run_id')
        self._id = '%s_%s' % (lib_id, lib_packet.get('run_tag'))
        self.project_id = lib_packet.get('project_id')
        self.subproject_id = lib_packet.get('subproject_id')

        self._get_raw_data(lib_packet)

    def _get_raw_data(self, lib_packet):
        self.raw_data = get_lib_fastqs(lib_packet.get('fastq_dir'))
