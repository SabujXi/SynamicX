import os
from synamic.core.classes.path_tree import PathTree
from synamic.core.contracts import (
    ContentModuleContract,
    TemplateModuleContract,
)
from synamic.core.exceptions import InvalidModuleType
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.content_modules.text import TextModule
from synamic.content_modules.home import HomeModule
from synamic.template_modules.synamic_template import SynamicTemplate
from synamic.content_modules.static import StaticModule
from synamic.core.functions.normalizers import normalize_key, normalize_content_url_path, normalize_relative_file_path
from synamic.core.dependency_resolver import create_dep_list
from synamic.core.classes.site_settings import SiteSettings
from collections import namedtuple
import re
# from synamic.core.functions.filter_content2 import filter_dispatcher, parse_rules
# from synamic.core.contracts.content import content_is_dynamic
import enum
from synamic.core.contracts.document import MarkedDocumentContract
from synamic.core.classes.frontmatter import DefaultFrontmatterValueParsers
from synamic.core.classes.utils import DictUtils
from synamic.core.functions import query_compiler


class SynamicConfig(object):
    @enum.unique
    class KEY(enum.Enum):
        CONTENTS_BY_ID = 0
        CONTENTS_BY_NAME = 1
        CONTENTS_BY_URL_PATH = 2
        CONTENTS_BY_GENERALIZED_URL_PATH = 3
        CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH = 5
        CONTENTS_SET = 4

    # module types
    MODULE_TYPE_CONTENT = ContentModuleContract
    MODULE_TYPE_TEMPLATE = TemplateModuleContract

    def __init__(self, site_root):
        assert os.path.exists(site_root), "Base path must not be non existent"
        assert os.path.exists(os.path.join(site_root, '.synamic')) and os.path.isfile(os.path.exists(os.path.join(site_root, '.synamic'))), "A file named `.synamic` must exist in the site root to explicitly declare that that is a legal synamic directory - this is to protect accidental modification other dirs"
        self.__site_root = site_root

        # modules: key => module.name, value => module
        self.__modules_map = {}
        self.__content_modules_map = {}
        self.__template_modules_map = {}
        # self.__meta_modules_map = {}

        # Content Map
        self.__content_map = {
            self.KEY.CONTENTS_BY_ID: dict(),
            self.KEY.CONTENTS_BY_NAME: dict(),
            self.KEY.CONTENTS_BY_URL_PATH: dict(),
            self.KEY.CONTENTS_BY_GENERALIZED_URL_PATH: dict(),
            self.KEY.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH: dict(),
            self.KEY.CONTENTS_SET: set()
        }

        # setting path tree
        self.__path_tree = PathTree(self)

        # key values
        self.__key_values = {}
        self.__is_loaded = False
        self.__dependency_list = None

        # site settings
        self.__site_settings = None

        self.__frontmatter_value_parser = {}

        # module root dirs
        # Initiate module root dirs
        ModuleRootDirs = namedtuple("ModuleRootDirs",
                                    ['CONTENT_MODULE_ROOT_DIR',
                                     'TEMPLATE_MODULE_ROOT_DIR'])
        self.__module_root_dirs = ModuleRootDirs(
            'content',
            'templates'
        )

        # initializing
        self.__initiate()

    def __initiate(self):
        self.add_module(TextModule(self))
        self.add_module(HomeModule(self))
        self.add_module(SynamicTemplate(self))
        self.add_module(StaticModule(self))

        # site settings
        self.__site_settings = SiteSettings(self)

    @property
    def site_settings(self):
        return self.__site_settings

    @property
    @loaded
    def modules(self):
        return list(self.__modules_map.values()).copy()

    @property
    @loaded
    def module_names(self):
        return set(self.__modules_map.keys()).copy()

    @property
    @loaded
    def content_modules(self):
        return list(self.__content_modules_map.values()).copy()

    @property
    @loaded
    def template_modules(self):
        return list(self.__template_modules_map.values()).copy()

    @property
    def module_types(self):
        return {self.MODULE_TYPE_CONTENT, self.MODULE_TYPE_TEMPLATE}

    def get_module_type(self, mod_instance):
        """Returns the type of the module_object as the contract class"""
        if isinstance(mod_instance, self.MODULE_TYPE_CONTENT):
            typ = self.MODULE_TYPE_CONTENT
        else:
            typ = self.MODULE_TYPE_TEMPLATE
            assert isinstance(mod_instance, self.MODULE_TYPE_TEMPLATE)
        return typ

    def get_module_root_dir(self, mod_instance):
        mod_type = self.get_module_type(mod_instance)
        if mod_type is self.MODULE_TYPE_CONTENT:
            return self.content_dir
        else:
            return self.template_dir

    def get_module_dir(self, mod_instance):
        return os.path.join(self.get_module_root_dir(mod_instance), mod_instance.name)

    @property
    def path_tree(self):
        return self.__path_tree

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        # """Load must be called after dependency list is built"""
        self.__dependency_list = create_dep_list(self.__modules_map)

        # Registering front matter value parsers
        DefaultFrontmatterValueParsers.register_default_value_parsers(self)

        self.__is_loaded = True

        self.__path_tree.load()

        for mod_name in self.__dependency_list:
            mod = self.__modules_map[mod_name]
            print(":: loading module_object: %s" % mod.name)
            mod.load()

    @loaded
    def initialize_site_dirs(self):
        dirs = [
            self.path_tree.get_full_path(self.output_dir),
        ]
        for mod in self.modules:

            mod_dir = self.get_module_dir(mod)
            dir = self.path_tree.get_full_path(mod_dir)
            dirs.append(dir)
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

    def add_module(self, mod_obj):
        """Module type can be contract classes or any subclass of them. At the end, the contract class will be the key 
        of the map"""

        mod_type = self.get_module_type(mod_obj)
        mod_name = normalize_key(mod_obj.name)
        if mod_type not in self.module_types:
            raise InvalidModuleType("The module_object type you provided is not valid: %s" % str(type(mod_obj)))

        assert mod_name not in self.__modules_map, "Mod name cannot already exist"

        # module name validation
        valid_mod_name_pattern = re.compile(r'^[a-z0-9_-]+$', re.I)
        assert valid_mod_name_pattern.match(mod_obj.name), "Invalid module_object name that does not go with %s" % valid_mod_name_pattern.pattern()
        # < module name validation

        self.__modules_map[mod_name] = mod_obj

        if mod_type is self.MODULE_TYPE_CONTENT:
            self.__content_modules_map[mod_name] = mod_obj
        else:
            self.__template_modules_map[mod_name] = mod_obj

    def get_module(self, mod_name):
        mod_name = normalize_key(mod_name)
        return self.__modules_map[mod_name]

    def add_content(self, content):
        self.add_document(content)

    def add_document(self, document: MarkedDocumentContract):
        url_object = document.url_object
        mod_name = normalize_key(document.module_object.name)
        # Checking/Validation and addition
        # 1. Content Name

        if document.content_name is not None and document.content_name != "":
            parent_d = self.__content_map[self.KEY.CONTENTS_BY_NAME]
            d = DictUtils.get_or_create_dict(parent_d, mod_name)
            assert document.content_name not in d,\
                "Multiple resource with the same content name cannot live together"
            d[document.content_name] = document

        # 4. Content id
        if document.content_id is not None and document.content_id != "":
            parent_d = self.__content_map[self.KEY.CONTENTS_BY_ID]
            d = DictUtils.get_or_create_dict(parent_d, mod_name)
            assert document.content_id not in d,\
                "Duplicate content id cannot exist"
            print("Content id adding %s" % document.content_id)
            # input()
            d[document.content_id] = document

        # 6. Normalized relative file path
        if document.content_type != document.types.AUXILIARY:
            _path = document.path_object.normalized_relative_path
            # print("Rormalized relative file path: %s" % _path)
            parent_d = self.__content_map[self.KEY.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH]
            d = DictUtils.get_or_create_dict(parent_d, mod_name)
            assert _path not in d, "Duplicate normalized relative file path: %s" % _path
            d[_path] = document

        # 2. Url path
        assert document.url_object.path not in self.__content_map[self.KEY.CONTENTS_BY_URL_PATH]
        self.__content_map[self.KEY.CONTENTS_BY_URL_PATH][document.url_object.path] = document

        # 3. Generalized real path
        assert url_object.generalized_real_path not in self.__content_map[self.KEY.CONTENTS_BY_GENERALIZED_URL_PATH],\
            "Multiple resource with the same generalized url cannot coexist"
        self.__content_map[self.KEY.CONTENTS_BY_GENERALIZED_URL_PATH][url_object.generalized_real_path] = document

        # 5. Contents set
        self.__content_map[self.KEY.CONTENTS_SET].add(document)

    def get_url(self, parameter):
        """
        Finds a content objects depending on name/content-id/url-path/file-path
        
        Format:
        <module-name>:<id>|<name>|<file-path>:...
        
        Examples:
            - text:id:it_39
            - text:id:it_39
            - text:name:got-it-1
            - text:file:/text-logo.png
            - text:file:text-logo.png
            - static:file:home-logo.png
        """
        parts = parameter.split(':')
        assert len(parts) == 3, "Invalid geturl parameter"

        # 1. Into name
        mod_name = normalize_key(parts[0])
        search_type = normalize_key(parts[1])
        search_what = parts[2].strip()
        print("Search what: %s" % search_what)

        if search_type == normalize_key('file'):
            search_what = normalize_relative_file_path(search_what)

        if search_type == normalize_key('name'):
            parent_d = self.__content_map[self.KEY.CONTENTS_BY_NAME]
            d = DictUtils.get_or_create_dict(parent_d, mod_name)
            res = d[search_what]

        # 4. Content id
        elif search_type == normalize_key('id'):
            parent_d = self.__content_map[self.KEY.CONTENTS_BY_ID]
            d = DictUtils.get_or_create_dict(parent_d, mod_name)
            assert search_what in d, "Content id does not exist %s:%s:%s %s" % (mod_name, search_type, search_what, d)
            res = d[search_what]

        # 6. Normalized relative file path
        elif search_type == normalize_key('file'):
            parent_d = self.__content_map[self.KEY.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH]
            d = DictUtils.get_or_create_dict(parent_d, mod_name)
            # for key in d.keys():
            #     print(key)
            assert search_what in d, "File not found with the module and name: %s:%s:%s:  " % (mod_name, search_type, search_what)
            res = d[search_what]
        else:
            # Should raise exception or just return None/False
            raise Exception("Url could not be found by url_object name or content id")

        return res.url_object.path

    def get_content_by_url_path(self, path):
        path = normalize_content_url_path(path)
        print("ContentPath requested: %s (normalized)" % path)
        if path in self.__content_map[self.KEY.CONTENTS_BY_URL_PATH]:
            url = self.__content_map[self.KEY.CONTENTS_BY_URL_PATH][path]
        else:
            url = None
        return url

    @property
    def site_root(self):
        return self.__site_root

    @property
    def content_dir(self):
        return self.__module_root_dirs.CONTENT_MODULE_ROOT_DIR

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

        for cont in self.__content_map[self.KEY.CONTENTS_SET]:
            url = cont.url_object
            print("BUILD():: Going to Write cont: ", url.path)
            dir = os.path.join(self.site_root, '_html', *url.dir_components)
            if not os.path.exists(dir):
                os.makedirs(dir)

            fs_path = os.path.join(self.site_root, '_html', url.real_path.lstrip('\\/'))
            with open(fs_path, 'wb') as f:
                stream = cont.get_stream()
                f.write(stream.read())
                print("BUILD():: Wrote: %s" % f.name)
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

    @loaded
    def filter_content(self, filter_txt):
        query_container = query_compiler.get_query_container(filter_txt)
        queries = query_container.queries

        # parsed_rules, sort = parse_rules(filter_txt, self.module_names)
        needed_module_names = set([rule.module_name for rule in queries])
        contents_map = {}
        for mod_name in needed_module_names:
            contents_map[mod_name] = set()

        for cont in self.__content_map[self.KEY.CONTENTS_SET]:
            cnt = cont
            if cnt.is_dynamic and cnt.module_object.name in needed_module_names:
                contents_map[cnt.module_object.name].add(cnt)

        accepted_contents_combination = []

        for query in queries:
            contents = contents_map[query.module_name]
            passed_contents = set()
            for cnt in contents:
                if query_compiler.filter_dispatcher(query, cnt):
                    passed_contents.add(cnt)
            accepted_contents_combination.append((passed_contents, query.combinator))

        accepted_contents = set()
        i = 0
        previous_combinator = None
        while i < len(accepted_contents_combination):

            contents = accepted_contents_combination[i][0]
            combinator = accepted_contents_combination[i][1]
            if previous_combinator is None:
                accepted_contents.update(contents)
                if combinator is None:
                    break
                previous_combinator = combinator
            else:
                if previous_combinator == '&':
                    accepted_contents = accepted_contents.intersection(contents)
                elif previous_combinator == '|':
                    accepted_contents = accepted_contents.union(contents)

                if combinator is None:
                    break
            i += 1
        # sort
        # sorted_content = None
        if not query_container.sort_filter_name:
            # sort by created on in desc
            sorted_content = sorted(accepted_contents, key=lambda _cont: 0 if _cont.created_on is None else _cont.created_on.toordinal(), reverse=True)
        else:
            reverse = False
            if query_container.sort_filter_order == 'desc':
                reverse = True

            if query_container.sort_filter_name == 'created-on':
                sorted_content = sorted(accepted_contents,
                                        key=lambda cnt: 0 if cnt.created_on is None else cnt.created_on.toordinal, reverse=reverse)
            else:
                sorted_content = sorted(accepted_contents, reverse=reverse)
        print("\n\n\n%s\n\n\n" % sorted_content)
        return sorted_content

    def register_frontmatter_value_parser(self, key, _callable):
        key = normalize_key(key)
        assert key not in self.__frontmatter_value_parser, 'A parser is already there for key: %s' % key
        self.__frontmatter_value_parser[key] = _callable

    def get_frontmatter_value_parser(self, key):
        key = normalize_key(key)
        return self.__frontmatter_value_parser[key]

    def enqueue_static_file(self, mod_obj, path):
        mod = self.get_module('static')
        mod.enqueue_file(mod_obj, path)

