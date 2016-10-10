"""
Compile combined/stitched 'summary' outputs of different types from
batch processing and write to a single CSV file.
"""
import logging
logger = logging.getLogger(__name__)
import os
import csv


class OutputCompiler(object):
    """
    Reads combined output tables from list of file paths and compiles
    into single table, stored in a file at the project level.
    """
    def __init__(self, paths):
        self.paths = paths
