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


class StaticContent(ContentContract):
    def __init__(self, site, file_cpath, curl, file_content=None, cdoctype=CDocType.BINARY_DOCUMENT, mimetype='octet/stream'):
        self.__site = site
        self.__file_cpath = file_cpath
        self.__curl = curl
        self.__file_content = file_content
        self.__cdoctype = cdoctype
        self.__mimetype = mimetype

        # validation
        assert CDocType.is_binary(self.__cdoctype)
        assert type(self.__file_content) in (type(None), bytes, bytearray)
        if self.__file_cpath is None:
            assert file_content is not None

    @property
    def site(self):
        return self.__site

    @property
    def cpath(self):
        return self.__file_cpath

    @property
    def curl(self):
        return self.__curl

    def get_stream(self):
        if self.__file_content is not None:
            file = io.BytesIO(self.__file_content)
        else:
            file = self.cpath.open('rb')
        return file

    @property
    def mimetype(self):
        # mimetype = 'octet/stream'
        # path = self.__url.to_file_system_path
        # type, enc = mimetypes.guess_type(path)
        # if type:
        #     mimetype = type
        # return mimetype
        return self.__mimetype

    @property
    def cdoctype(self):
        return self.__cdoctype

