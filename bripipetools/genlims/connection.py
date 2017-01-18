"""
Connect to the GenLIMS Mongo database.
"""
import logging
from logging.config import fileConfig
import os
import ConfigParser

import pymongo

config_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'config'
)
fileConfig(os.path.join(config_path, 'logging_config.ini'),
           disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def connect():
    """
    Check the current environment to determine which database
    parameters to use, then connect to the target database on the
    specified host.

    :return: A database connection object.
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        'config'
    )

    property_file = os.environ.get('DB_PARAM_FILE')
    if property_file is None:
        logger.info("No environmental variable set; using 'default.ini'.")
        property_file = 'default.ini'
    else:
        logger.info("property file set: '{}'".format(property_file))

    config = ConfigParser.ConfigParser()

    property_path = os.path.join(config_path, property_file)
    with open(property_path) as f:
        config.readfp(f)
    db_host = config.get('database', 'db_host')
    db_name = config.get('database', 'db_name')

    logger.info("Connecting to database '{}' on host '{}'."
                .format(db_name, db_host))
    client = pymongo.MongoClient(db_host, 27017)

    try:
        logger.info("Authenticating database '{}'.".format(db_name))
        client[db_name].authenticate(config.get('database', 'user'),
                                     config.get('database', 'password'))
    except ConfigParser.NoOptionError:
        logger.info("No username/password provided; "
                    "attempting to connect anyway.")

    return client[db_name]

# db = connect()
