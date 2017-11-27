import abc


class MetaContentModuleContract(abc.ABC):
    @property
    def generic_name(self):
        return "meta"

    @property
    @abc.abstractmethod
    def name(self): pass

    @property
    @abc.abstractmethod
    def directory_name(self):
        """
        This method must return the name of what the directory name will be inside the contents_modules directory.
        If no directory should be created for this, then it should return None.
        It may return the value of canonical name to make shortcut.
        :return: 
        """
        pass
    #
    # @property
    # @abc.abstractmethod
    # def dotted_path(self): pass

    @property
    @abc.abstractmethod
    def dependencies(self): pass

    @abc.abstractmethod
    def load(self):
        pass

    @property
    @abc.abstractmethod
    def is_loaded(self):
        pass
