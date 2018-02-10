"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import os
import re
import enum
from synamic.core.classes.path_tree import PathTree
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.functions.normalizers import normalize_key, normalize_content_url_path, normalize_relative_file_path
from synamic.core.site_settings.site_settings import SiteSettings
from synamic.core.classes.utils import DictUtils
from synamic.core.type_system.type_system import TypeSystem
from synamic.core.services.model_service import ModelService
from synamic.core.services.template_service import SynamicTemplateService
from synamic.core.classes.path_tree import ContentPath2
from synamic.core.classes.virtual_file import VirtualFile
from synamic.core.classes.url import ContentUrl
from synamic.core.classes.static import StaticContent
from synamic.core.services.content_module_service import MarkedContentService
from synamic.core.services.static_module_service import StaticModuleService
from synamic.core.new_filter.filter_functions import query


@enum.unique
class Key(enum.Enum):
    CONTENTS_BY_ID = 0
    CONTENTS_BY_URL_PATH = 2
    CONTENTS_BY_GENERALIZED_URL_PATH = 3
    CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH = 5
    CONTENTS_SET = 4
    DYNAMIC_CONTENTS = 6


@enum.unique
class EventTypes(enum.Enum):
    NOTHING_NOW = 1


class SynamicConfig(object):
    def __init__(self, site_root):
        assert os.path.exists(site_root), "Base path must not be non existent"
        # assert os.path.exists(os.path.join(site_root, '.synamic')) and os.path.isfile(os.path.join(site_root, '.synamic')), "A file named `.synamic` must exist in the site root to explicitly declare that that is a legal synamic directory - this is to protect accidental modification other dirs: %s" % os.path.join(site_root, '.synamic')
        self.__event_types = EventTypes
        self.__site_root = site_root

        self.__services_list = []
        # Content Map
        self.__content_map = {
            Key.CONTENTS_BY_ID: dict(),
            Key.CONTENTS_BY_URL_PATH: dict(),
            Key.CONTENTS_BY_GENERALIZED_URL_PATH: dict(),
            Key.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH: dict(),
            Key.CONTENTS_SET: set(),
            Key.DYNAMIC_CONTENTS: set()
        }
        # setting path tree
        self.__path_tree = PathTree(self)
        # templates service
        self.__templates = SynamicTemplateService(self)
        # type system
        self.__type_system = TypeSystem(self)
        # model service
        self.__model_service = ModelService(self)
        # Taxonomy
        self.__taxonomy = None
        # Series
        self.__series = None
        # key values
        self.__key_values = {}
        self.__is_loaded = False
        self.__dependency_list = None
        # site settings
        self.__site_settings = None

        # content service
        self.__content_service = MarkedContentService(self)

        # static service
        self.__static_service = StaticModuleService(self)

        # registered directories, path
        self.__registered_dir_paths = set()
        self.__registered_virtual_files = set()
        # initializing modules

    @property
    def event_types(self):
        return self.__event_types

    def register_path(self, dir_path: ContentPath2):
        assert dir_path.is_dir
        if dir_path in self.__registered_dir_paths:
            raise Exception("The same path is already registered")
        self.__registered_dir_paths.add(dir_path)

    def register_virtual_file(self, virtual_file: VirtualFile):
        assert type(virtual_file) is VirtualFile
        if virtual_file in self.__registered_virtual_files:
            raise Exception("Virtual file already exists")
        self.__registered_virtual_files.add(virtual_file)

    @property
    def is_loaded(self):
        return self.__is_loaded

    @property
    def path_tree(self):
        return self.__path_tree

    @property
    def templates(self):
        return self.__templates

    @property
    def type_system(self):
        return self.__type_system

    @property
    def model_service(self):
        return self.__model_service

    @property
    def site_settings(self):
        if self.__site_settings is None:
            self.__site_settings = SiteSettings(self)
        return self.__site_settings

    @property
    @loaded
    def taxonomy(self):
        return self.__taxonomy

    @property
    @loaded
    def series(self):
        return self.__series

    @not_loaded
    def load(self):
        # load templates service
        self.__templates.load()
        # load model service
        self.__model_service.load()

        self.__static_service.load()
        self.__content_service.load()

        self.__is_loaded = True

        # post processing
        for cnt in self.__content_map[Key.DYNAMIC_CONTENTS]:
            cnt.trigger_post_processing()



        # test
        # fil_res = self.filter_content('txt | :sort_by created_on "des"|@one')
        # print(fil_res)

    # Content &| Document Things
    # Content &| Document Things
    # Content &| Document Things
    def add_content(self, content):
        self.add_document(content)

    def add_document(self, document):
        url_object = document.url_object
        # Checking/Validation and addition
        # 1. Content Name

        if not document.is_auxiliary:
            # 4. Content id
            if document.content_id is not None and document.content_id != "":
                parent_d = self.__content_map[Key.CONTENTS_BY_ID]
                # d = DictUtils.get_or_create_dict(parent_d, mod_name)

                assert document.content_id not in parent_d,\
                    "Duplicate content id cannot exist %s" % document.content_id
                parent_d[document.content_id] = document

        # 6. Normalized relative file path
        if document.content_type != document.types.AUXILIARY:
            _path = document.path_object.normalized_listing_relative_path
            # print("Rormalized relative file path: %s" % _path)
            parent_d = self.__content_map[Key.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH]
            # d = DictUtils.get_or_create_dict(parent_d, mod_name)
            assert _path not in parent_d, "Duplicate normalized relative file path: %s" % _path
            parent_d[_path] = document

        # 2. Url path
        assert document.url_object.path not in self.__content_map[Key.CONTENTS_BY_URL_PATH], "Path %s in content map" % document.url_object.path
        self.__content_map[Key.CONTENTS_BY_URL_PATH][document.url_object.path] = document

        # 3. Generalized real path
        assert url_object.norm_real_path not in self.__content_map[Key.CONTENTS_BY_GENERALIZED_URL_PATH],\
            "Multiple resource with the same generalized url cannot coexist"
        self.__content_map[Key.CONTENTS_BY_GENERALIZED_URL_PATH][url_object.norm_real_path] = document

        # 5. Contents set
        self.__content_map[Key.CONTENTS_SET].add(document)

        if document.is_dynamic and not document.is_auxiliary:
            self.__content_map[Key.DYNAMIC_CONTENTS].add(document)

    @property
    def dynamic_contents(self):
        return tuple(self.__content_map[Key.DYNAMIC_CONTENTS])

    def add_static_content(self, file_path):
        assert type(file_path) is ContentPath2
        if file_path.meta_info:
            permalink = file_path.meta_info.get('permalink', None)
            if permalink:
                permalink = permalink.rstrip(r'\/')
                permalink_comps = [x for x in re.split(r'[\\/]+', permalink)]
            else:
                permalink_comps = file_path.relative_path_components

            id = file_path.meta_info.get('id', None)
            cnt_url = ContentUrl(self, permalink_comps, is_dir=False)
        else:
            cnt_url = ContentUrl(self, file_path.relative_path_components, is_dir=False)
            id = None

        if id is None:
            id = "/".join(file_path.relative_path_components)

        static_content = StaticContent(self, file_path, cnt_url, id)
        self.add_content(static_content)
        return static_content

    def get_document_by_id(self, mod_name, doc_id):
        parent_d = self.__content_map[Key.CONTENTS_BY_ID]
        d = DictUtils.get_or_create_dict(parent_d, mod_name)
        assert doc_id in d, "Content id does not exist %s:%s" % (mod_name, d)
        return d[doc_id]

    # URL Things
    # URL Things
    # URL Things
    def get_url(self, parameter):
        """
        Finds a content objects depending on name/content-id/url-path/file-path
        
        Format:
        <content|static>:<id>|<file-path>:...
        
        Examples:
            - content:id:it_39
            - content:file:/text-logo.png
            - content:file:text-logo.png
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

        # 4. Content id
        if search_type == normalize_key('id'):
            parent_d = self.__content_map[Key.CONTENTS_BY_ID]
            assert search_what in parent_d, "Content id does not exist %s:%s:%s %s" % (mod_name, search_type, search_what, parent_d)
            res = parent_d[search_what]

        # 6. Normalized relative file path
        elif search_type == normalize_key('file'):
            # _search_what = os.path.join(mod_name, search_what)
            _search_what = normalize_relative_file_path(search_what)
            parent_d = self.__content_map[Key.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH]
            assert _search_what in parent_d, "File not found with the module and name: %s:%s:%s:  " % (mod_name, search_type, _search_what)
            res = parent_d[_search_what]
        else:
            # Should raise exception or just return None/False
            raise Exception("Url could not be found by url_object name or content id")

        return res.url_object.path

    def get_content_by_url_path(self, path):
        path = normalize_content_url_path(path)
        print("ContentPath requested: %s (normalized)" % path)
        if path in self.__content_map[Key.CONTENTS_BY_URL_PATH]:
            url = self.__content_map[Key.CONTENTS_BY_URL_PATH][path]
        else:
            url = None
        return url

    # Primary Configs
    # Primary Configs
    # Primary Configs
    @property
    def site_root(self):
        return self.__site_root

    @property
    def content_dir(self):
        return 'content'

    @property
    def template_dir(self):
        return 'templates'

    @property
    def meta_dir(self):
        return 'meta'

    @property
    def models_dir(self):
        return 'models'

    @property
    def settings_file_name(self):
        return "settings.txt"

    # Build Things
    # Build Things
    # Build Things
    @loaded
    def build(self):
        self.initialize_site()
        for cont in self.__content_map[Key.CONTENTS_SET]:
            url = cont.url_object
            dir = os.path.join(self.site_root, self.site_settings.output_dir, *url.dir_components)
            if not os.path.exists(dir):
                os.makedirs(dir)

            with url.to_file_path.open('wb') as f:
                stream = cont.get_stream()
                f.write(stream.read())
                stream.close()

    @loaded
    def initialize_site(self):
        dirs = [
            self.site_settings.output_dir
        ]
        # for mod in self.modules:
        #     mod_dir = self.get_module_dir(mod)
        #     dirs.append(mod_dir)
        # execution: directories creation
        for dir in dirs:
            if not self.path_tree.exists(dir):
                self.path_tree.makedirs(dir)

        # creating empty site settings file
        if not self.path_tree.exists(self.settings_file_name):
            with self.path_tree.open_file(self.settings_file_name, 'w') as f:
                pass

    @loaded
    def filter_content(self, filter_txt):
        return query(self, filter_txt)

    def register_event(self, fun):
        pass


