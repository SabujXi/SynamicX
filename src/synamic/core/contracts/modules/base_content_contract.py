import abc


class ContentModuleContract(abc.ABC):
    @property
    def generic_name(self):
        return "content"

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

    # @property
    # @abc.abstractmethod
    # def directory_path(self):
    #     """Relative directory path"""
    #     pass

    # @property
    # @abc.abstractmethod
    # def parent_dir(self):
    #     """Relative directory path"""
    #     pass
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

    @property
    @abc.abstractmethod
    def extensions(self): pass

    @property
    @abc.abstractmethod
    def root_url_path(self):
        """
            ContentUrl of the contents will be constructed based on this. Later on I can add per module root path in settings.yaml
            
            root_url_path will directly be appended to the url of the content.
            
            e.g. 1:
                content url: me/mo  # initial '/' is always stripped off
                path_root: meau
                
                final url: meaume/mo
                
            e.g 2:
                content url: me/mo  # initial '/' is always stripped off
                path_root: meau
                
                final url: meau/me/mo
        """
