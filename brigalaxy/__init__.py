from bioblend import galaxy
import requests, re, os, json, zipfile, StringIO

class SessionManager(object):

    def __init__(self, user_num=None, galaxy_user=None, galaxy_server=None,
                 galaxy_instance=None, galaxy_session=None,
                 include_results=None, target_dir=None):

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

        self.rd = include_results

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

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)


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

    def annotate_dataset_list(self):
        def clean_dataset_name(dataset_name=None):
            """
            Format a Dataset name (to make it generic).
            """
            dataset_name = re.sub("lib.*fastq", "input FASTQ", dataset_name)
            dataset_name = re.sub(" on data [0-9]+( and data [0-9]+)*", "",
                                  dataset_name)
            dataset_name = re.sub("_.*(\:|\.)+", ": ", dataset_name)

            return dataset_name

        dataset_dict = {d.get('id'):
                        {'name': clean_dataset_name(d.get('name')),
                         'num': d.get('hid')} for d in self.dl}

        self.dd = dataset_dict

    # def get_dataset_name(self, dataset_id):
    #     """
    #     Get Dataset name corresponding to ID.
    #     """
    #     dc = self.gi.datasets
    #     dataset_name = dc.show_dataset(dataset_id).get('name')
    #
    #     return self.clean_dataset_name(dataset_name)

    def build_dataset_graph(self, dataset_graph={}):
        """
        Build graph representing input/output relationship of all Datasets in
        current History.
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
        View graph (dictionary) with input/output relationship for all
        Datasets in History.
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

    def build_summary_graph(self, input_dataset=None, summary_graph={}):
        """
        Trace path from a single input to all outputs.
        """
        if not hasattr(self, 'idl'):
            self.get_input_datasets()

        if not input_dataset:
            input_id = self.idl[0].keys()[0]
        else:
            input_id = input_dataset

        self.sg = summary_graph

        if isinstance(input_id, list):
            [self.build_summary_graph(i, self.sg) for i in input]
        if input_id in self.dg:
            [self.build_summary_graph(i, self.sg) \
             for i in self.dg[input_id]]

            self.sg[input_id] = [i for i in self.dg[input_id]]

        return self.sg

    def collect_history_info(self):
        if not hasattr(self, 'sg'):
            self.build_summary_graph()
        if not hasattr(self, 'dd'):
            self.annotate_dataset_list()

###################################

class ResultCollector(object):
    """
    Class with methods for collecting information about all downstream
    (output) Datasets for current input Dataset.
    """
    def __init__(self, history_manager=None, input_dataset=None):

        self.hm = history_manager

        self.id = input_dataset.keys()[0]
        self.file = input_dataset.values()[0]
        self.lib = re.search('lib[0-9]+(.*(XX)+)*',
                              self.file).group()

    def get_input_outputs(self, input_id=None, input_output_list=[]):
        """
        Get list of all output Datasets downstream of current input Dataset.
        """
        if not input_id:
            input_id = self.id

        self.iol = input_output_list

        if input_id in self.hm.dg:
            self.iol = list(set(self.iol + self.hm.dg[input_id]))

            for d in self.hm.dg[input_id]:
                self.iol = self.get_input_outputs(d, self.iol)

        return self.iol

    def annotate_output_list(self):

        if not hasattr(self, 'iol'):
            self.get_input_outputs()

        def get_info(dataset_id):
            dname = self.hm.dd[dataset_id].get('name')
            dnum = self.hm.dd[dataset_id].get('num')

            return (dname, dnum)

        self.ol = []
        for output in self.iol:
            dname,dnum = get_info(output)
            priors = [get_info(d)[0] \
                      for d in self.hm.sg if output in self.hm.sg[d]][0]
            self.ol.append({'id': output, 'num': dnum,
                                'name': dname, 'prior': priors})


    def flag_duplicate_outputs(self, output_list):
        seen = set()
        seen_add = seen.add

        # find final versions of duplicated outputs
        duplicated = { x.get('name'): i \
                       for i,x in enumerate(output_list) \
                       if x.get('name') in seen or seen_add(x.get('name')) }

        # remove duplicated outputs if not final version
        not_final = [i for i,x in enumerate(output_list) \
                     if x.get('name') in duplicated \
                     and not i == duplicated[x.get('name')]]

        for i in not_final:
            output_list[i]['name'] = 'skip_' + output_list[i]['name']

        return output_list

    def show_output_list(self):

        if not hasattr(self, 'ol'):
            self.annotate_output_list()

        get_hid = self.hm.gi.histories.show_dataset
        sorted_output_list = sorted(self.ol, key=lambda x: x.get('num'))
        final_output_list = self.flag_duplicate_outputs(sorted_output_list)

        return sorted_output_list


###################################

class ResultDownloader(object):

    def __init__(self, session_manager, lib_id=None, output=None,
                 result_type=None):

        self.gi = session_manager.gi
        self.gs = session_manager.gs
        self.dir = session_manager.dir
        self.lib = lib_id


        if output is not None:
            self.parse_output(output)

        with open('data/params.json') as f:
            self.params = json.load(f)

        if not result_type:
            self.get_result_type()

        self.state = 'idle'

    def parse_output(self, output):
        self.dname = output.get('name')
        self.oid = output.get('id')
        self.prior = output.get('prior')
        self.label = '%s (%d)' % (self.dname, output.get('num'))


    def get_result_type(self, result_type=None):

        dname = self.dname

        result_type_dict = self.params['result_types']

        self.rtd = result_type_dict

        if dname in result_type_dict:
            result_type = result_type_dict[dname]

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

            if 'bam' in extension:
                instructions['out_idx'] = os.path.join(self.folder, self.lib + extension + '.bai')
                instructions['idx_url'] = self.gi.datasets.show_dataset(self.oid)['metadata_bam_index']

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
            msg = ["Non-requested result type; skipping."]

        return msg



###################################

class DownloadHandler(object):

    def __init__(self, galaxy_session, instructions):
        self.gs = galaxy_session
        self.src = instructions['file_url']
        self.path = instructions['out_file']
        self.method = instructions['method']

        if 'idx_url' in instructions:
            self.idx_src = instructions['idx_url']
            self.idx_path = instructions['out_idx']

    def get_data(self):
        message=[]
        if self.method == 'remote':
            message.append(("Copying file from %s to %s via remote connection." %
                            (self.src, self.path)))

            r = self.gs.get(self.src)
            with open(self.path, 'wb') as f:
                f.write(r.content)

        elif self.method == 'local':
            message.append(("Copying file from %s to %s via SLURM." %
                            (self.src, self.path)))
            os.system(('sbatch -N 1 -o slurm.out --open-mode=append <<EOF\n'
                       '#!/bin/bash\n'
                       'cp %s %s') % (self.src, self.path))

            if hasattr(self, 'idx_src'):
                message.append(("Copying index from %s to %s via SLURM." %
                                (self.idx_src, self.idx_path)))
                os.system(('sbatch -N 1 -o slurm.out --open-mode=append <<EOF\n'
                           '#!/bin/bash\n'
                           'cp %s %s') % (self.idx_src, self.idx_path))

        return message


###################################

class ResultStitcher(object):
    def __init__(self, resultType=None, processedDir=None, libList=None):
        self.resultType = resultType
        self.processedDir = processedDir
        self.resultDir = os.path.join(self.processedDir, self.resultType)
        self.libList = libList

        if self.libList is None:
            self.libList = self.get_lib_list(self.resultDir)

    def get_lib_id(self, libFile):
        libId = re.search('lib[0-9]+(.*(XX)+)*', libFile).group()

        return libId

    def get_lib_list(self, resultDir):
        self.libList = [self.get_lib_id(libFile) \
                   for libFile in os.listdir(self.resultDir) \
                   if 'lib' in libFile]
        self.libList = list(set(self.libList))
        self.libList.sort()
        return self.libList

    def build_count_dict(self):
        self.countDict = {}
        print("Generating combined counts data...")
        for idx, lib in enumerate(self.libList):
            filePath = [os.path.join(self.resultDir, fileName) \
                        for fileName in os.listdir(self.resultDir) \
                        if lib in fileName][0]

            with open(filePath) as csvFile:
                reader = csv.reader(csvFile, delimiter = '\t')
                if idx == 0:
                    self.countHeader = ['geneName', lib]
                    for row in reader:
                        self.countDict[row[0]] = [row[1]]
                else:
                    self.countHeader.append(lib)
                    for row in reader:
                        self.countDict[row[0]].append(row[1])

        return (self.countHeader, self.countDict)

    def write_counts_file(self, countsFile):
        print("Writing combined counts file...")
        with open(countsFile, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(self.countHeader)
            for entry in self.countDict:
                writer.writerow([entry] + self.countDict[entry])

    def build_metric_list(self):
        # Specify information for combined metric file below
        self.metricHeader = ['libID']
        self.metricList = []

        # Specify all output filenames
        metricFileDict = {'picard_align': {'fileExt': '_qc.zip',
                                           'fileName': 'CollectAlignmentSummaryMetrics.metrics.txt'},
                       'picard_rnaseq': {'fileExt': '_al.zip',
                                         'fileName': 'CollectRnaSeqMetrics.metrics.txt'},
                       'tophat_stats': {'fileExt': 'ths.txt'},
                       'htseq': {'fileExt': 'mm.txt'},
                       'picard_markdups': {'fileExt': 'MarkDups.zip',
                                           'fileName': 'MarkDuplicates.metrics.txt'}}
        metricTypes = ['picard_align', 'picard_rnaseq', 'tophat_stats', 'htseq', 'picard_markdups']

        print("Generating combined metrics data...")
        for idx, lib in enumerate(self.libList):
            metrics = [lib]
            for metricType in metricTypes:
                filePath = [os.path.join(self.resultDir, fileName) \
                            for fileName in os.listdir(self.resultDir) \
                            if lib in fileName and
                            metricFileDict[metricType].get('fileExt') in fileName][0]

                if '.zip' in metricFileDict[metricType].get('fileExt'):
                    with zipfile.ZipFile(filePath) as metric:
                        metSrc = StringIO.StringIO(metric.read(metricFileDict[metricType].get('fileName')))
                        metricLines = metSrc.readlines()
                    metricVals = metricLines[7].rstrip('\n').split('\t')
                    headerVals = metricLines[6].rstrip('\n').split('\t')

                else:
                    metricVals = []
                    if metricType is 'tophat_stats':
                        col = 0
                        headerVals = ['fastq_total_reads', 'reads_aligned_sam',
                                   'aligned', 'reads_with_mult_align',
                                   'algn_seg_with_mult_algn']
                    elif metricType is 'htseq':
                        col = 1
                        headerVals = ['no_feature',
                                   'ambiguous', 'too_low_aQual', 'not_aligned',
                                   'alignment_not_unique']
                    with open(filePath) as metric:
                        metricLines = metric.readlines()
                        for line in metricLines:
                            metricVals.append(line.strip().split('\t')[col])
                if idx == 0:
                    self.metricHeader = self.metricHeader + headerVals
                metrics = metrics + metricVals

            # Add column for normalized reads
            ureIdx = self.metricHeader.index("UNPAIRED_READS_EXAMINED")
            unpairedExamined = float(metrics[ureIdx])

            ftrIdx = self.metricHeader.index("fastq_total_reads")
            totalReads = float(metrics[ftrIdx])

            metrics.append("%f" % (unpairedExamined / totalReads))

            if idx == 0:
                self.metricHeader = self.metricHeader + ['mapped_reads_w_dups']
            self.metricList.append(metrics)

        return (self.metricHeader, self.metricList)

    def write_metrics_file(self, metricsFile):
        print("Writing combined metrics file...")
        with open(metricsFile, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(self.metricHeader)
            for entry in self.metricList:
                writer.writerow(entry)

    def execute(self, targetFile):
        if self.resultType is 'counts':
            self.build_count_dict()
            self.write_counts_file(targetFile)
        elif self.resultType is 'metrics':
            self.build_metric_list()
            self.write_metrics_file(targetFile)
        print "Done"
