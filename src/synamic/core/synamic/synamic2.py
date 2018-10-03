"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
from synamic.core.services.event_system.events import EventSystem
from synamic.core.services.filesystem.path_tree import PathTree
from synamic.core.services.content.content_service import ContentService
from synamic.core.services.menu.menu_service import MenuService
from synamic.core.services.template.template_service import SynamicTemplateService
from synamic.core.services.image_resizer.image_resizer_service import ImageResizerService
from synamic.core.services.site_settings.site_settings import SiteSettingsService
from synamic.core.standalones.functions.decorators import loaded, not_loaded
from synamic.core.services.types.type_system import TypeSystem
from synamic.core.services.sass.sass_service import SASSService
from synamic.core.services.tasks import TasksService
from synamic.core.configs import DefaultConfigManager
from synamic.core.object_manager import ObjectManager
from synamic.core.services.router import RouterService
from synamic.core.services.marker import MarkerService


def _install_default_services(synamic):
    self = synamic
    # Event Bus
    self.add_service('event_bus', EventSystem)

    # setting path tree
    self.add_service('path_tree', PathTree)
    # markers
    self.add_service('markers', MarkerService)
    # menus
    self.add_service('menus', MenuService)
    # templates service
    self.add_service('templates', SynamicTemplateService)
    # type system
    self.add_service('types', TypeSystem)

    # site settings
    self.add_service('site_settings', SiteSettingsService)

    # content service
    self.add_service('contents', ContentService)

    self.add_service('image_resizer', ImageResizerService)
    self.add_service('sass', SASSService)

    self.add_service('tasks', TasksService)

    # Router Service
    self.add_service('router', RouterService)

    # # null service for adding some virtual files
    # NullService(self)


class Synamic:
    def __init__(self, site_root, parent=None, prefix_dir=""):
        self.__is_loaded = False
        self.__site_root = site_root
        self.__parent = parent
        self.__prefix_dir = prefix_dir

        # 1. >>> Check if the parent is the same type object.
        if parent is not None:
            assert type(self.__parent) is type(self)
        # Root of all the synamic object must be None (Adam had no parent). Check it
        _root_parent = self.__parent
        while _root_parent:
            if _root_parent.parent is not None:
                _root_parent = _root_parent.parent
            else:
                _root_parent = None
        assert _root_parent is None
        # 1. <<<

        # Default Config Manager
        self.__default_configs = DefaultConfigManager(self)

        # Object Manager
        # self.add_service('object_manager', ObjectManager)
        self.__object_manager = ObjectManager(self)

        # Service container
        self.__services_container = {}
        _install_default_services(self)

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
        self.__is_loaded = True
        return self

    @property
    def default_configs(self) -> DefaultConfigManager:
        return self.__default_configs

    @property
    def event_bus(self) -> EventSystem:
        return self.__services_container['event_bus']

    @property
    def object_manager(self) -> ObjectManager:
        return self.__object_manager

    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded

    @property
    def site_root(self):
        return self.__site_root

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
        # TODO: fix it
        if not settings_prefix_dir:
            res = self.__prefix_dir
        else:
            res = settings_prefix_dir + '/' + self.__prefix_dir
        return res

    @loaded
    @property
    def sites(self):
        # TODO: fix it
        # TODO: Sites can only be instantiated, accessed from root synamic - otherwise raise exception. is_root
        self.__sites

    @loaded
    @property
    def router(self):
        # TODO: Router can only be instantiated, accessed from root synamic - otherwise raise exception. is_root
        pass

    @loaded
    @property
    def builder(self):
        pass
