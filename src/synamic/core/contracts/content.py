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
class CDocType(enum.Enum):
    # later, intending the use of auto() - currently this project in 3.5 and auto() is available in 3.6
    BINARY_DOCUMENT = "BINARY_DOCUMENT"
    GENERATED_BINARY_DOCUMENT = "GENERATED_BINARY_DOCUMENT"
    TEXT_DOCUMENT = "TEXT_DOCUMENT"
    GENERATED_TEXT_DOCUMENT = "GENERATED_TEXT_DOCUMENT"
    HTML_DOCUMENT = "HTML_DOCUMENT"
    GENERATED_HTML_DOCUMENT = "GENERATED_HTML_DOCUMENT"

    META_DOCUMENT = "META_DOCUMENT"
    NOURL_DOCUMENT = "NOURL_DOCUMENT"
    DIRECTORY = "DIRECTORY"
    UNSPECIFIED = "UNSPECIFIED"

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

    __cdoc_types = CDocType

    @property
    @abc.abstractmethod
    def site(self):
        pass

    @property
    @abc.abstractmethod
    def cfields(self):
        pass

    @abc.abstractmethod
    def get_stream(self):
        """
        This will be a file like object. 
        """

    @property
    @abc.abstractmethod
    def body(self):
        pass

    @property
    @abc.abstractmethod
    def body_as_bytes(self):
        pass

    @property
    @abc.abstractmethod
    def body_as_string(self):
        pass

    def __str__(self):
        return "Content with url -> %s" % self.cfields.curl.path_as_str_w_site

    def __repr__(self):
        return repr(self.__str__())

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.cfields.curl == other.cfields.curl

    def __hash__(self):
        return hash(self.cfields.curl)
