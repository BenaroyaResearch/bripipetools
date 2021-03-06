"""
Class for reading and parsing Tophat Stats metrics files.
"""
import logging

logger = logging.getLogger(__name__)


class TophatStatsFile(object):
    """
    Parser to read tables of metrics generated by custom Tophat Stats PE tool,
    stored in a tab-delimited text file.
    """
    def __init__(self, path):
        self.path = path
        self.data = {}

    def _read_file(self):
        """
        Read file into list of raw strings.
        """
        logger.debug("reading file '{}' to raw string list".format(self.path))
        with open(self.path) as f:
            self.data['raw'] = f.readlines()

    def _parse_lines(self):
        """
        Get key-value pairs from text lines and return dictionary.
        """
        metric_keys = {
            'total reads in fastq file': 'fastq_total_reads',
            'reads aligned in sam file': 'reads_aligned_sam',
            'aligned': 'aligned',
            'reads with multiple alignments': 'reads_with_mult_align',
            'of aligned segments had multiple alignments':
                'algn_seg_with_mult_algn'
        }
        logger.debug("{}".format(self.data['raw']))
        self.data['table'] = {metric_keys[l.strip().split('\t')[1]]: 
                              float(l.strip().translate({ord('%'):None}).split('\t')[0])
                              for l in self.data['raw']}

    def parse(self):
        """
        Parse metrics table and return dictionary.
        """
        self._read_file()
        self._parse_lines()
        return self.data['table']
