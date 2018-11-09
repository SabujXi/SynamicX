"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
import io
from synamic.core.contracts.content import ContentContract, CDocType


class GeneratedContent(ContentContract):
    def __init__(self, site, synthetic_cfields, curl, file_content,
                 cdoctype=CDocType.GENERATED_TEXT_DOCUMENT,
                 mime_type='octet/stream', source_cpath=None):

        self.__site = site
        self.__synthetic_cfields = synthetic_cfields
        self.__curl = curl
        self.__file_content = file_content
        self.__cdoctype = cdoctype
        self.__mime_type = mime_type
        self.__source_cpath = source_cpath

        # validation
        assert CDocType.is_generated(self.__cdoctype)
        assert type(self.__file_content) in (type(None), bytes, bytearray, str)

    @property
    def site(self):
        return self.__site

    @property
    def cpath(self):
        raise Exception("Generated content cannot have cpath object")

    @property
    def curl(self):
        return self.__curl

    def get_stream(self):
        if self.__file_content is None:
            assert self.__source_cpath is not None

        if self.__file_content is not None:
            if isinstance(self.__file_content, (bytes, bytearray)):
                file = io.BytesIO(self.__file_content)
            else:
                assert isinstance(self.__file_content, str)
                file = io.BytesIO(self.__file_content.encode('utf-8'))
        else:
            file = self.__source_cpath.open('rb')
        return file

    @property
    def body(self):
        body = self.__synthetic_cfields.get('__body__', '')
        return body

    @property
    def mime_type(self):
        return self.__mime_type

    @property
    def cdoctype(self):
        return self.__cdoctype

    def __get(self, key):
        return self.__synthetic_cfields.get(key, None)

    def __getitem__(self, key):
        return self.__get(key)

    def __getattr__(self, key):
        return self.__get(key)

    def __str__(self):
        return "Generated content: <%s>\n" % str(self.curl) + '...'

    def __repr__(self):
        return str(self)

    @property
    def source_cpath(self):
        return self.__source_cpath

    @property
    def file_content(self):
        if self.__file_content is not None:
            return self.__file_content
        else:
            with self.get_stream() as stream:
                content = stream.read()
                return content

    def __set_file_content__(self, fc):
        assert self.__file_content is None
        self.__file_content = fc


