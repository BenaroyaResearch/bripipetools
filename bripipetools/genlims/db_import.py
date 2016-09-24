# import json
# 
# from bripipetools.genlims import parsers
# from bripipetools.genlims import db_objects as dbo
#
# class LibListImporter(object):
#
#     def __init__(self, lib_list_file):
#
#         self.lib_list_file = lib_list_file
#
#     def get_fc_run_info(self):
#         fc_dict, lib_dict = parsers.LibListParser(self.lib_list_file).read_lib_list()
#
#         self.runs_objects = []
#         protocol_dict = {}
#         for fc_id, fc_packet in fc_dict.items():
#             run_obj = dbo.FlowcellRun()
#             run_obj._init_from_fc_packet(fc_id, fc_packet)
#             if run_obj._id not in protocol_dict:
#                 protocol_dict[run_obj._id] = run_obj.protocol_id
#
#             self.runs_objects.append(run_obj.to_db())
#
#         self.samples_objects = []
#         for lib_id, lib_packet in lib_dict.items():
#             for p_i in lib_packet:
#                 lib_run_id = p_i.get('run_id')
#                 lib_protocol = protocol_dict.get(lib_run_id, None)
#                 seq_lib_obj = dbo.SequencedLibrarySample(protocol_id = lib_protocol)
#                 seq_lib_obj._init_from_lib_packet(lib_id, p_i)
#
#                 self.samples_objects.append(seq_lib_obj.to_db())
#
#         return self.runs_objects, self.samples_objects
#
#     def write_to_json(self, file_base):
#
#         runs_json_file = file_base + '_fc_runs.json'
#         samples_json_file = file_base + '_seq_libs.json'
#
#         with open(runs_json_file, 'wb+') as f:
#             json.dump(self.runs_objects, f)
#
#         with open(samples_json_file, 'wb+') as f:
#             json.dump(self.samples_objects, f)
