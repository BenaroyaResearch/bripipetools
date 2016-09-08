"""
Basic operations for the GenLIMS Mongo database.
"""
import logging
import re

logger = logging.getLogger(__name__)

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
    samples = [samples] if not isinstance(samples, list) else samples
    for s in samples:
        logger.debug("inserting {} into 'samples' collection".format(s))
        db.samples.insert_one(s)

def put_runs(db, runs):
    """
    Insert each document in list into 'runs' collection.
    """
    runs = [runs] if not isinstance(runs, list) else runs
    for r in runs:
        logger.debug("inserting {} into 'runs' collection".format(r))
        db.runs.insert_one(r)

def put_workflowbatches(db, workflowbatches):
    """
    Insert each document in list into 'workflowbatches' collection.
    """
    workflowbatches = ([workflowbatches]
                      if not isinstance(workflowbatches, list)
                      else workflowbatches)
    for wb in workflowbatches:
        logger.debug("inserting {} into 'workflowbatches' collection".format(
            wb
        ))
        db.workflowbatches.insert_one(wb)

def create_workflowbatch_id(db, prefix, date):
    """
    Check the 'workflowbatches' collection and construct ID with lowest
    available batch number (i.e., ''<prefix>_<date>_<number>').
    """
    query = {'_id': {'$regex': '{}_{}_.+'.format(prefix, date)}}
    logger.debug("searching 'workflowbatches' collection with query {}"
                 .format(query))
    workflowbatches = get_workflowbatches(db, query)
    num = 1

    if len(workflowbatches):
        while True:
            num_regex = re.compile('_{}$'.format(num))
            logger.debug("searching for matched workflowbatches {} ending in {}"
                         .format(workflowbatches, num))
            if any([num_regex.search(wb['_id']) for wb in workflowbatches]):
                num += 1
                break

    return '{}_{}_{}'.format(prefix, date, num)
