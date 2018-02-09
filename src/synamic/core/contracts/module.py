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
    pass