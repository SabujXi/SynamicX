import os

from synamic.core.classes.path_tree import PathTree
from synamic.core.contracts import (
    ContentModuleContract,
    MetaContentModuleContract,
    TemplateModuleContract,
    UrlContract
)

from synamic.core.exceptions import InvalidModuleType
from synamic.core.functions.decorators import loaded, not_loaded


class SynamicConfig(object):

    def __init__(self, _site_root):
        assert os.path.exists(_site_root), "Base path must not be non existent"
        self.__site_root = _site_root

        # modules
        self.__modules_map = {}
        self.__content_modules_map = {}
        self.__template_modules_map = {}
        self.__meta_modules_map = {}

        # URL store
        self.__url_map = {
            "names": set(),
            "urls": {}  # key => full url path, value => url object
        }

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
        from synamic.content_modules.statics import Statics
        self.add_module(Texts(self))
        self.add_module(SynamicTemplate(self))
        self.add_module(Statics(self))

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
    @loaded
    def modules(self):
        return list(self.__modules_map.values()).copy()

    @property
    @loaded
    def content_modules(self):
        return list(self.__content_modules_map.values()).copy()

    @property
    @loaded
    def template_modules(self):
        return list(self.__template_modules_map.values()).copy()

    @property
    @loaded
    def meta_modules(self):
        return list(self.__meta_modules_map.values()).copy()

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

    @not_loaded
    def load(self):
        # """Load must be called after dependency list is built"""
        # assert not self.is_loaded, "Cannot be loaded twice"
        from synamic.core.dependency_resolver import create_dep_list
        self.__dependency_list = create_dep_list(self.__modules_map)

        self.__is_loaded = True

        self.__path_tree.load()

        for mod_name in self.__dependency_list:
            mod = self.__modules_map[mod_name]
            print(":: loading module: %s" % mod.name)
            mod.load()


    # def render(self):
    #     assert self.is_loaded, "Everything must be loaded before render() on config or synamic object can be invoked"
    #     for mod_name in self.__dependency_list:
    #         mod = self.__modules_map[mod_name]
    #         if isinstance(mod, ContentModuleContract):
    #             print(":: rendering module: %s" % mod.name)
    #             mod.render()

    def initialize_site_dirs(self):
        dirs = [
            self.path_tree.get_full_path(self.output_dir),
        ]
        for mod in self.modules:
            if isinstance(mod, ContentModuleContract):
                mod_root_dir = self.content_dir
            elif issubclass(mod, MetaContentModuleContract):
                mod_root_dir = self.meta_dir
            else:
                mod_root_dir = self.template_dir
                assert isinstance(mod, TemplateModuleContract)

            if mod.directory_name:
                dir = self.path_tree.get_full_path(mod_root_dir, mod.directory_name)
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

        if isinstance(mod_obj, ContentModuleContract):
            self.__content_modules_map[mod_obj.name] = mod_obj
        elif issubclass(mod_obj, MetaContentModuleContract):
            self.__meta_modules_map[mod_obj.name] = mod_obj
        else:
            assert isinstance(mod_obj, TemplateModuleContract)
            self.__template_modules_map[mod_obj.name] = mod_obj

    def add_url(self, url: UrlContract):
        if url.name is not None and url.name != "":
            print("Adding url name: ", url.name)
            assert url.name not in self.__url_map["names"], "Multiple resource with the same url name cannot live together"
        assert url.path not in self.__url_map["urls"], "Multiple resource with the same full url cannot coexist"

        if url.name is not None or url.name != "":
            self.__url_map["names"].add(url.name)
        self.__url_map["urls"][url.path] = url

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

    @property
    def hostname(self):
        return "example.com"

    @property
    def hostname_scheme(self):
        return "http"

    @property
    def host_address(self):
        return self.hostname_scheme + "://" + self.hostname

    @loaded
    def build(self):
        self.initialize_site_dirs()
        for url in self.__url_map['urls'].values():
            print("Going to Write url: ", url.path)
            dir = os.path.join(self.site_root, '_html', *url.dir_components)
            if not os.path.exists(dir):
                os.makedirs(dir)

            fs_path = os.path.join(self.site_root, '_html', url.real_path.lstrip('\\/'))
            with open(fs_path, 'wb') as f:
                stream = url.content.get_stream()
                f.write(stream.read())
                print("Wrote: %s" % f.name)
                stream.close()
