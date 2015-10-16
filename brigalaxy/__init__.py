from bioblend import galaxy
import requests, re, os, json

class SessionManager(object):

    def __init__(self, user_num=None, galaxy_user=None, galaxy_server=None,
                 galaxy_instance=None, galaxy_session=None, target_dir=None):

        if not galaxy_user:
            if user_num is None:
                self.select_user()
            else:
                self.select_user(user_num)
        else:
            self.gu = galaxy_user

        if not galaxy_server:
            self.server = 'http://srvgalaxy02'
        else:
            self.server = galaxy_server

        if not galaxy_instance:
            self.connect_to_galaxy_api()
        else:
            self.gi = galaxy_instance

        if not galaxy_session:
            self.connect_to_galaxy_server()
        else:
            self.gs = galaxy_session

    def select_user(self, user_num=None):

        # Load list of known users
        with open('data/users.json') as f:
            users = json.load(f)

        # Select user number
        if user_num is None:
            print "\nFound the following users:"
            for t,u in enumerate(users):
                print "%3d : %s" % (t, users[u].get('username'))

            un = raw_input("Type the number of the user you wish to select: ")
        else:
            un = user_num

        self.user = users[users.keys()[int(un)]]

    def connect_to_galaxy_api(self):

        # Connect to Galaxy API
        galaxy_instance = galaxy.GalaxyInstance(url=self.server,
                                                key=self.user.get('api_key'))
        self.gi = galaxy_instance

    def connect_to_galaxy_server(self):

        # Log into Galaxy server
        login_payload = {'email': self.user.get('username'),
                         'redirect': self.server,
                         'password': self.user.get('password'),
                         'login_button': 'Login'}
        galaxy_session = requests.session()
        login = galaxy_session.post(url=self.server + '/user/login?use_panels=True',
                                    data=login_payload)
        self.gs = galaxy_session

    def add_target_dir(self, target_dir=None):
        self.dir = target_dir


###################################

class HistoryManager(object):
    """
    Class with methods for inspecting and performing operations with a Galaxy History.
    """
    def __init__(self, galaxy_instance, history_id=None):
        self.gi = galaxy_instance

        if not history_id:
            self.select_history()
        else:
            self.hid = history_id
            self.hname = self.gi.histories.get_histories(self.hid)[0].get('name')

    def select_history(self):
        """
        Select current Galaxy History.
        """
        # Get list of histories on Galaxy and print as user options
        history_list = self.gi.histories.get_histories()
        print "\nFound the following histories:"
        for t,h in enumerate(history_list):
            print "%3d : %s" % (t, h.get('name'))

        # For the selected history, get the ID and full history contents
        var = raw_input("Type the number of the History you wish to select: ")
        history = history_list[int(var)]
        self.hid = history.get('id')
        self.hname = history.get('name')


    def get_datasets(self):
        """
        Get list of all Datasets in History.
        """
        dataset_list = self.gi.histories.show_history(self.hid, contents=True)
        self.dl = dataset_list

    def show_datasets(self):
        """
        View list of History Datasets.
        """
        if not hasattr(self, 'dl'):
            self.get_datasets()

        return self.dl

    def build_dataset_graph(self, dataset_graph={}):
        """
        Build graph representing input/output relationship of all Datasets in current History.
        """
        if not hasattr(self, 'dl'):
            self.get_datasets()

        get_provenance = self.gi.histories.show_dataset_provenance

        for d in self.dl:
            out_id = d.get('id')

            dataset_params = get_provenance(self.hid, out_id).get('parameters')

            dataset_inputs = [dataset_params[p].get(f) \
                              for p in dataset_params \
                              for f in dataset_params[p] \
                              if re.search('^id$', f)]

            if len(dataset_inputs):
                for d in dataset_inputs:
                    if d in dataset_graph:
                        dataset_graph[d] = list(set(dataset_graph[d] + [out_id]))
                    else:
                        dataset_graph[d] = [out_id]

        self.dg = dataset_graph


    def show_dataset_graph(self):
        """
        View graph (dictionary) with input/output relationship for all Datasets in History.
        """
        if not hasattr(self, 'dg'):
            self.build_dataset_graph()

        return self.dg

    def get_root_datasets(self):
        """
        Based on the Dataset graph, identify root Datasets in the History.
        """
        if not hasattr(self, 'dg'):
            self.build_dataset_graph()

        output_dataset_list = [o for outputs in self.dg.values() \
                               for o in outputs]
        root_dataset_list = [d for d in self.dl \
                             if d.get('id') not in output_dataset_list]
        self.rdl = root_dataset_list


    def show_root_datasets(self):
        """
        Show list of root Datasets in current History.
        """
        if not hasattr(self, 'rdl'):
            get_root_datasets()

        return self.rdl

    def get_input_datasets(self):
        """
        Get list of input (non-reference) Datasets for current History.
        """
        if not hasattr(self, 'rdl'):
            self.get_root_datasets()

        input_dataset_list = [{d.get('id'): d.get('name')} \
            for d in self.rdl \
            if re.search('incoming',
            self.gi.datasets.show_dataset(d.get('id')).get('file_name'))]

        self.idl = input_dataset_list

    def show_input_datasets(self):
        """
        View list of input (non-reference) Datasets for History.
        """
        if not hasattr(self, 'idl'):
            self.get_input_datasets()

        return self.idl


###################################

class ResultCollector(object):
    """
    Class with methods for collecting information about all downstream (output) Datasets for current input Dataset.
    """
    def __init__(self, history_manager=None, dataset_graph=None, input_dataset=None):

        self.hm = history_manager
        self.dg = dataset_graph

        self.id = input_dataset.keys()[0]
        self.file = input_dataset.values()[0]
        self.lib = re.search('lib[0-9]+(.*(XX)+)*',
                              self.file).group()

    def build_input_graph(self, input_id=None, input_graph={}):
        """
        Build graph representing all input/output relationships among Datasets downstream of input Dataset.
        """
        if not input_id:
            input_id = self.id

        self.ig = input_graph

        if input_id in self.dg:
            self.ig[input_id] = self.dg[input_id]

            for d in self.dg[input_id]:
                self.ig = self.build_input_graph(d, self.ig)

        return self.ig

    def get_input_outputs(self, input_id=None, input_output_list=[]):
        """
        Get list of all output Datasets downstream of current input Dataset.
        """
        if not input_id:
            input_id = self.id

        self.iol = input_output_list

        if input_id in self.dg:
            self.iol = list(set(self.iol + self.dg[input_id]))

            for d in self.dg[input_id]:
                self.iol = self.get_input_outputs(d, self.iol)

        return self.iol

    def show_output_list(self):

        if not hasattr(self, 'iol'):
            self.get_input_outputs()

        get_hid = self.hm.gi.histories.show_dataset
        sorted_output_list = sorted(self.iol, key=lambda x: get_hid(self.hm.hid, x).get('hid'))

        return sorted_output_list


###################################

class ResultDownloader(object):

    def __init__(self, session_manager, lib_id=None, output_id=None, result_type=None):

        self.gi = session_manager.gi
        self.gs = session_manager.gs
        self.dir = session_manager.dir
        self.lib = lib_id
        self.oid = output_id

        with open('data/params.json') as f:
            self.params = json.load(f)

        if not result_type:
            self.get_result_type()

        self.state = 'idle'

    def clean_dataset_name(self, dataset_name=None):

        dataset_name = re.sub(" on data [0-9]+( and data [0-9]+)*", "", dataset_name)
        dataset_name = re.sub("_.*(\:|\.)+", ": ", dataset_name)

        return dataset_name

    def get_dataset_name(self):
        dc = self.gi.datasets
        dataset_name = dc.show_dataset(self.oid).get('name')

        self.dname = self.clean_dataset_name(dataset_name)

    def get_result_type(self, result_type=None):

        if not hasattr(self, 'dname'):
            self.get_dataset_name()

        result_type_dict = self.params['result_types']

        self.rtd = result_type_dict

        if self.dname in result_type_dict:
            result_type = result_type_dict[self.dname]

        self.rt = result_type

    # Create output subdirectories for each Workflow result type
    def prep_output_folder(self):

        folder_dict = self.params['folders']

        if self.rt in folder_dict:
            result_folder = os.path.join(self.dir, folder_dict[self.rt])

        if not os.path.isdir(result_folder) and self.state is 'active':
            os.makedirs(result_folder)

        self.folder = result_folder


    def prep_download_instructions(self):

        if not hasattr(self, 'folder'):
            self.prep_output_folder()

        instructions = {}

        ext_dict = self.params['extensions']
        method_dict = self.params['methods']

        if self.rt in ext_dict:
            extension = ext_dict[self.rt]
            method = method_dict[os.path.splitext(extension)[1]]
            instructions['out_file'] = os.path.join(self.folder, self.lib + extension)

            if method == 'remote':
                instructions['file_url'] = (self.gi.base_url + '/datasets/' + self.oid + '/display?to_ext=html')
            elif method == 'local':
                instructions['file_url'] = self.gi.datasets.show_dataset(self.oid)['file_name']

            instructions['method'] = method

        self.instructions = instructions


    def show(self):
        self.state = 'idle'

        if self.rt:
            if not hasattr(self, 'instructions'):
                self.prep_download_instructions()

            return {'dataset_name': self.dname,
                    'result_type': self.rt,
                    'result_folder': self.folder,
                    'instructions': self.instructions}
        else:
            return {'dataset_name': self.dname,
                    'result_type': self.rt,
                    'result_folder': 'NA',
                    'instructions': 'NA'}

    def go(self):
        self.state = 'active'

        if self.rt:
            self.prep_output_folder()

            if not hasattr(self, 'instructions'):
                self.prep_download_instructions()

            msg = DownloadHandler(self.gs, self.instructions).get_data()
        else:
            msg = "Non-requested result type; skipping."

        return msg



###################################

class DownloadHandler(object):

    def __init__(self, galaxy_session, instructions):
        self.gs = galaxy_session
        self.src = instructions['file_url']
        self.path = instructions['out_file']
        self.method = instructions['method']

    def get_data(self):
        if self.method == 'remote':
            message = ("Copying file from %s to %s via remote connection." %
                       (self.src, self.path))

            r = self.gs.get(self.src)
            with open(self.path, 'wb') as f:
                f.write(r.content)

        elif self.method == 'local':
            message = ("Copying file from %s to %s via SLURM." %
                       (self.src, self.path))
#             os.system(('sbatch -N 1 -o slurm.out --open-mode=append <<EOF\n'
#                        '#!/bin/bash\n'
#                        'cp %s %s') % (self.src, self.path)

        return message
