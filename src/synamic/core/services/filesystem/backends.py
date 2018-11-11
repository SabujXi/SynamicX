import os
import os.path
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
    def remove(self, path):
        """Removes the path"""


class FileSystemBackend(BaseFsBackendContract):
    def open(self, path, *args, **kwargs):
        return open(path, *args, **kwargs)

    def exists(self, path):
        return os.path.exists(path)

    def is_file(self, path):
        return os.path.isfile(path)

    def is_dir(self, path):
        return os.path.isdir(path)

    def listdir(self, path):
        return os.listdir(path)

    def makedirs(self, path):
        return os.makedirs(path)

    def getmtime(self, path):
        return os.path.getmtime(path)

    def remove(self, path):
        return os.remove(path)


class InMemoryBackend(BaseFsBackendContract):
    pass


class FileSystemRedirectBackend(BaseFsBackendContract):
    pass
