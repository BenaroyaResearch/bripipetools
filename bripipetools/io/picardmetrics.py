"""
Class for reading and parsing Picard metrics files.
"""
import logging
logger = logging.getLogger(__name__)
import os
import sys
import re

from bs4 import BeautifulSoup

class PicardMetricsFile(object):

    def __init__(self, path):
        self.path = path
        self.data = {}
        self._read_file()

    def _read_file(self):
        logger.debug("reading file {} as to raw HTML string".format(self.path))
        with open(self.path) as f:
            self.data['raw'] = f.read()

    def _get_table(self):
        raw_html = self.data['raw']
        soup = BeautifulSoup(raw_html, 'html.parser')
        logger.debug("getting metrics table from raw HTML string")
        return soup.findAll('table', attrs={'cellpadding': '3'})

    def _check_table_format(self):
        table = self._get_table()
        if any([re.search(u'\xa0', td.text)
                for tr in table[0].findAll('tr')
                for td in tr.findAll('td')]):
            logger.debug("non-breaking space found in table")
            return 'long'
        else:
            logger.debug("no non-breaking space found in table")
            return 'wide'

    def _parse_long(self):
        table = self._get_table()
        metrics = {}
        for tr in table[0].findAll('tr'):
            for td in tr.findAll('td'):
                if re.search('^([A-Z]+(\_)*)+$', td.text):
                    td_key = td.text.replace('\n', '')
                    logger.debug("found metrics field {}".format(td_key))

                    td_val = td.next_sibling.string.replace(u'\xa0', u'')
                    td_val = td_val.replace('\n', '')
                    logger.debug("with corresponding value {}".format(td_val))

                    if not re.search('[a-z]', td_val.lower()) and len(td_val):
                        td_val = float(td_val)
                    metrics[td_key] = td_val

    def _parse_wide(self):
            table = self._get_table()
            metrics = {}
            for tr in table[0].findAll('tr'):
                for td in tr.findAll('td'):
                    if re.search('^[A-Z]+', td.text):
                        td_keys = td.text.split('\t')
                        td_vals = tr.next_sibling.next_sibling.text.split('\t')
                        td_keys = td_keys[0:len(td_vals)]
                        metrics = {key: float(td_vals[idx])
                                   for idx, key in enumerate(td_keys)}
