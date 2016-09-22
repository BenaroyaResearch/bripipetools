import logging
import os
import sys

import argparse

import _mypath
from bripipetools import genlims
from bripipetools import dbify

def parse_input_args(parser=None):
    parser.add_argument('-p', '--import_path',
                        required=True,
                        default=None,
                        help=("path to flowcell run folder - e.g., "
                              "/mnt/genomics/Illumina/"
                              "150218_D00565_0081_BC5UF5ANXX/ - "
                              "or workflow batch file"))
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help=("Set logging level to debug"))

    # Parse and collect input arguments
    args = parser.parse_args()

    return parser.parse_args()

def main(argv):
    parser = argparse.ArgumentParser()
    args = parse_input_args(parser)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("importing data based on path {}"
                .format(args.import_path))
    dbify.ImportManager(path=args.import_path, db=genlims.db).run()

if __name__ == "__main__":
   main(sys.argv[1:])
