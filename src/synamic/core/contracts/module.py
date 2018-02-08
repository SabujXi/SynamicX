import abc
import re


class BaseModuleContract(metaclass=abc.ABCMeta):
    __module_name_pattern = re.compile(r'^[a-zA-Z0-9_-]+$', re.I)

    @classmethod
    def is_module_name_valid(cls, name):
        return bool(cls.__module_name_pattern.match(name) and name.islower())

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    @abc.abstractmethod
    def config(self):
        pass

    @property
    @abc.abstractmethod
    def dependencies(self):
        pass

    @abc.abstractmethod
    def load(self):
        pass

    @property
    @abc.abstractmethod
    def is_loaded(self):
        pass


class BaseMetaModuleContract(BaseModuleContract):
    pass


class BaseContentModuleContract(BaseModuleContract):

    @property
    @abc.abstractmethod
    def content_class(self):
        pass

    @property
    @abc.abstractmethod
    def root_url_path(self):
        """
            ContentUrl of the contents will be constructed based on this. Later on I can add per module_object root path in settings.yaml
            
            root_url_path will directly be appended to the url_object of the content.
            
            e.g. 1:
                content url_object: me/mo  # initial '/' is always stripped off
                path_root: meau
                
                final url_object: meaume/mo
                
            e.g 2:
                content url_object: me/mo  # initial '/' is always stripped off
                path_root: meau
                
                final url_object: meau/me/mo
        """

    @property
    @abc.abstractmethod
    def dynamic_contents(self):
        pass

    @property
    @abc.abstractmethod
    def static_contents(self):
        pass

    @abc.abstractmethod
    def get_content_by_id(self, content_id):
        pass
