from synamic.core.contracts import RootModuleContract


class RootSiteConfigModule(RootModuleContract):
    def __init__(self, synamic_config):
        self._synamic_config = synamic_config
        self._module_map = {}
        self._load_default_modules()

    def _load_default_modules(self):
        for mod_name in self._synamic_config.get_meta_content_module_names():
            self.add_module("synamic.site_config_modules" + mod_name)

    def add_module(self, module_path):
        """
        :param module_path: dot separated list of module 
        :return: 
        """
        pass

    def remove_module(self, module_name_or_path):
        del self._module_map[module_name_or_path]

    def get_available_module_names(self):
        return set(self._module_map.keys())

    def get_module_name(self):
        return "synamic.site_config_modules"

    def get_canonical_name(self):
        return "site_config"

    def get_directory_name(self):
        return self.get_canonical_name()


RootModule = RootSiteConfigModule
