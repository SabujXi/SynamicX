import abc


class CFieldsContract(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, key, default=None):
        pass

    @abc.abstractmethod
    def set(self, key, value):
        pass

    @abc.abstractmethod
    def keys(self):
        pass

    @property
    @abc.abstractmethod
    def raw(self):
        pass

    @property
    @abc.abstractmethod
    def cdoctype(self):
        """
        Instance of document __cdoc_types enum
        """
        pass

    @property
    @abc.abstractmethod
    def cpath(self):
        pass

    @property
    @abc.abstractmethod
    def curl(self):
        pass

    @property
    @abc.abstractmethod
    def cmodel(self):
        pass

    @property
    @abc.abstractmethod
    def mimetype(self):
        pass
