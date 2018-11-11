from abc import abstractmethod, ABC
from .host import HostContract


class SynamicContract(ABC, HostContract):
    @abstractmethod
    def load(self):
        pass

    @property
    @abstractmethod
    def is_loaded(self):
        pass

    @property
    @abstractmethod
    def env(self):
        pass

    @property
    @abstractmethod
    def event_system(self):
        pass

    @property
    @abstractmethod
    def default_data(self):
        pass

    @property
    @abstractmethod
    def object_manager(self):
        pass

    @property
    @abstractmethod
    def sites(self):
        pass

    @property
    @abstractmethod
    def router(self):
        pass
