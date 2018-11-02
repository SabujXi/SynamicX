"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import sass
import io
import mimetypes
from synamic.core.contracts.content import ContentContract
from synamic.core.synamic.router.url import _ContentUrl


class CSSContent(ContentContract):

    def __init__(self, site, scss_path, css_path):
        self.__url = None
        self.__site = site
        self.__scss_path = scss_path
        self.__path = css_path
        self.__url = self.__url = _ContentUrl(self.__site, css_path)

    @property
    def site(self):
        return self.__site

    @property
    def path(self):
        return self.__path

    @property
    def path_object(self):
        return self.path

    # @property
    # def id(self):
    #     return None

    def get_stream(self):
        scss_fn = self.__scss_path.abs_path
        css_str = sass.compile(filename=scss_fn)
        css_io = io.BytesIO(css_str.encode('utf-8'))
        del css_str
        return css_io

    @property
    def mime_type(self):
        mime_type = 'octet/stream'
        path = self.__url.real_path
        type, enc = mimetypes.guess_type(path)
        if type:
            mime_type = type
        return mime_type

    @property
    def document_type(self):
        return ContentContract.__document_types.AUXILIARY

    @property
    def url_object(self):
        return self.__url
