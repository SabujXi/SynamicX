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
    def is_binary(cls, other, not_generated=False):
        if not_generated:
            return other in (cls.BINARY_DOCUMENT, )
        else:
            return other in (cls.BINARY_DOCUMENT, cls.GENERATED_BINARY_DOCUMENT)

    @classmethod
    def is_text(cls, other, not_generated=False):
        if not_generated:
            return other in (cls.TEXT_DOCUMENT, cls.HTML_DOCUMENT, )
        else:
            return other in (cls.TEXT_DOCUMENT, cls.GENERATED_TEXT_DOCUMENT, cls.HTML_DOCUMENT, cls.GENERATED_HTML_DOCUMENT)

    @classmethod
    def is_html(cls, other, not_generated=False):
        if not_generated:
            return other in (cls.HTML_DOCUMENT, )
        else:
            return other in (cls.HTML_DOCUMENT, cls.GENERATED_HTML_DOCUMENT)

    @classmethod
    def is_file(cls, other, not_generated=False):
        return cls.is_text(other, not_generated=not_generated) or cls.is_binary(other, not_generated=not_generated)

    @classmethod
    def is_generated(cls, other):
        return other in (cls.GENERATED_HTML_DOCUMENT, cls.GENERATED_TEXT_DOCUMENT, cls.GENERATED_BINARY_DOCUMENT)


class ContentContract(metaclass=abc.ABCMeta):

    __document_types = DocumentType

    @property
    def document_types(self) -> DocumentType:
        return self.__document_types

    @property
    @abc.abstractmethod
    def site(self):
        pass

    @property
    @abc.abstractmethod
    def cpath(self):
        """
        This is a path object associated with the file (for static the path, for dynamic the path to things like .md
         and for auxiliary - i need to think about that :p )
        """
        pass

    @property
    @abc.abstractmethod
    def curl(self):
        """
        Generated contents will have to implement this method themselves,
        Markdown and static content can call object manager method from inside to get it.
        <A content should know what it's url is - that's why I re-added this method to the interface.>
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
         
         this can be determined by the extension of to_file_system_path() on the curl object.
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

    def __str__(self):
        return "Content with url -> %s" % self.curl.path_as_str_w_site

    def __repr__(self):
        return repr(self.__str__())

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.curl == other.curl

    def __hash__(self):
        return hash(self.curl)
