"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


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
