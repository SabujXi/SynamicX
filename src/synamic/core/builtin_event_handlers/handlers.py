import os
import shutil


def handler_pre_build(event):
    """
     This handler cleans up the output directory before building the project.
    """
    out_path = event.subject.path_tree.get_full_path(event.subject.site_settings.output_dir)
    if os.path.exists(out_path):
        for a_path in os.listdir(out_path):
            fp = os.path.join(out_path, a_path)
            # print("Removing: %s" % fp)
            if os.path.isdir(fp):
                shutil.rmtree(fp)
            else:
                os.remove(fp)
