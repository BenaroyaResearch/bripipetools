"""
Connect to the GenLIMS Mongo database and perform basic operations.
"""

import pymongo

class GenLIMS(object):

    def __init__(self, dbname):

        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client[dbname]
