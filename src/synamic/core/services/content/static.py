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
from synamic.core.synamic.router.url import _ContentUrl


class StaticContent(ContentContract):
    def __init__(self, site, path, file_content=None):
        assert file_content is None
        self.__url = None
        self.__site = site
        self.__path = path

    @property
    def path(self):
        return self.__path

    @property
    def path_object(self):
        return self.path

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
    def document_type(self):
        return ContentContract.__document_types.STATIC

    @property
    def url_object(self):
        if self.__url is None:
            self.__url = _ContentUrl(self.__site, self.__path)
        return self.__url

        # if file_path.meta_info:
        #     permalink = file_path.meta_info.get('permalink', None)
        #     if permalink:
        #         permalink = permalink.rstrip(r'\/')
        #         permalink_comps = [x for x in re.split(r'[\\/]+', permalink)]
        #     else:
        #         permalink_comps = file_path.path_comps
        #
        #     id = file_path.meta_info.get('id', None)
        #     cnt_url = _ContentUrl(self, permalink_comps, append_slash=False)
        # else:
        #     cnt_url = _ContentUrl(self, file_path.path_comps, append_slash=False)
        #     id = None
        #
        # if id is None:
        #     id = "/".join(file_path.path_comps)

