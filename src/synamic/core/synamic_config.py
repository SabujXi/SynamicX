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

from synamic.core.builtin_event_handlers.handlers import handler_pre_build
from synamic.core.classes.path_tree import ContentPath2
from synamic.core.classes.path_tree import PathTree
from synamic.core.classes.static import StaticContent
from synamic.core.classes.url import ContentUrl
from synamic.core.classes.utils import DictUtils
from synamic.core.classes.virtual_file import VirtualFile
from synamic.core.enums import Key
from synamic.core.event_system.events import EventTypes, EventSystem, Event, Handler
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.functions.normalizers import normalize_key  # , normalize_relative_file_path
from synamic.core.new_filter.filter_functions import query_by_synamic_4_dynamic_contents
from synamic.core.services.category_service import CategoryService
from synamic.core.services.content.content_module_service import MarkedContentService
from synamic.core.services.menu_service import MenuService
from synamic.core.services.model_service import ModelService
from synamic.core.services.null_service import NullService
from synamic.core.services.static_module_service import StaticModuleService
from synamic.core.services.tags_service import TagsService
from synamic.core.services.template_service import SynamicTemplateService
from synamic.core.site_settings.site_settings import SiteSettings
from synamic.core.type_system.type_system import TypeSystem
from synamic.core.exceptions.synamic_exceptions import *


class SynamicConfig(object):
    def __init__(self, site_root):
        # acquire trigger function of event system
        self.__event_trigger = EventSystem._get_trigger()
        # registered directories, path
        self.__registered_dir_paths = set()
        self.__registered_virtual_files = set()
        assert os.path.exists(site_root), "Base path must not be non existent"
        self.__site_root = site_root

        self.__services_list = []
        # Content Map
        self.__content_map = {
            Key.CONTENTS_BY_ID: dict(),
            Key.CONTENTS_BY_CONTENT_URL: dict(),
            Key.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH: dict(),
            Key.CONTENTS_SET: set(),
            Key.DYNAMIC_CONTENTS: set()
        }
        # setting path tree
        self.__path_tree = PathTree(self)
        # tags
        self.__tags = TagsService(self)
        # categories
        self.__categories = CategoryService(self)
        # menus
        self.__menus = MenuService(self)
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
        self.__site_settings = SiteSettings(self)

        # content service
        self.__content_service = MarkedContentService(self)

        # static service
        self.__static_service = StaticModuleService(self)

        # null service for adding some virtual files
        NullService(self)

    @property
    def urls(self):
        return self.__content_map[Key.CONTENTS_BY_URL_PATH].copy()

    @property
    def tags(self):
        return self.__tags

    @property
    def categories(self):
        return self.__categories

    @property
    def menus(self):
        return self.__menus

    def register_path(self, dir_path: ContentPath2):
        assert dir_path.is_dir
        # print(self.__registered_dir_paths)
        if dir_path in self.__registered_dir_paths:
            raise SynamicException("The same path (%s) is already registered" % self.path_tree.get_full_path(dir_path.path_components))
        self.__registered_dir_paths.add(dir_path)

    def register_virtual_file(self, virtual_file: VirtualFile):
        assert type(virtual_file) is VirtualFile
        if virtual_file in self.__registered_virtual_files:
            raise SynamicException("Virtual file (%s) already exists" % virtual_file.file_path)
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
    def content_service(self):
        return self.__content_service

    @property
    def site_settings(self):
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
        assert os.path.exists(os.path.join(self.site_root, '.synamic')) and os.path.isfile(os.path.join(self.site_root, '.synamic')), "A file named `.synamic` must exist in the site root to explicitly declare that that is a legal synamic directory - this is to protect accidental modification other dirs: %s" % os.path.join(self.site_root, '.synamic')
        self.__site_settings.load()
        # tags
        self.__tags.load()
        # categories
        self.__categories.load()
        # menus
        self.__menus.load()
        # load templates service
        self.__templates.load()
        # load model service
        self.__model_service.load()

        self.__static_service.load()

        # content load
        self.__content_service.load()

        self.__event_trigger(
            EventTypes.CONTENT_POST_LOAD,
            Event(self)
        )

        self.__is_loaded = True

        # post processing
        # for cnt in self.__content_map[Key.DYNAMIC_CONTENTS]:
        #     cnt.trigger_post_processing()

            # test
            # fil_res = self.filter_content('txt | :sort_by created_on "des"|@one')
            # print(fil_res)

    # Content &| Document Things
    # Content &| Document Things
    # Content &| Document Things
    def add_content(self, content):
        self.add_document(content)

    def add_document(self, document):
        assert document.is_auxiliary is False
        # 1. Content id
        if document.id is not None and document.id != "":
            parent_d = self.__content_map[Key.CONTENTS_BY_ID]
            # d = DictUtils.get_or_create_dict(parent_d, mod_name)

            assert document.id not in parent_d, \
                "Duplicate content id cannot exist %s" % document.id
            parent_d[document.id] = document

        # 2. Normalized relative file path
        _path = document.path_object.norm_relative_path
        parent_d = self.__content_map[Key.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH]
        assert _path not in parent_d, "Duplicate normalized relative file path: %s" % _path
        parent_d[_path] = document

        # 3. Content Url Object
        assert document.url_object not in self.__content_map[
            Key.CONTENTS_BY_CONTENT_URL], "Path %s in content map" % document.url_object.path
        self.__content_map[Key.CONTENTS_BY_CONTENT_URL][document.url_object] = document

        # 4. Contents set
        self.__content_map[Key.CONTENTS_SET].add(document)

        if document.is_dynamic:
            self.__content_map[Key.DYNAMIC_CONTENTS].add(document)

    def add_auxiliary_content(self, document):
        assert document.is_auxiliary is True
        # 3. Content Url Object
        assert document.url_object not in self.__content_map[
            Key.CONTENTS_BY_CONTENT_URL], "Path %s in content map" % document.url_object.path
        self.__content_map[Key.CONTENTS_BY_CONTENT_URL][document.url_object] = document

        # 4. Contents set
        self.__content_map[Key.CONTENTS_SET].add(document)

    @property
    def dynamic_contents(self):
        return tuple(self.__content_map[Key.DYNAMIC_CONTENTS])

    def add_static_content(self, file_path):
        assert type(file_path) is ContentPath2
        static_content = StaticContent(self, file_path)
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
        # print("Search what: %s" % search_what)

        # 4. Content id
        if search_type == normalize_key('id'):
            parent_d = self.__content_map[Key.CONTENTS_BY_ID]
            assert search_what in parent_d, "Content id does not exist %s:%s:%s %s" % (mod_name, search_type, search_what, parent_d)
            res = parent_d[search_what]

        # 6. Normalized relative file path
        elif search_type == normalize_key('file'):
            # _search_what = os.path.join(mod_name, search_what)
            _search_what = search_what.lower().lstrip(r'\/')
            _search_what = mod_name + '/' + _search_what
            _search_what = os.path.join(*self.__path_tree.to_components(_search_what))
            parent_d = self.__content_map[Key.CONTENTS_BY_NORMALIZED_RELATIVE_FILE_PATH]
            assert _search_what in parent_d, "File not found with the module and name: %s:%s:%s:  " % (mod_name, search_type, _search_what)
            res = parent_d[_search_what]
        else:
            # Should raise exception or just return None/False
            raise GetUrlFailed("Url could not be found for: %s" % parameter)

        return res.url_object.path

    def get_content_by_content_url(self, curl: ContentUrl):
        assert type(curl) is ContentUrl
        if curl in self.__content_map[Key.CONTENTS_BY_CONTENT_URL]:
            cont = self.__content_map[Key.CONTENTS_BY_CONTENT_URL][curl]
        else:
            cont = None
        return cont

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
        out_path = self.path_tree.create_path(self.site_settings.output_dir)
        if not out_path.exists():
            self.path_tree.makedirs(out_path.path_components)

        EventSystem.add_event_handler(
            EventTypes.PRE_BUILD,
            Handler(handler_pre_build)
        )

        self.__event_trigger(
            EventTypes.PRE_BUILD,
            Event(self)
        )
        # ^ event section

        # real work begins
        self.initialize_site()
        for cont in self.__content_map[Key.CONTENTS_SET]:
            url = cont.url_object
            dir = os.path.join(self.site_root, self.site_settings.output_dir, *url.dir_components)
            if not os.path.exists(dir):
                os.makedirs(dir)

            with url.to_content_path.open('wb') as f:
                stream = cont.get_stream()
                f.write(stream.read())
                stream.close()

    def initialize_site(self, force=False):
        dir_paths = [
            *self.__registered_dir_paths
        ]

        if force:
            for dir_path in dir_paths:
                if not dir_path.exists():
                    self.path_tree.makedirs(*dir_path.path_components)

            for v in self.__registered_virtual_files:
                if not v.file_path.exists():
                    with v.file_path.open('w') as f:
                        f.write(v.file_content)
        else:
            if len(os.listdir(self.site_root)) == 0:
                for dir_path in dir_paths:
                    if not dir_path.exists():
                        self.path_tree.makedirs(*dir_path.path_components)

                for v in self.__registered_virtual_files:
                    if not v.file_path.exists():
                        with v.file_path.open('w') as f:
                            f.write(v.file_content)

    @loaded
    def filter_content(self, filter_txt):
        return query_by_synamic_4_dynamic_contents(self, filter_txt)



