import os
import os.path
from synamic.core.contracts import BaseFsBackendContract


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
