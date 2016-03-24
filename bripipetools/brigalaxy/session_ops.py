import os
import glob
import json
import requests
from bioblend import galaxy

class SessionManager(object):

    def __init__(self, galaxy_server='http://srvgalaxy02',
                 user_num=None, galaxy_user=None, target_dir=None,
                 include_results=None):

        self._locate_data_dir()

        if not galaxy_user:
            if user_num is None:
                self.select_user()
            else:
                self.select_user(user_num)
        else:
            self.gu = galaxy_user

        self.server = galaxy_server
        self.rd = include_results

    def _locate_data_dir(self, max_height=2):

        # TODO: raise error if data folder not found
        for d in range(0, max_height):
            up_dir = '../' * d
            dir_glob = os.path.join(up_dir, '*')
            for f in glob.glob(dir_glob):
                if 'data' in f and os.path.isdir(f):
                    self.data_path = f
                    break

    def select_user(self, user_num=None):

        # Load list of known users
        user_data = os.path.join(self.data_path, 'users.json')
        with open(user_data) as f:
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
        login = galaxy_session.post(url=(self.server +
                                         '/user/login?use_panels=True'),
                                    data=login_payload)
        self.gs = galaxy_session

    def connect_all(self):

        # Connect go Galaxy API
        self.connect_to_galaxy_api()

        # Connect to Galaxy server
        self.connect_to_galaxy_server()

    def add_target_dir(self, target_dir=None):
        self.dir = target_dir

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
