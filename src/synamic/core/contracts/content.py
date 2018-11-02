"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
import abc
import enum


@enum.unique
class DocumentType(enum.Enum):
    # later, intending the use of auto() - currently this project in 3.5 and auto() is available in 3.6
    BINARY_DOCUMENT = "BINARY_DOCUMENT"
    GENERATED_BINARY_DOCUMENT = "GENERATED_BINARY_DOCUMENT"
    TEXT_DOCUMENT = "TEXT_DOCUMENT"
    GENERATED_TEXT_DOCUMENT = "GENERATED_TEXT_DOCUMENT"
    HTML_DOCUMENT = "HTML_DOCUMENT"
    GENERATED_HTML_DOCUMENT = "GENERATED_HTML_DOCUMENT"
    NOURL_DOCUMENT = "NOURL_DOCUMENT"
    META_DOCUMENT = "META_DOCUMENT"
    DIRECTORY = "DIRECTORY"
    NONE = "NONE"

    @classmethod
    def is_binary(cls, other):
        return other in (cls.BINARY_DOCUMENT, cls.GENERATED_BINARY_DOCUMENT)

    @classmethod
    def is_text(cls, other):
        return other in (cls.TEXT_DOCUMENT, cls.GENERATED_TEXT_DOCUMENT, cls.HTML_DOCUMENT, cls.GENERATED_HTML_DOCUMENT)

    @classmethod
    def is_html(cls, other):
        return other in (cls.HTML_DOCUMENT, cls.GENERATED_HTML_DOCUMENT)

    @classmethod
    def is_file(cls, other):
        return cls.is_text(other) or cls.is_binary(other)


class ContentContract(metaclass=abc.ABCMeta):

    __document_types = DocumentType

    @property
    def document_types(self) -> DocumentType:
        return self.__document_types

    @property
    @abc.abstractmethod
    def id(self):
        """
            Content id will not be of type int, it will be kept as string because there may be string id many time in our program.
            Warning: Unlike other things in Synamic, content ids are case sensitive.
        """
        pass

    @property
    @abc.abstractmethod
    def path_object(self):
        """
        This is a path object associated with the file (for static the path, for dynamic the path to things like .md
         and for auxiliary - i need to think about that :p )
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
         
         this can be determined by the extension of to_file_system_path() on the url_object object.
        """

    @property
    @abc.abstractmethod
    def document_type(self):
        """
        Instance of document __document_types enum
        """
        pass

    @property
    def is_text_document(self):
        return self.document_type is self.__document_types.TEXT_DOCUMENT

    @property
    def is_binary_document(self):
        return self.document_type is self.__document_types.BINARY_DOCUMENT

    @property
    def is_generated_binary_document(self):
        return self.document_type is self.__document_types.GENERATED_BINARY_DOCUMENT

    @property
    def is_generated_text_document(self):
        return self.document_type is self.__document_types.GENERATED_TEXT_DOCUMENT

    @property
    def is_nourl_document(self):
        return self.document_type is self.__document_types.NOURL_DOCUMENT

    @property
    def is_meta_document(self):
        return self.document_type is self.__document_types.META_DOCUMENT
