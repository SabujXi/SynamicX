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
    def is_frontmatter_valid(self):
        pass

    @property
    @abstractmethod
    def has_frontmatter(self):
        pass

    @property
    @abstractmethod
    def has_valid_frontmatter(self):
        pass

    @property
    @abstractmethod
    def raw_frontmatter(self):
        pass

    @property
    @abstractmethod
    def frontmatter(self):
        pass

    @property
    @abstractmethod
    def body(self):
        pass

    @property
    @abstractmethod
    def title(self):
        pass

    @property
    @abstractmethod
    def created_on(self):
        pass

    @property
    @abstractmethod
    def updated_on(self):
        pass

    @property
    @abstractmethod
    def summary(self):
        pass

    @property
    @abstractmethod
    def tags(self):
        pass

    @property
    @abstractmethod
    def categories(self):
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

    @abstractmethod
    def trigger_pagination(self):
        pass

