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

from synamic.core.contracts.synamic_contract import SynamicContract
from synamic.core.event_system.events import EventTypes, EventSystem, Event
from synamic.core.filesystem.path_tree import ContentPath2
from synamic.core.filesystem.path_tree import PathTree
from synamic.core.filesystem.virtual_file import VirtualFile
from synamic.core.query_systems.filter_functions import query_by_synamic_4_dynamic_contents
from synamic.core.services.category.category_service import CategoryService
from synamic.core.services.content.content_module_service import MarkedContentService
from synamic.core.services.menu.menu_service import MenuService
from synamic.core.services.model.model_service import ModelService
from synamic.core.services.null.null_service import NullService
from synamic.core.services.static.static_module_service import StaticModuleService
from synamic.core.services.tags.tags_service import TagsService
from synamic.core.services.template.template_service import SynamicTemplateService
from synamic.core.site_settings.site_settings import SiteSettings
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.synamic._synamic_enums import Key
from synamic.core.synamic.functions.add_auxiliary_content import synamic_add_auxiliary_content
from synamic.core.synamic.functions.add_document import synamic_add_document
from synamic.core.synamic.functions.add_static_content import synamic_add_static_content
from synamic.core.synamic.functions.build import _synamic_build
from synamic.core.synamic.functions.get_content_by_url import synamic_get_content_by_url
from synamic.core.synamic.functions.get_document_by_id import synamic_get_document_by_id
from synamic.core.synamic.functions.get_url import synamic_get_url
from synamic.core.synamic.functions.initialize_site import _synamic_initialize_site
from synamic.core.synamic.functions.register_path import synamic_register_path
from synamic.core.synamic.functions.register_virtual_file import synamic_register_virtual_file
from synamic.core.type_system.type_system import TypeSystem
from synamic.core.urls.url import ContentUrl


class Synamic(SynamicContract):
    __slots__ = ('__event_trigger', '__registered_dir_paths', '__registered_virtual_files',
                 '__site_root', '__services_list', '__content_map', '__path_tree', '__tags',
                 '__categories', '__menus', '__templates', '__type_system', '__model_service', '__taxonomy',
                 '__series', '__key_values', '__is_loaded', '__dependency_list', '__site_settings', '__content_service',
                 '__static_service', '__event_system')

    __site_root_paths = set()

    @property
    def event_system(self) -> EventSystem:
        return self.__event_system

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
        return synamic_register_path(self, dir_path, self.__registered_dir_paths)

    def register_virtual_file(self, virtual_file: VirtualFile):
        return synamic_register_virtual_file(self, virtual_file, self.__registered_virtual_files)

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

    # Content &| Document Things
    def add_content(self, content):
        self.add_document(content)

    def add_document(self, document):
        return synamic_add_document(self, document, self.__content_map)

    def add_auxiliary_content(self, document):
        return synamic_add_auxiliary_content(self, document, self.__content_map)

    @property
    def dynamic_contents(self):
        return tuple(self.__content_map[Key.DYNAMIC_CONTENTS])

    def add_static_content(self, file_path):
        return synamic_add_static_content(self, file_path)

    def get_document_by_id(self, mod_name, doc_id):
        return synamic_get_document_by_id(self, mod_name, doc_id)

    # URL Things
    def get_url(self, parameter):
        return synamic_get_url(self, parameter, self.__content_map)

    def get_content_by_content_url(self, curl: ContentUrl):
        return synamic_get_content_by_url(self, curl, self.__content_map)

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
    @loaded
    def build(self):
        return _synamic_build(self, self.__content_map, self.__event_trigger)

    def initialize_site(self, force=False):
        return _synamic_initialize_site(self, force, self.__registered_dir_paths, self.__registered_virtual_files)

    @loaded
    def filter_content(self, filter_txt):
        return query_by_synamic_4_dynamic_contents(self, filter_txt)

    def __init__(self, site_root):
        normcase_normpath_root = os.path.normpath(os.path.normcase(site_root))
        assert os.path.exists(site_root), "Base path must not be non existent"
        assert normcase_normpath_root not in self.__site_root_paths
        self.__site_root_paths.add(normcase_normpath_root)
        self.__site_root = site_root

        self.__is_loaded = False

        # Event system
        self.__event_system = EventSystem(self)
        # acquire trigger function of event system
        self.__event_trigger = self.event_system._get_trigger()
        self.__init_instance_variables()

    def __init_instance_variables(self):
        # registered directories, path
        self.__registered_dir_paths = set()
        self.__registered_virtual_files = set()
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
        self.__dependency_list = None
        # site settings
        self.__site_settings = SiteSettings(self)

        # content service
        self.__content_service = MarkedContentService(self)

        # static service
        self.__static_service = StaticModuleService(self)

        # null service for adding some virtual files
        NullService(self)

    @not_loaded
    def load(self):
        assert os.path.exists(os.path.join(self.site_root, '.synamic')) and os.path.isfile(os.path.join(self.site_root,
                                                                                                        '.synamic')), "A file named `.synamic` must exist in the site root to explicitly declare that that is a legal synamic directory - this is to protect accidental modification other dirs: %s" % os.path.join(
            self.site_root, '.synamic')
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

    @loaded
    def _reload(self):
        # DONE: don's forget to convert event system to be instance based.
        # TODO: Reload not working
        self.__is_loaded = False
        self.__init_instance_variables()
        self.load()