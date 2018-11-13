import abc


class BaseFsBackendContract(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def open(self, path, *args, **kwargs):
        """Return a file object"""

    @abc.abstractmethod
    def exists(self, path):
        """Checks existence of path"""

    @abc.abstractmethod
    def is_file(self, path):
        """Checks if it is a file"""

    @abc.abstractmethod
    def is_dir(self, path):
        """Checks if it is a dir"""

    @abc.abstractmethod
    def listdir(self, path):
        """Lists a directory"""

    @abc.abstractmethod
    def makedirs(self, path):
        """Makes directories recursively"""

    @abc.abstractmethod
    def getmtime(self, path):
        """Get modification? time"""

    @abc.abstractmethod
    def getctime(self, path):
        """Get last metadata change or creation time (on windows)"""

    @abc.abstractmethod
    def remove(self, path):
        """Removes the path"""
