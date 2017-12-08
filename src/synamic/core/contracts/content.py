import abc
import enum


class ContentContract(metaclass=abc.ABCMeta):
    @enum.unique
    class types(enum.Enum):
        # later, intending the use of auto() - currently this project in 3.5 and auto() is available in 3.6
        STATIC = 1
        DYNAMIC = 2
        AUXILIARY = 3

    @property
    @abc.abstractmethod
    def module_object(self):
        pass

    @property
    @abc.abstractmethod
    def path_object(self):
        """
        This is a path object associated with the file (for static the path, for dynamic the path to things like .md
         and for auxiliary - i need to think about that :p )
        """
        pass

    @property
    @abc.abstractmethod
    def content_name(self):
        """ 
        """

    @property
    @abc.abstractmethod
    def content_id(self):
        """
            Content id will not be of type int, it will be kept as string because there may be string id many time in our program.
             
             Warning: Unlike other things in Synamic, content ids are case sensitive.
        """
        pass

    @abc.abstractmethod
    def get_stream(self):
        """
            This will be a file like object. 
        """

    @property
    @abc.abstractmethod
    def mime_type(self):
        """
         return mime/type
         
         this can be determined by the extension of real_path() on the url_object object.
        """

    @property
    @abc.abstractmethod
    def content_type(self):
        """
        Instance of types enum
        """
        pass
    @property
    def is_dynamic(self):
        return self.content_type is self.types.DYNAMIC

    @property
    def is_static(self):
        return self.content_type is self.types.STATIC

    @property
    def is_auxiliary(self):
        return self.content_type is self.types.AUXILIARY

    # @property
    # @abc.abstractmethod
    # def is_static(self):
    #     """
    #     Static files that need not extra processing and can be handled by static module.
    #
    #     With the help of this, static files can be send by dev server or sendfile instead of streaming.
    #     """
    #
    # @property
    # @abc.abstractmethod
    # def is_dynamic(self):
    #     """
    #     For example, created with the help of .md files in text module
    #     """
    #
    # @property
    # @abc.abstractmethod
    # def is_auxiliary(self):
    #     """
    #     For example, created invoking paginate.
    #     """
    #


