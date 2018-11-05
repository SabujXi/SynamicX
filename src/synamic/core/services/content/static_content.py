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
from synamic.core.contracts.content import ContentContract, DocumentType


class StaticContent(ContentContract):
    def __init__(self, site, file_cpath, url_object, file_content=None, document_type=DocumentType.BINARY_DOCUMENT, mime_type='octet/stream'):
        self.__site = site
        self.__file_cpath = file_cpath
        self.__url_object = url_object
        self.__file_content = file_content
        self.__document_type = document_type
        self.__mime_type = mime_type

        # validation
        assert DocumentType.is_binary(self.__document_type)
        assert type(self.__file_content) in (type(None), bytes, bytearray)
        if self.__file_cpath is None:
            assert file_content is not None

    @property
    def site(self):
        return self.__site

    @property
    def path_object(self):
        return self.__file_cpath

    @property
    def url_object(self):
        return self.__url_object

    def get_stream(self):
        if self.__file_content is not None:
            file = io.BytesIO(self.__file_content)
        else:
            file = self.path_object.open('rb')
        return file

    @property
    def mime_type(self):
        # mime_type = 'octet/stream'
        # path = self.__url.to_file_system_path
        # type, enc = mimetypes.guess_type(path)
        # if type:
        #     mime_type = type
        # return mime_type
        return self.__mime_type

    @property
    def document_type(self):
        return self.__document_type
