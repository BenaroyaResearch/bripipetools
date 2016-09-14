import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import os
import re

import pytest
import mongomock

from bripipetools import postprocess
from bripipetools import io

@pytest.mark.usefixtures('mock_genomics_server')
class TestOutputStitcher:
    @pytest.fixture(scope='class',
                    params=[('metrics_path', {'type': 'metrics',
                                              'len_outputs': 5,
                                              'lib': 'lib7294_C6VG0ANXX',
                                              'len_data': 5})
                            # ('counts_path', {'type': 'counts',
                            #                  'len_outputs': 1})
                            ])
    def outputstitcherdata(self, request, mock_genomics_server):
        logger.info("[setup] OutputStitcher test instance "
                    "for file type '{}'".format(request.param))

        # GIVEN a OutputStitcher with mock 'genomics' server path to outputs
        outputstitcher = postprocess.OutputStitcher(
            path=mock_genomics_server[request.param[0]]
        )
        def fin():
            logger.info("[teardown] OutputStitcher mock instance")
        request.addfinalizer(fin)
        return (outputstitcher, request.param[1])

    def test_sniff_output_type(self, outputstitcherdata):
        logger.info("test `_sniff_output_type()`")
        (outputstitcher, expected_output) = outputstitcherdata

        # WHEN the file specified by path is read
        output_type = outputstitcher._sniff_output_type()

        # THEN output type should match expected type
        assert(output_type == expected_output['type'])

    def test_get_outputs(self, outputstitcherdata):
        logger.info("test `_get_outputs()`")
        (outputstitcher, expected_output) = outputstitcherdata

        # WHEN the list of output files is collected
        outputs = outputstitcher._get_outputs(outputstitcher.type)

        # THEN the expected number of outputs should be found
        assert(len(outputs) == expected_output['len_outputs'])

    @pytest.mark.parametrize(
        'output,expected',
        [(('metrics', 'htseq'), getattr(io, 'HtseqMetricsFile')),
         (('metrics', 'picard_rnaseq'), getattr(io, 'PicardMetricsFile')),
         (('metrics', 'picard_markdups'), getattr(io, 'PicardMetricsFile')),
         (('metrics', 'picard_align'), getattr(io, 'PicardMetricsFile')),
         (('metrics', 'tophat_stats'), getattr(io, 'TophatStatsFile'))])
    def test_get_parser(self, outputstitcherdata, output, expected):
        logger.info("test `_get_parser()`")
        (outputstitcher, _) = outputstitcherdata

        # WHEN the parser is retrieved given output type and source
        parser = outputstitcher._get_parser(output[0], output[1])

        # THEN the expected number of outputs should be found
        assert(parser == expected)

    def test_read_data(self, outputstitcherdata):
        logger.info("test `_read_data()`")
        (outputstitcher, expected_output) = outputstitcherdata

        # WHEN data from each output file is read and parsed
        outputstitcher._read_data()
        data = outputstitcher.data[expected_output['type']]

        # THEN data should be stored in a dictionary named for the current
        # output type, with a sub-dict for each output source
        assert(len(data[expected_output['lib']])
               == expected_output['len_data'])

    def test_build_table(self, outputstitcherdata):
        logger.info("test `_build_table()`")
        (outputstitcher, expected_output) = outputstitcherdata

        # WHEN data is combined into a table (one row for each sample,
        # plus the header row)
        outputstitcher._read_data()
        table_rows = outputstitcher._build_table()

        assert(len(table_rows) == 2)
        assert(len(set([len(row) for row in table_rows])) == 1)
