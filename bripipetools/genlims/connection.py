"""
Connect to the GenLIMS Mongo database.
"""
import logging
import os
import ConfigParser

import pymongo

logger = logging.getLogger(__name__)


def connect():
    """
    Check the current environment to determine which database
    parameters to use, then connect to the target database on the
    specified host.

    :return: A database connection object.
    """
    property_file = os.environ.get('DB_PARAM_FILE')
    if property_file is None:
        logger.info("no environmental variable set; using 'default.ini'")
        property_file = 'default.ini'
    else:
        logger.info("property file set: '{}'".format(property_file))

    config = ConfigParser.ConfigParser()
    with open(property_file) as f:
        config.readfp(f)
    db_host = config.get('database', 'db_host')
    db_name = config.get('database', 'db_name')

    logger.info("connecting to database '{}' on host '{}"
                .format(db_name, db_host))
    client = pymongo.MongoClient(db_host, 27017)

    try:
        logger.info("authenticating database '{}'".format(db_name))
        client[db_name].authenticate(config.get('database', 'user'),
                                     config.get('database', 'password'))
    except ConfigParser.NoOptionError:
        logger.warn("no username/password provided; "
                    "attempting to connect anyway")

    return client[db_name]
db = connect()
