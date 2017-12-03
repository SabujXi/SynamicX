import os
import sys
from synamic.core.classes.path_tree import PathTree
from synamic.core.contracts import (
    ContentModuleContract,
    # MetaContentModuleContract,
    TemplateModuleContract,
    ContentUrlContract
)
from synamic.core.exceptions import InvalidModuleType
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.content_modules.texts import Texts
from synamic.template_modules.synamic_template import SynamicTemplate
from synamic.content_modules.statics import Statics
from synamic.core.functions.normalizers import normalize_key, normalize_content_url_path
from synamic.core.dependency_resolver import create_dep_list
from synamic.core.classes.site_settings import SiteSettings
from collections import namedtuple
import re
from synamic.core.classes.filter_content import filter_dispatcher, parse_rules, combinators


class SynamicConfig(object):
    KEY_URLS_BY_NAME = sys.intern("key-URLS_BY_NAME")
    KEY_URLS_BY_PATH = sys.intern("key-URLS_BY_PATH")
    KEY_URLS_BY_GENERALIZED_REAL_PATH = sys.intern("key-URLS_BY_GENERALIZED_REAL_PATH")
    KEY_URLS_BY_CONTENT_ID = sys.intern("key-URLS_BY_CONTENT_ID")
    KEY_URLS = sys.intern("key-URLS")

    # module types
    MODULE_TYPE_CONTENT = ContentModuleContract
    MODULE_TYPE_TEMPLATE = TemplateModuleContract
    # MODULE_TYPE_META = MetaContentModuleContract

    def __init__(self, site_root):
        assert os.path.exists(site_root), "Base path must not be non existent"
        self.__site_root = site_root

        # modules: key => module.name, value => module
        self.__modules_map = {}
        self.__content_modules_map = {}
        self.__template_modules_map = {}
        # self.__meta_modules_map = {}

        # URL store
        self.__url_map = {
            self.KEY_URLS_BY_NAME: dict(),
            self.KEY_URLS_BY_PATH: dict(),
            self.KEY_URLS_BY_GENERALIZED_REAL_PATH: dict(),
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
                                     # 'META_MODULE_ROOT_DIR',
                                     'TEMPLATE_MODULE_ROOT_DIR'])
        self.__module_root_dirs = ModuleRootDirs(
            'content',
            # 'meta',
            'templates'
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

    # @property
    # @loaded
    # def meta_modules(self):
    #     return list(self.__meta_modules_map.values()).copy()

    @property
    def module_types(self):
        return {self.MODULE_TYPE_CONTENT, self.MODULE_TYPE_TEMPLATE}  #, self.MODULE_TYPE_META}

    def get_module_type(self, mod_instance):
        """Returns the type of the module as the contract class"""
        if isinstance(mod_instance, self.MODULE_TYPE_CONTENT):
            typ = self.MODULE_TYPE_CONTENT
        # elif isinstance(mod_instance, self.MODULE_TYPE_META):
        #     typ = self.MODULE_TYPE_META
        else:
            typ = self.MODULE_TYPE_TEMPLATE
            assert isinstance(mod_instance, self.MODULE_TYPE_TEMPLATE)
        return typ

    def get_module_root_dir(self, mod_instance):
        mod_type = self.get_module_type(mod_instance)
        if mod_type is self.MODULE_TYPE_CONTENT:
            return self.content_dir
        # elif mod_type is self.MODULE_TYPE_META:
        #     return self.meta_dir
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

            mod_dir = self.get_module_dir(mod)
            # if mod.directory_name:
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
            raise InvalidModuleType("The module type you provided is not valid: %s" % str(type(mod_obj)))

        assert mod_name not in self.__modules_map, "Mod name cannot already exist"

        # module name validation
        valid_mod_name_pattern = re.compile(r'^[a-z0-9_-]+$', re.I)
        assert valid_mod_name_pattern.match(mod_obj.name), "Invalid module name that does not go with %s" % valid_mod_name_pattern.pattern()
        # < module name validation

        self.__modules_map[mod_name] = mod_obj

        if mod_type is self.MODULE_TYPE_CONTENT:
            self.__content_modules_map[mod_name] = mod_obj
        # elif mod_type is self.MODULE_TYPE_META:
        #     self.__meta_modules_map[mod_name] = mod_obj
        else:
            self.__template_modules_map[mod_name] = mod_obj

    def get_module(self, mod_name):
        mod_name = normalize_key(mod_name)
        return self.__modules_map[mod_name]

    def add_url(self, url: ContentUrlContract):
        # Checking/Validation and addition
        # 1. Url Name
        if url.name is not None and url.name != "":
            assert url.name not in self.__url_map[self.KEY_URLS_BY_NAME], "Multiple resource with the same url name cannot live together"
            self.__url_map[self.KEY_URLS_BY_NAME][url.name] = url
        # 2. Url path
        assert url.path not in self.__url_map[self.KEY_URLS_BY_PATH]
        self.__url_map[self.KEY_URLS_BY_PATH][url.path] = url

        # 3. Generalized real path
        assert url.generalized_real_path not in self.__url_map[self.KEY_URLS_BY_GENERALIZED_REAL_PATH], "Multiple resource with the same full url cannot coexist"
        self.__url_map[self.KEY_URLS_BY_GENERALIZED_REAL_PATH][url.generalized_real_path] = url

        # 4. Content id
        if url.content.content_id is not None and url.content.content_id != "":
            assert url.content.content_id not in self.__url_map[self.KEY_URLS_BY_CONTENT_ID], "Duplicate content id cannot exist"
            self.__url_map[self.KEY_URLS_BY_CONTENT_ID][url.content.content_id] = url

        # 5. Urls set
        self.__url_map[self.KEY_URLS].add(url)

    def get_url(self, name_or_id):
        """
        Finds a url depending on name/content-id
        
        Search priority:
            1. Name
            2. ID
        """

        # 1. Into name
        name = normalize_key(name_or_id)
        if name in self.__url_map[self.KEY_URLS_BY_NAME]:
            return self.__url_map[self.KEY_URLS_BY_NAME][name]
        # 2. Content id
        elif name_or_id in self.__url_map[self.KEY_URLS_BY_CONTENT_ID]:
            return self.__url_map[self.KEY_URLS_BY_CONTENT_ID][name_or_id]
        else:
            # Should raise exception or just return None/False
            raise Exception("Url could not be found by url name or content id")

    def get_url_by_path(self, path):
        path = normalize_content_url_path(path)
        print("ContentPath requested: %s (normalized)" % path)
        if path in self.__url_map[self.KEY_URLS_BY_PATH]:
            url = self.__url_map[self.KEY_URLS_BY_PATH][path]
        else:
            url = None
        return url

    @property
    def site_root(self):
        return self.__site_root

    @property
    def content_dir(self):
        return self.__module_root_dirs.CONTENT_MODULE_ROOT_DIR

    # @property
    # def meta_dir(self):
    #     return self.__module_root_dirs.META_MODULE_ROOT_DIR

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
        for url in self.__url_map[self.KEY_URLS]:
            print("BUILD():: Going to Write url: ", url.path)
            dir = os.path.join(self.site_root, '_html', *url.dir_components)
            if not os.path.exists(dir):
                os.makedirs(dir)

            fs_path = os.path.join(self.site_root, '_html', url.real_path.lstrip('\\/'))
            with open(fs_path, 'wb') as f:
                stream = url.content.get_stream()
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
        """Filters only is_dynamic content"""
        parsed_rules, sort = parse_rules(filter_txt, self.module_names)
        needed_module_names = set([rule.module_name for rule in parsed_rules])
        contents_map = {}
        for mod_name in needed_module_names:
            contents_map[mod_name] = set()

        for u in self.__url_map[self.KEY_URLS]:
            cnt = u.content
            if cnt.is_dynamic and cnt.module.name in needed_module_names:
                contents_map[cnt.module.name].add(cnt)

        accepted_contents_combination = []

        for rule in parsed_rules:
            contents = contents_map[rule.module_name]
            passed_contents = set()
            for cnt in contents:
                if filter_dispatcher(cnt, rule.filter, rule.operator, rule.value_s):
                    passed_contents.add(cnt)
            accepted_contents_combination.append((passed_contents, rule.combinator))

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
                if previous_combinator == '&&':
                    accepted_contents = accepted_contents.intersection(contents)
                elif previous_combinator == '//':
                    accepted_contents = accepted_contents.union(contents)

                if combinator is None:
                    break
            i += 1
        # sort
        # sorted_content = None
        if not sort:
            # sort by created on in desc
            sorted_content = sorted(accepted_contents, key=lambda cnt: 0 if cnt.created_on is None else cnt.created_on.toordinal, reverse=True)
        else:
            reverse = False
            if sort.order == 'desc':
                reverse = True

            if sort.by_filter == 'created-on':
                sorted_content = sorted(accepted_contents,
                                        key=lambda cnt: 0 if cnt.created_on is None else cnt.created_on.toordinal, reverse=reverse)
            else:
                sorted_content = sorted(accepted_contents, reverse=reverse)
        return sorted_content

    def paginate(self, content_obj, rules_txt, per_page=2):
        cnts = self.filter_content(rules_txt)

        paginated_contents = []

        if cnts:
            print("Contents: %s" % cnts)
            q, r = divmod(len(cnts), per_page)
            divs = q
            if r > 0:
                divs += 1
            print("Divs: %s" % divs)

            for i in range(divs):
                _cts = []
                for j in range(per_page):
                    idx = (i*per_page) + j           #(row * NUMCOLS) + column        #(i * divs) + j
                    print("idx: %s" % idx)
                    if idx >= len(cnts):
                        break
                    print("IDX %s - %s" % (idx, cnts))
                    _cts.append(cnts[idx])
                paginated_contents.append(tuple(_cts))
        print("Paginated contents: %s" % paginated_contents)
        if paginated_contents:
            i = 1
            for page in paginated_contents:
                auxiliary_content = content_obj.create_auxiliary(str(i))  # Currently it is creating paginated content relative to every cloned
                print("Creating auxiliary: %s" % i)
                self.add_url(auxiliary_content.url)
                i += 1






