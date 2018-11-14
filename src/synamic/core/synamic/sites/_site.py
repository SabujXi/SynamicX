import os
from synamic.core.services.event_system.events import EventSystem
from synamic.core.services.filesystem.path_tree import PathTree
from synamic.core.services.content.content_service import ContentService
from synamic.core.services.menu.menu_service import MenuService
from synamic.core.services.template.template_service import SynamicTemplateService
from synamic.core.services.image_resizer.image_resizer_service import ImageResizerService
from synamic.core.services.site_settings.site_settings import SiteSettingsService
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.services.types.type_system import TypeSystem
from synamic.core.services.pre_processor import PreProcessorService
from synamic.core.services.tasks import TasksService
from synamic.core.services.marker import MarkerService
from synamic.core.services.user import UserService
from synamic.core.services.data import DataService
from synamic.core.default_data import DefaultDataManager
from synamic.core.contracts import SiteContract
from synamic.core.services.sitemap import SitemapService


def _install_default_services(site):
    self = site
    # Event Bus
    self.add_service('event_bus', EventSystem)

    # markers
    self.add_service('markers', MarkerService)
    # menus
    self.add_service('menus', MenuService)

    # user
    self.add_service('users', UserService)

    # templates service
    self.add_service('templates', SynamicTemplateService)
    # type system
    self.add_service('types', TypeSystem)

    # site settings
    self.add_service('site_settings', SiteSettingsService)

    # content service
    self.add_service('contents', ContentService)

    self.add_service('image_resizer', ImageResizerService)
    self.add_service('pre_processor', PreProcessorService)

    # data
    self.add_service('data', DataService)

    self.add_service('tasks', TasksService)

    # sitemap
    self.add_service('sitemap', SitemapService)


class _Site(SiteContract):
    def __init__(self, synamic, site_id, abs_path_to_site, parent_site=None, root_site=None):
        assert os.path.exists(abs_path_to_site)
        self.__synamic = synamic
        self.__site_id = site_id
        self.__abs_path_to_site = abs_path_to_site
        self.__parent_site = parent_site
        self.__root_site = root_site
        assert type(parent_site) in (self.__class__, type(None))
        assert type(root_site) in (self.__class__, type(None))

        # 1. >>> Check if the parent is the same type object.
        if self.__parent_site is not None:
            assert type(self.__parent_site) is type(self)
        # Root of all the synamic object must be None (Adam had no parent). Check it
        _root_parent = self.__parent_site
        while _root_parent:
            if _root_parent.parent is not None:
                _root_parent = _root_parent.parent
            else:
                _root_parent = None
        assert _root_parent is None
        # 1. <<<

        # Object Manager for site
        self.__object_manager_4_site = self.__synamic.object_manager.get_manager_for_site(self)

        # setting path tree
        self.__path_tree = PathTree.for_site(self)

        # Service container
        self.__services_container = {}
        _install_default_services(self)

        # Add path tree as service.
        # TODO: remove it later - keeping it now just to not crash the system.
        self.__services_container['path_tree'] = self.__path_tree

        self.__menus_wrapper = MenusWrapper(self.__object_manager_4_site)
        self.__users_wrapper = UsersWrapper(self.__object_manager_4_site)

        self.__is_loaded = False

    @property
    def synamic(self):
        return self.__synamic

    @property
    def id(self):
        return self.__site_id

    @property
    def abs_root_path(self):
        return self.__abs_path_to_site

    @property
    def parent(self):
        return self.__parent_site

    @property
    def has_parent(self):
        return False if self.__parent_site is None else True

    @property
    def root(self):
        return self.__root_site

    @property
    def is_root(self):
        return self.__root_site is None

    def get_service(self, service_name, default=None, error_out=True):
        service = self.__services_container.get(service_name, None)
        if error_out:
            if service is None:
                raise Exception("Service with name %s could not be found." % service_name)
        if service is None:
            return default
        return service

    def add_service(self, service_name, service_class, init_args=(), init_kwargs=None):
        if init_kwargs is None:
            init_kwargs = {}
        assert service_name not in self.__services_container, 'Service with name `%s` already exists.' % service_name
        for existing_service_class in [type(service) for service in self.__services_container.values()]:
            if existing_service_class == service_class:
                raise Exception('Service instance already added. You are trying to add service with name'
                                '`%s` and type `%s`. Instance with name `%s` and the same type found.'
                                % (service_name, str(service_class), str(existing_service_class)))
        # Now do the real adding work.
        new_service = service_class(self, *init_args, **init_kwargs)
        self.__services_container[service_name] = new_service
        return new_service

    @not_loaded
    def load(self):
        for service in self.__services_container.values():
            service.load()
        self.__object_manager_4_site.load()
        self.__is_loaded = True
        return self

    @property
    def default_data(self) -> DefaultDataManager:
        return self.__synamic.default_data

    @property
    def system_settings(self):
        return self.__synamic.default_data.get_system_settings()

    @property
    def settings(self):
        return self.object_manager.get_site_settings()

    @property
    def menu(self):
        return self.__menus_wrapper

    @property
    def user(self):
        return self.__users_wrapper

    @property
    def path_tree(self):
        return self.__path_tree

    @property
    def event_bus(self) -> EventSystem:
        return self.__services_container['event_bus']

    @property
    def object_manager(self):
        return self.__object_manager_4_site

    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded

    @property
    def site_wrapper(self):
        return _SiteWrapper(self)

    def __getattr__(self, service_name):
        return self.get_service(service_name, error_out=True)

    def __getitem__(self, service_name):
        return self.get_service(service_name, error_out=True)

    def __str__(self):
        return 'Site: ' + str(self.id) + ' <- ' + (str(self.parent.id.components) if self.has_parent else str(None)) \
               + ' [parent]'

    def __repr__(self):
        return repr(self.__str__())

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.id == other.id


class _SiteWrapper:
    """Wrapper for passing to templates and other places."""
    def __init__(self, site):
        self.__site = site
        self.__blacklisted_attrs = {'load', 'add_service', 'get_service', 'synamic', 'parent', 'root',
                                    'default_data', 'object_manager', 'parent', 'sites', 'router', 'builder',
                                    'site_wrapper'}

    def __getattr__(self, key):
        if key in self.__blacklisted_attrs:
            raise AttributeError('%s key is black listed' % key)
        else:
            try:
                return getattr(self.__site, key)
            except AttributeError:
                raise AttributeError('%s key was not found on site' % key)


class _SiteStuffWrapper:
    def __init__(self, origin_object):
        self.__origin_object__ = origin_object

    def get(self, key, default=None):
        return self.__origin_object__.get(key, default=default)

    def __getattr__(self, key):
        return self.get(key)

    def __getitem__(self, key):
        return self.get(key)


class MenusWrapper:
    def __init__(self, object_manager):
        self.__object_manager = object_manager

    def all(self):
        return self.__object_manager.get_menus()

    def get(self, key, default=None):
        return self.__object_manager.get_menu(key, default=default)

    def __getattr__(self, key):
        return self.get(key)

    def __getitem__(self, key):
        return self.get(key)


class UsersWrapper:
    def __init__(self, object_manager):
        self.__object_manager = object_manager

    def all(self):
        return self.__object_manager.get_users()

    def get(self, key, default=None):
        return self.__object_manager.get_user(key, default=default)

    def __getattr__(self, key):
        return self.get(key)

    def __getitem__(self, key):
        return self.get(key)
