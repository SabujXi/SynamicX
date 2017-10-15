import os
from synamic import default_site_config
from synamic.main import Synamic


class ModuleSystemFileLoader:
    def __init__(self):
        self.map = {}

    def get_map(self):
        return self.map

    def add_module_files(self, module_name, file_name):
        mset = self.map.get(module_name)
        if mset:
            mset.add(file_name)
        else:
            mset = self.map[module_name] = set()
            mset.add(file_name)

    def list_dir(s):
        base_dir = Synamic.get_synamic_instance().get_base_path()
