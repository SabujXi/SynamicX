import re

from synamic.core.contracts.url import UrlContract
import os


class Url(UrlContract):
    def __init__(self, config, content, url_str, url_name, is_dir=True):
        self.__config = config
        self.__content = content
        self.__url_str = url_str
        self.__url_name = url_name
        self.__is_dir = is_dir

        self.__url_str = self.__url_str.replace('\\', '/')

        if not self.__url_str.startswith('/'):
            self.__url_str = '/' + self.__url_str

    @property
    def full_url(self):
        raise NotImplemented

    @property
    def is_file(self):
        return not self.__is_dir

    @property
    def url_encoded_path(self):
        raise NotImplemented

    @property
    def path(self):
        return self.__url_str

    @property
    def name(self):
        return self.__url_name

    @property
    def content(self):
        return self.__content

    @property
    def real_path(self):
        if self.is_file:
            return self.path
        else:
            return self.path + "/index.html"

    @property
    def dir_components(self):
        if self.is_file:
            return self.path.strip('/').split('/')[:-1]
        else:
            return self.path.strip('/').split('/')

