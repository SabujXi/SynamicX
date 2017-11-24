import os

from synamic.core.classes.path_tree import PathTree
from synamic.core.contracts import (
    ContentModuleContract,
    MetaContentModuleContract,
    TemplateModuleContract,
)

from synamic.core.exceptions import InvalidModuleType


class SynamicConfig(object):

    def __init__(self, _site_root):
        assert os.path.exists(_site_root), "Base path must not be non existent"
        self.__site_root = _site_root

        # modules
        self.__modules_map = {}

        # setting path tree
        self.__path_tree = PathTree(self)

        # key values
        self.__key_values = {}

        self.__is_loaded = False
        self.__dependency_list = None

        # initializing
        self._populate_with_initial_settings()

    def _populate_with_initial_settings(self):

        # Loading Root Modules
        # for cls in RootModuleInfo.info_list:
        #     _mod = importlib.import_module(cls.dotted_path)
        #     _class = _mod.Module
        #     mod = _class(self)
        #     self.add_module(mod)
        from synamic.content_modules.texts import Texts
        from synamic.template_modules.synamic_template import SynamicTemplate
        self.add_module(Texts(self))
        self.add_module(SynamicTemplate(self))

        # Populating with
        from synamic.core.functions.root_config import get_site_root_settings
        obj = get_site_root_settings(self)
        self.update(obj)

    def __normalize_key(self, key: str):
        return key.lower()

    def get(self, key, default=None):
        key = self.__normalize_key(key)
        return self.__key_values.get(key, default)

    def set(self, key, value):
        key = self.__normalize_key(key)
        self.__key_values[key] = value

    def delete(self, key):
        key = self.__normalize_key(key)
        del self.__key_values[key]

    def update(self, obj: dict):
        for key, value in obj.items():
            self.set(key, value)

    def contains(self, key):
        key = self.__normalize_key(key)
        if key in self.__key_values:
            return True
        return False

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        return self.delete(key)

    def __contains__(self, item):
        return self.contains(item)

    @property
    def modules(self):
        return self.__modules_map.copy()

    def get_module(self, name):
        name = name.lower()
        mod = self.__modules_map[name]
        return mod

    @property
    def path_tree(self):
        return self.__path_tree

    @property
    def is_loaded(self):
        return self.__is_loaded

    def load(self):
        """Load must be called after dependency list is built"""
        assert not self.is_loaded, "Cannot be loaded twice"
        from synamic.core.dependency_resolver import create_dep_list
        self.__dependency_list = create_dep_list(self.modules)

        self.__is_loaded = True

        for mod_name in self.__dependency_list:
            mod = self.__modules_map[mod_name]
            print(":: loading module: %s" % mod.name)
            mod.load()

    def render(self):
        assert self.is_loaded, "Everything must be loaded before render() on config or synamic object can be invoked"
        for mod_name in self.__dependency_list:
            mod = self.__modules_map[mod_name]
            if isinstance(mod, ContentModuleContract):
                print(":: rendering module: %s" % mod.name)
                mod.render()

    def initialize_site_dirs(self):
        dirs = [
            self.path_tree.get_full_path(self.output_dir),
        ]
        for name, mod in self.modules.items():
            dir = self.path_tree.get_full_path(mod.directory_path)
            dirs.append(dir)

        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)


    def add_module(self, mod_obj):
        """Module type can be contract classes or any subclass of them. At the end, the contract class will be the key 
        of the map"""
        if not (isinstance(mod_obj, ContentModuleContract)
                or isinstance(mod_obj, MetaContentModuleContract)
                or isinstance(mod_obj, TemplateModuleContract)):
            raise InvalidModuleType("The module type you provided is not valid: %s" % str(type(mod_obj)))
        assert mod_obj.name not in self.__modules_map
        self.__modules_map[mod_obj.name] = mod_obj

    @property
    def site_root(self):
        return self.__site_root

    @property
    def content_dir(self):
        return "content"

    @property
    def meta_dir(self):
        return "meta_content"

    @property
    def template_dir(self):
        return "templates"

    @property
    def output_dir(self):
        return "_html"

    @property
    def root_config_file_name(self):
        return "settings.yaml"
