class BaseBackend:
    def __init__(self, path_tree):
        self.__path_tree = path_tree

    @property
    def path_tree(self):
        return self.__path_tree

    def open(self, cpath, *args, **kwargs):
        """Return a file object"""
        raise NotImplemented

    def exists(self, cpath):
        raise NotImplemented

    def is_file(self, cpath):
        pass

    def is_dir(self, cpath):
        pass

    def listdir(self, cpath):
        raise NotImplemented

    def makedirs(self, cpath):
        raise NotImplemented

    def getmtime(self, cpath):
        raise NotImplemented

    def remove(self, cpath):
        raise NotImplemented


class FileSystemBackend(BaseBackend):
    pass


class InMemoryBackend(BaseBackend):
    pass


class FileSystemRedirectBackend(BaseBackend):
    pass
