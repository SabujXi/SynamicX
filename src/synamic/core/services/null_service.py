from synamic.core.classes.path_tree import ContentPath2
from synamic.core.classes.virtual_file import VirtualFile


class NullService:
    def __init__(self, cfg):
        cfg.register_virtual_file(
            VirtualFile(
                ContentPath2(cfg.path_tree, cfg.site_root, (cfg.settings_file_name,), is_file=True),
                ''
            )
        )
