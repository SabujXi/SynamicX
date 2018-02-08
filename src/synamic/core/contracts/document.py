from abc import abstractmethod
from synamic.core.contracts.content import ContentContract


class BaseDocumentContract(ContentContract):
    @property
    @abstractmethod
    def url_object(self):
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
