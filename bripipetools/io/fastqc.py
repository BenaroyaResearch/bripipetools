"""
Class for reading and parsing FastQC report files.
"""
import logging
import re

logger = logging.getLogger(__name__)


class FastQCFile(object):
    """
    Parser to read QC data from a FastQC report, stored in a
    tab-delimited text file.
    """
    def __init__(self, path):
        self.path = path
        self.data = {}

    def _read_file(self):
        """
        Read file into list of raw strings.
        """
        logger.debug("reading file '{}' to raw string list"
                     .format(self.path))
        with open(self.path) as f:
            self.data['raw'] = f.readlines()

    def _clean_header(self, header):
        """
        Extract section header from header line, convert to snake case.
        """
        return re.sub(' ', '_', re.sub('(>>|#)', '', header).lower())

    def _clean_value(self, value):
        """
        Convert to numeric unless value contains text.
        """
        if len(value) and not re.search(r'[^\d.]+', value.lower()):
            return float(value)
        else:
            return value

    def _locate_sections(self):
        """
        Return a dict with section names as keys and tuples of start/end
        line numbers as values.
        """
        section_headers = [self._clean_header(l.rstrip().split('\t')[0])
                           for l in self.data['raw']
                           if re.search('>>(?!END)', l)]
        section_starts = [idx for idx, l in enumerate(self.data['raw'])
                          if re.search('>>(?!END)', l)]
        section_ends = [idx for idx, l in enumerate(self.data['raw'])
                        if re.search('>>(?=END)', l)]
        return dict(zip(section_headers, zip(section_starts, section_ends)))

    def _get_section_status(self, section_name, section_info):
        """
        Return a tuple with the section name and status.
        """
        logger.debug("getting section status for '{}' from line {}"
                     .format(section_name,
                             self.data['raw'][section_info[0]].rstrip()))
        return (section_name,
                self.data['raw'][section_info[0]][2:].rstrip().split('\t')[1])

    def _parse_section_table(self, section_info):
        """
        For the specified section lines, parse tab-delimited columns into
        key-value pairs and return list of tuples.
        """
        section_table = self.data['raw'][section_info[0]:section_info[1]]

        return [tuple([self._clean_header(item)
                       if idx == 0 else self._clean_value(item)
                       for idx, item in enumerate(l.rstrip().split('\t'))])
                for l in section_table[1:]
                if len(l.split('\t')) == 2 and not re.search('#Measure', l)]

    def parse(self):
        """
        Parse file and return key-value pairs as dictionary.
        """
        self._read_file()
        sections = self._locate_sections()
        data = []
        for section_name, section_info in sections.items():
            data.append(self._get_section_status(section_name, section_info))
            if section_name in ['basic_statistics',
                                'sequence_duplication_levels']:
                data += self._parse_section_table(section_info)
        logger.debug("{}".format(data))
        return dict(data)

    def parse_overrepresented_seqs(self):
        """
        Parse table of overrepresented sequences, return as list of
        dictionaries.
        """
        self._read_file()
        sections = self._locate_sections()
        logger.debug("{}".format(sections))
        section_status = self._get_section_status(
            'overrepresented_sequences',
            sections['overrepresented_sequences'])
        if section_status[-1] != 'pass':
            section_start, section_end = sections['overrepresented_sequences']
            overrep_seq_table = self.data['raw'][section_start+1:section_end]

            headers = [self._clean_header(item)
                       for item in overrep_seq_table[0].rstrip().split('\t')]
            return [dict(zip(headers,
                             [self._clean_value(item)
                              for item in l.rstrip().split('\t')]))
                    for l in overrep_seq_table[1:]]
        else:
            return []
