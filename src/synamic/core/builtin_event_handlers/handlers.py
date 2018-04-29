# import os
# import shutil
#
#
# def _remove_all(out_path):
#     if os.path.exists(out_path):
#         for a_path in os.listdir(out_path):
#             fp = os.path.join(out_path, a_path)
#             if os.path.isdir(fp):
#                 shutil.rmtree(fp)
#             else:
#                 os.remove(fp)
#
#
# def handler_pre_build(event):
#     """
#      This handler cleans up the output directory before building the project.
#     """
#     synamic = event.subject
#     if synamic.is_root:
#         out_path = synamic.path_tree.get_full_path(event.subject.site_settings.output_dir)
#         _remove_all(out_path)
#
