"""
Connect to the GenLIMS Mongo database and perform basic operations.
"""
import logging
logger = logging.getLogger(__name__)

import pymongo

logger.info("connecting to 'tg3' Mongo database")
client = pymongo.MongoClient('localhost', 27017)
db = client['tg3']

def get_samples(db, query):
    """
    Return list of documents from 'samples' collection based on query.
    """
    logger.debug("searching 'samples' collection with query {}".format(query))
    return list(db.samples.find(query))

def get_runs(db, query):
    """
    Return list of documents from 'runs' collection based on query.
    """
    logger.debug("searching 'runs' collection with query {}".format(query))
    return list(db.runs.find(query))

def get_workflowbatches(db, query):
    """
    Return list of documents from 'workflow batches' collection based on query.
    """
    logger.debug("searching 'workflowbatches' collection with query {}".format(
        query
    ))
    return list(db.workflowbatches.find(query))

def put_samples(db, samples):
    """
    Insert each document in list into 'samples' collection.
    """
    for s in samples:
        logger.debug("inserting {} into 'samples' collection".format(s))
        db.samples.insert_one(s)

def put_runs(db, runs):
    """
    Insert each document in list into 'runs' collection.
    """
    for r in runs:
        logger.debug("inserting {} into 'runs' collection".format(r))
        db.runs.insert_one(r)

def put_workflowbatches(db, workflowbatches):
    """
    Insert each document in list into 'workflowbatches' collection.
    """
    for wb in workflowbatches:
        logger.debug("inserting {} into 'workflowbatches' collection".format(
            wb
        ))
        db.workflowbatches.insert_one(wb)
        
