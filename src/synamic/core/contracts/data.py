import abc


class DataContract(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_data_name(self):
        pass

    @property
    @abc.abstractmethod
    def origin(self):
        """Returns original data object"""

    @abc.abstractmethod
    def get(self, key, default=None):
        """Given a key returns the data"""

    @abc.abstractmethod
    def __getitem__(self, item):
        """Uses get()"""

    @abc.abstractmethod
    def __getattr__(self, key):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass
