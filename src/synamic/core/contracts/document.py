from abc import abstractmethod
from synamic.core.contracts.content import ContentContract


class BaseDocumentContract(ContentContract):
    @property
    @abstractmethod
    def url_object(self):
        pass

    @url_object.setter
    @abstractmethod
    def url_object(self, url_object):
        pass


class StaticDocumentContract(BaseDocumentContract):
    @property
    @abstractmethod
    def absolute_path(self):
        pass


class MarkedDocumentContract(BaseDocumentContract):
    @property
    @abstractmethod
    def fields(self):
        pass

    @property
    @abstractmethod
    def body(self):
        pass

    @property
    @abstractmethod
    def template_name(self):
        """
        Returns template name  
        """

    @property
    @abstractmethod
    def template_module_object(self):
        """
        Returns template module_object
        """