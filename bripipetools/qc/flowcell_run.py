"""
Summarize metrics/statistics from an Illumina flowcell sequencing run.
"""
# import os
# import re
#
# from bripipetools.io import parsers
#
# class FlowcellRun(object):
#     def __init__(self, flowcell_dir):
#         """
#         Collects, formats, and reports information from metrics files for a
#         flowcell run.
#         """
#         self.flowcell_dir = flowcell_dir
#         self.unaligned_dir = os.path.join(flowcell_dir, 'Unaligned')
#
#     def _find_demux_stats_file(self):
#         """
#         Search the 'Unaligned' folder to locate the 'DemultiplexingStats.xml'
#         file.
#         """
#         unaligned_dir = self.unaligned_dir
#         return [os.path.join(unaligned_dir, f)
#                 for f in os.listdir(unaligned_dir)
#                 if f == 'DemultiplexingStats.xml'][0]
#
#     def _find_demux_summary_file(self, lane):
#         """
#         Search the 'Unaligned' folder to locate the 'DemuxSummary' file
#         corresponding to the specified lane.
#         """
#         unaligned_dir = self.unaligned_dir
#         return [os.path.join(unaligned_dir, f)
#                 for f in os.listdir(unaligned_dir)
#                 if re.search('DemuxSummaryF1L{}'.format(lane), f)][0]
#
#     def _parse_demux_stats_file(self, demux_stats_file):
#         """
#         Import 'DemultiplexingStats.xml' into a Pandas DataFrame object.
#         """
#         return parsers.DemultiplexStatsParser(demux_stats_file).parse_to_df()
#
#     def _parse_demux_summary_file(self, demux_summary_file):
#         """
#         Import 'DemuxSummary[...].txt' as a Pandas DataFrame object.
#         """
#         return parsers.DemuxSummaryParser(demux_summary_file).parse_to_df()
#
#     def convert_barcode_data(self, output='csv'):
#         """
#         Locate files related to barcode/index statistics and save formatted
#         data as the specified output filetype.
#         """
#         demux_stats_file = self._find_demux_stats_file()
#         demux_stats_df = self._parse_demux_stats_file(demux_stats_file)
#         demux_stats_df.to_csv(os.path.join(os.path.dirname(demux_stats_file),
#                                            'demux_stats.csv'))
#
#         for lane in range(1, 8 + 1):
#             lane = str(lane)
#             demux_summary_file = self._find_demux_summary_file(lane)
#             unknown_index_df = self._parse_demux_summary_file(demux_summary_file)
#             unknown_index_df.to_csv(os.path.join(
#                 os.path.dirname(demux_summary_file),
#                 'unknown_indexes_L{}.csv'.format(lane)))
