import os
import sys
from synamic.core.classes.path_tree import PathTree
from synamic.core.contracts import (
    ContentModuleContract,
    MetaContentModuleContract,
    TemplateModuleContract,
    ContentUrlContract
)
from synamic.core.exceptions import InvalidModuleType
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.content_modules.texts import Texts
from synamic.template_modules.synamic_template import SynamicTemplate
from synamic.content_modules.statics import Statics
from synamic.core.functions.normalizers import normalize_key
from synamic.core.dependency_resolver import create_dep_list
from synamic.core.classes.site_settings import SiteSettings
from collections import namedtuple


class SynamicConfig(object):
    KEY_URLS_BY_NAME = sys.intern("key-URLS_BY_NAME")
    KEY_URLS_BY_PATH = sys.intern("key-URLS_BY_PATH")
    KEY_URLS_BY_REAL_PATH = sys.intern("key-URLS_BY_REAL_PATH")
    KEY_URLS_BY_CONTENT_ID = sys.intern("key-URLS_BY_CONTENT_ID")
    KEY_URLS = sys.intern("key-URLS")

    # module types
    MODULE_TYPE_CONTENT = ContentModuleContract
    MODULE_TYPE_TEMPLATE = TemplateModuleContract
    MODULE_TYPE_META = MetaContentModuleContract

    def __init__(self, site_root):
        assert os.path.exists(site_root), "Base path must not be non existent"
        self.__site_root = site_root

        # modules: key => module.name, value => module
        self.__modules_map = {}
        self.__content_modules_map = {}
        self.__template_modules_map = {}
        self.__meta_modules_map = {}

        # URL store
        self.__url_map = {
            self.KEY_URLS_BY_NAME: dict(),
            self.KEY_URLS_BY_PATH: dict(),
            self.KEY_URLS_BY_REAL_PATH: dict(),
            self.KEY_URLS_BY_CONTENT_ID: dict(),
            self.KEY_URLS: set()
        }

        # setting path tree
        self.__path_tree = PathTree(self)

        # key values
        self.__key_values = {}
        self.__is_loaded = False
        self.__dependency_list = None

        # site settings
        self.__site_settings = None

        # module root dirs
        # Initiate module root dirs
        ModuleRootDirs = namedtuple("ModuleRootDirs",
                                    ['CONTENT_MODULE_ROOT_DIR',
                                     'META_MODULE_ROOT_DIR',
                                     'TEMPLATE_MODULE_ROOT_DIR'])
        self.__module_root_dirs = ModuleRootDirs(
            'content',
            'meta',
            'template'
        )

        # initializing
        self.__initiate()

    def __initiate(self):
        self.add_module(Texts(self))
        self.add_module(SynamicTemplate(self))
        self.add_module(Statics(self))

        # site settings
        self.__site_settings = SiteSettings(self)
        # obj = get_site_root_settings(self)
        # self.update(obj)

    @property
    def site_settings(self):
        return self.__site_settings

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

    @property
    def module_types(self):
        return {self.MODULE_TYPE_CONTENT, self.MODULE_TYPE_TEMPLATE, self.MODULE_TYPE_META}

    def get_module_type(self, mod_instance):
        """Returns the type of the module as the contract class"""
        if isinstance(mod_instance, self.MODULE_TYPE_CONTENT):
            typ = self.MODULE_TYPE_CONTENT
        elif isinstance(mod_instance, self.MODULE_TYPE_META):
            typ = self.MODULE_TYPE_META
        else:
            typ = self.MODULE_TYPE_TEMPLATE
            assert isinstance(mod_instance, self.MODULE_TYPE_TEMPLATE)
        return typ

    def get_module_root_dir(self, mod_instance):
        mod_type = self.get_module_type(mod_instance)
        if mod_type is self.MODULE_TYPE_CONTENT:
            return self.content_dir
        elif mod_type is self.MODULE_TYPE_META:
            return self.meta_dir
        else:
            return self.template_dir

    def get_module_dir(self, mod_instance):
        return os.path.join(self.get_module_root_dir(mod_instance), mod_instance.directory_name)

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
        self.__dependency_list = create_dep_list(self.__modules_map)

        self.__is_loaded = True

        self.__path_tree.load()

        for mod_name in self.__dependency_list:
            mod = self.__modules_map[mod_name]
            print(":: loading module: %s" % mod.name)
            mod.load()

    @loaded
    def initialize_site_dirs(self):
        dirs = [
            self.path_tree.get_full_path(self.output_dir),
        ]
        for mod in self.modules:
            mod_root_dir = self.get_module_root_dir(mod)
            # if mod.directory_name:
            dir = self.path_tree.get_full_path(self.get_module_dir(mod))
            dirs.append(dir)
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

    def add_module(self, mod_obj):
        """Module type can be contract classes or any subclass of them. At the end, the contract class will be the key 
        of the map"""
        mod_type = self.get_module_type(mod_obj)
        mod_name = normalize_key(mod_type.name)
        if mod_type not in self.module_types:
            raise InvalidModuleType("The module type you provided is not valid: %s" % str(type(mod_obj)))

        assert mod_name not in self.__modules_map, "Mod name cannot already exist"

        self.__modules_map[mod_name] = mod_obj

        if mod_type is self.MODULE_TYPE_CONTENT:
            self.__content_modules_map[mod_name] = mod_obj
        elif mod_type is self.MODULE_TYPE_META:
            self.__meta_modules_map[mod_name] = mod_obj
        else:
            self.__template_modules_map[mod_name] = mod_obj

    def get_module(self, mod_name):
        mod_name = normalize_key(mod_name)
        return self.__modules_map[mod_name]

    def add_url(self, url: ContentUrlContract):
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
        return self.__module_root_dirs.CONTENT_MODULE_ROOT_DIR

    @property
    def meta_dir(self):
        return self.__module_root_dirs.META_MODULE_ROOT_DIR

    @property
    def template_dir(self):
        return self.__module_root_dirs.TEMPLATE_MODULE_ROOT_DIR

    @property
    def output_dir(self):
        return "_html"

    @property
    def settings_file_name(self):
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

    def get(self, key, default=None):
        key = normalize_key(key)
        return self.__key_values.get(key, default)

    def set(self, key, value):
        key = normalize_key(key)
        self.__key_values[key] = value

    def delete(self, key):
        key = normalize_key(key)
        del self.__key_values[key]

    def update(self, obj: dict):
        for key, value in obj.items():
            self.set(key, value)

    def contains(self, key):
        key = normalize_key(key)
        return key in self.__key_values

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        return self.delete(key)

    def __contains__(self, item):
        return self.contains(item)
