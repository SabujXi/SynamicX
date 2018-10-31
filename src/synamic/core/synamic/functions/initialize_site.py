import os


def _synamic_initialize_site(synamic, force, registered_dir_paths, registered_virtual_files):
    self = synamic
    dir_paths = [
        *registered_dir_paths
    ]

    if force:
        for dir_path in dir_paths:
            if not dir_path.exists():
                self.path_tree.makedirs(*dir_path.path_comps)

        for v in registered_virtual_files:
            if not v.file_path.exists():
                with v.file_path.open('w') as f:
                    f.write(v.file_content)
    else:
        if len(os.listdir(self.site_root)) == 0:
            for dir_path in dir_paths:
                if not dir_path.exists():
                    self.path_tree.makedirs(*dir_path.path_comps)

            for v in registered_virtual_files:
                if not v.file_path.exists():
                    with v.file_path.open('w') as f:
                        f.write(v.file_content)
