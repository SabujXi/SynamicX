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
import shutil
from synamic.core.synamic.classes.sites import Sites

from synamic.core.contracts.synamic_contract import SynamicContract
from synamic.core.event_system.events import EventTypes, EventSystem, Event
from synamic.core.filesystem.content_path.content_path2 import ContentPath2
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
from synamic.core.services.image_resizer.image_resizer_service import ImageResizerService
from synamic.core.site_settings.site_settings import SiteSettings
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.synamic._synamic_enums import Key
from synamic.core.synamic.functions.add_auxiliary_content import synamic_add_auxiliary_content
from synamic.core.synamic.functions.add_document import synamic_add_document
from synamic.core.synamic.functions.add_static_content import synamic_add_static_content
from synamic.core.synamic.functions.build import _synamic_build
from synamic.core.synamic.functions.get_content_by_url import synamic_get_content_by_url
from synamic.core.synamic.functions.get_document_by_id import synamic_get_document_by_id
from synamic.core.synamic.functions.initialize_site import _synamic_initialize_site
from synamic.core.synamic.functions.register_path import synamic_register_path
from synamic.core.synamic.functions.register_virtual_file import synamic_register_virtual_file
from synamic.core.type_system.type_system import TypeSystem
from synamic.core.urls.url import ContentUrl
from synamic.core.services.sass.sass_service import SASSService
from synamic.core.synamic.functions.get_content import synamic_get_content
from synamic.core.exceptions.synamic_exceptions import GetUrlFailed, GetContentFailed
from synamic.core.standalones.functions.parent_config_splitter import parent_config_str_splitter
from synamic.core.standalones.functions.sequence_ops import Sequence


class Synamic(SynamicContract):
    __slots__ = ('__event_trigger', '__registered_dir_paths', '__registered_virtual_files',
                 '__site_root', '__services_list', '__content_map', '__path_tree', '__tags',
                 '__categories', '__menus', '__templates', '__type_system', '__model_service', '__taxonomy',
                 '__series', '__key_values', '__is_loaded', '__dependency_list', '__site_settings', '__content_service',
                 '__static_service', '__event_system')

    __site_root_paths = set()

    # > Object Stores
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

    @property
    @loaded
    def series(self):
        return self.__series

    @property
    def site_settings(self):
        return self.__site_settings

    @property
    @loaded
    def taxonomy(self):
        return self.__taxonomy

    # < Object Stores

    # > Non-Object Stores
    @property
    def path_tree(self):
        return self.__path_tree

    @property
    def sass_service(self):
        return self.__sass_sservice

    @property
    def templates(self):
        return self.__templates
    template_service = templates
    # > Non-Object Stores

    @property
    def event_system(self) -> EventSystem:
        return self.__event_system

    def register_path(self, dir_path: ContentPath2):
        return synamic_register_path(self, dir_path, self.__registered_dir_paths)

    def register_virtual_file(self, virtual_file: VirtualFile):
        return synamic_register_virtual_file(self, virtual_file, self.__registered_virtual_files)

    @property
    def is_loaded(self):
        return self.__is_loaded

    @property
    def type_system(self):
        return self.__type_system

    @property
    def model_service(self):
        return self.__model_service

    @property
    def content_service(self):
        return self.__content_service

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
    get_content_by_id = get_document_by_id

    def get_content(self, parameter):
        is_from_parent, parameter = parent_config_str_splitter(parameter)
        # print("is_from_parent: %s" % is_from_parent)
        # print(parameter)
        if is_from_parent:
            assert self.parent is not None, "Parent does not exist"
            res = self.parent.get_content(parameter)
        else:
            res = synamic_get_content(self, parameter, self.__content_map)
        return res

    # URL Things
    def get_url(self, parameter):
        try:
            cnt = self.get_content(parameter)
        except GetContentFailed:
            # Should raise exception or just return None/False
            raise GetUrlFailed("Url could not be found for: %s" % parameter)
        return cnt.url_object.path

    def get_content_by_content_url(self, curl: ContentUrl):
        prefix_components = self.prefix_dir.split('/')
        has_prefix = False if prefix_components[0] == '' else True
        url_comps = curl.path_components
        # print('\n\n')
        # print("First url components: %s" % str(url_comps))
        if not has_prefix:
            new_url_comps = curl.path_components
            new_url = curl
            cnt = synamic_get_content_by_url(self, new_url, self.__content_map)
        else:
            new_url_comps = Sequence.extract_4m_startswith(url_comps, prefix_components)
            # print("New First url components: %s" % str(new_url_comps))
            if new_url_comps is None:
                cnt = None
                new_url = curl
            else:
                new_url = ContentUrl(self, new_url_comps, append_slash=curl.append_slash)
                cnt = synamic_get_content_by_url(self, new_url, self.__content_map)

        if cnt is None:
            for dr, syn in self.__children_site_synamics.items():
                cnt = syn.get_content_by_content_url(new_url)
                # print("Last new url path: %s" % str(new_url.path))
                # print("Last new url path comps: %s" % str(new_url.path_components))
                if cnt is not None:
                    # print("Found: %s" % new_url.path)
                    break
                else:
                    # print("not Found: %s in %s" % (new_url.path, dr))
                    pass
        else:
            # print("Found: %s" % new_url.path)
            pass

        # print("New Content Url: %s" % new_url.path)
        return cnt

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

    @property
    def output_dir(self):
        return self.site_settings.output_dir

    def _prebuild_clean_output(self):
        def _remove_all(out_path):
            if os.path.exists(out_path):
                for a_path in os.listdir(out_path):
                    fp = os.path.join(out_path, a_path)
                    if os.path.isdir(fp):
                        shutil.rmtree(fp)
                    else:
                        os.remove(fp)
        if self.is_root:
            out_path = self.path_tree.get_full_path(self.site_settings.output_dir)
            _remove_all(out_path)
        for syn in self.__children_site_synamics.values():
            syn._prebuild_clean_output()

    # Build Things
    @loaded
    def build(self):
        # return
        self._prebuild_clean_output()
        for dr in self.__children_site_dirs:
            self.__children_site_synamics[dr].build()
        res = _synamic_build(self, self.__content_map, self.__event_trigger)
        # move all the child to parent
        if self.has_parent:
            output_dir_in_child = self.path_tree.get_full_path([self.output_dir])
            print("output_dir_in_child: %s" % output_dir_in_child)
            output_dir_in_parent = self.parent.path_tree.get_full_path([self.parent.output_dir, self.prefix_dir])
            print("output_dir_in_parent: %s" % output_dir_in_parent)
            for cpath in os.listdir(output_dir_in_child):
                new_child_path = os.path.join(output_dir_in_child, cpath)
                new_parent_path = os.path.join(output_dir_in_parent, cpath)
                dir_new_parent_path = new_parent_path
                if os.path.isdir(new_parent_path):
                    if not os.path.exists(new_parent_path):
                        os.makedirs(new_parent_path)
                        print("Dir created: %s" % new_parent_path)
                else:
                    # shutil.copy(new_child_path, new_parent_path)
                    if not os.path.exists(os.path.dirname(new_parent_path)):
                        dir_new_parent_path = os.path.dirname(new_parent_path)
                        os.makedirs(dir_new_parent_path)
                        print("Dir created: %s" % dir_new_parent_path)
                print(new_child_path + " -> " + new_parent_path)
                # if self.is_root:
                assert os.path.exists(new_child_path)
                shutil.move(new_child_path, new_parent_path)
                # input('Proceed?')
            # os.rmdir(output_dir_in_child)

        return

    def initialize_site(self, force=False):
        return _synamic_initialize_site(self, force, self.__registered_dir_paths, self.__registered_virtual_files)

    @loaded
    def filter_content(self, filter_txt):
        return query_by_synamic_4_dynamic_contents(self, filter_txt)

    @loaded
    def filter(self, filter_txt):
        return self.filter_content(filter_txt)

    @property
    def parent(self):
        return self.__parent

    @property
    def has_parent(self):
        return False if self.parent is None else True

    @property
    def is_root(self):
        return not self.has_parent

    @property
    def prefix_dir(self):
        settings_prefix_dir = self.site_settings.prefix_dir
        if not settings_prefix_dir:
            res = self.__prefix_dir
        else:
            res = settings_prefix_dir + '/' + self.__prefix_dir
        return res

    @loaded
    @property
    def sites(self):
        self.__sites

    def __init__(self, site_root, parent=None, prefix_dir=""):
        self.__parent = parent
        if parent is not None:
            assert type(self.__parent) is type(self)
        _parent = self.__parent
        while _parent:
            if _parent.parent is not None:
                _parent = _parent.parent
            else:
                _parent = None
        assert _parent is None
        self.__prefix_dir = prefix_dir
        self.__children_site_dirs = []
        self.__children_site_synamics = {}  # dir => synamic
        self.__sites = Sites(self, self.__children_site_synamics)

        normcase_normpath_root = os.path.normpath(os.path.normcase(site_root))
        assert os.path.exists(site_root), "Base path must not be non existent"
        print("normcase_normpath_root: %s" % normcase_normpath_root)
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

        self.__image_resizer = ImageResizerService(self)
        self.__sass_sservice = SASSService(self)

        # null service for adding some virtual files
        NullService(self)

    @loaded
    def resize_image(self, path, width, height):
        path = self.path_tree.create_path(path)
        return self.__image_resizer.resize(path, width, height)

    @not_loaded
    def load(self):
        if not self.has_parent:
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

        self.__image_resizer.load()

        self.__sass_sservice.load()

        # content load
        self.__content_service.load()

        self.__event_trigger(
            EventTypes.CONTENT_POST_LOAD,
            Event(self)
        )

        self.__is_loaded = True

        my_sub_sites_dir = os.path.join(self.site_root, 'sites')
        if not os.path.exists(my_sub_sites_dir):
            return
        chdn_paths = os.listdir(my_sub_sites_dir)
        print(chdn_paths)
        self.__children_site_dirs = [dr for dr in chdn_paths if os.path.isdir(os.path.join(self.site_root, 'sites', dr))]
        print(self.__children_site_dirs)
        for dr in self.__children_site_dirs:
            if dr == self.site_settings.output_dir:
                continue
            dr_full = os.path.join(self.site_root, 'sites', dr)
            print(dr_full)
            # input()
            self.__children_site_synamics[dr] = self.__class__(
                dr_full,
                parent=self,
                prefix_dir=dr
            )
            self.__children_site_synamics[dr].load()
            print("Loaded:: " + dr)

    @loaded
    def _die_cleanup(self):
        normcase_normpath_root = os.path.normpath(os.path.normcase(self.site_root))
        self.__site_root_paths.remove(normcase_normpath_root)
        for syn in self.__children_site_synamics.values():
            syn._die_cleanup()
