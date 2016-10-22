"""
Connect to the GenLIMS Mongo database.
"""
import logging
import pymongo

logger = logging.getLogger(__name__)

logger.info("connecting to 'tg3' Mongo database")
client = pymongo.MongoClient('localhost', 27017)
db = client['tg3']
