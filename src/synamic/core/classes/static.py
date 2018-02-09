"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import mimetypes
from synamic.core.contracts.content import ContentContract


class StaticContent(ContentContract):

    def __init__(self, config, path, url, content_id):
        self.__url = url
        self.__config = config
        self.__path = path
        self.__content_id = content_id

    @property
    def config(self):
        return self.__config

    @property
    def path(self):
        return self.__path

    @property
    def path_object(self):
        return self.path

    @property
    def content_id(self):
        return self.__content_id

    def get_stream(self):
        file = self.path.open('rb')
        return file

    @property
    def mime_type(self):
        mime_type = 'octet/stream'
        path = self.__url.real_path
        type, enc = mimetypes.guess_type(path)
        if type:
            mime_type = type
        return mime_type

    @property
    def content_type(self):
        return ContentContract.types.STATIC

    @property
    def url_object(self):
        return self.__url
