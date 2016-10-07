"""
Connect to the GenLIMS Mongo database.
"""
import logging
logger = logging.getLogger(__name__)

import pymongo


logger.info("connecting to 'tg3' Mongo database")
client = pymongo.MongoClient('localhost', 27017)
db = client['tg3']
