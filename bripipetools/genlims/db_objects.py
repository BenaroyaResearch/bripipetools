
def to_camel_case(snake_str):
    if not re.search('^_', snake_str):
        components = snake_str.split('_')
        return components[0] + "".join(x.title() for x in components[1:])
    else:
        return snake_str

def convert_keys(obj):
    if isinstance(obj, list):
        return [convert_keys(i) for i in obj]
    elif isinstance(obj, dict):
        return {to_camel_case(k): convert_keys(obj[k])
                for k in obj}
    else:
        return obj

class TG3Object(dict):
    '''
    Generic functions for objects in TG3 collections.
    '''

    def __init__(self, _id=None, type=None):

        self._id = _id
        self.type = type

    def to_db(self):
        return convert_keys(self.__dict__)


class Sample(TG3Object):
    '''
    GenLIMS object in the 'samples' collection
    '''

    def __init__(self, *args, **kwargs):
        if 'procedure_id' in kwargs:
            self.procedure_id = kwargs.pop('procedure_id')
        else:
            self.procedure_id = None
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

    def _init_from_library(self, lib_id, lib_packet):
        self.parent_id = lib_id
        self.run_id = lib_packet.get('run_id')
        self._id = lib_id + '_' + lib_packet.get('run_id')

        self._get_raw_data(lib_packet)

    def _get_raw_data(self, lib_packet):
        self.raw_data = get_lib_fastqs(lib_packet.get('fastq_dir'))
