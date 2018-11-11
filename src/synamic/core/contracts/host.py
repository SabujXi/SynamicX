from abc import abstractmethod, ABCMeta


class HostContract(metaclass=ABCMeta):
    """Synamic and Site are hosts currently"""
    @property
    @abstractmethod
    def abs_root_path(self):
        pass

    @property
    @abstractmethod
    def path_tree(self):
        pass

    @property
    @abstractmethod
    def default_data(self):
        pass
