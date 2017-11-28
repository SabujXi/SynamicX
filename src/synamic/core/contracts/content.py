import abc


class ContentContract(abc.ABC):
    @property
    @abc.abstractmethod
    def module(self):
        pass

    @property
    @abc.abstractmethod
    def path(self):
        pass

    @property
    @abc.abstractmethod
    def content_id(self):
        """
            Content id will not be of type int, it will be kept as string because there may be string id many time in our program. 
        """
        pass

    @abc.abstractmethod
    def get_stream(self):
        """
            This will be a file like object. 
        """

    @property
    @abc.abstractmethod
    def content_type(self):
        """
         return mime/type
         
         this can be determined by the extension of real_path() on the url object.
        """
