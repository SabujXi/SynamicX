"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import os
import urllib.parse
from synamic.core.contracts.url import ContentUrlContract
from synamic.core.functions.normalizers import normalize_content_url_path, generalize_content_url_path, normalize_key, split_content_url_path_components
import re


class ContentUrl:
    def __init__(self, config, url_comps, is_dir=True):
        self.__config = config
        # self.__content = content_object
        if type(url_comps) is str:
            url_comps = url_comps.strip().strip(r'\/')
            self.__url_comps = [x for x in re.split(r'[\\/]+', url_comps) if x != '']
            if re.match(r'.*\.[a-z0-9]+$', url_comps, re.I):
                is_dir = False
        else:
            assert type(url_comps) in {list, tuple, set, frozenset}, "Url components can either be str, list or tuple"
            self.__url_comps = url_comps
        self.__url_comps = tuple([x for x in self.__url_comps if x != ''])
        # self.__url_name = url_name
        self.__is_dir = is_dir

        self.__url_str = None

    @property
    def absolute_url(self):
        raise NotImplemented

    @property
    def is_dir(self):
        return self.__is_dir

    @property
    def is_file(self):
        return not self.__is_dir

    @property
    def url_encoded_path(self):
        return urllib.parse.quote_plus(self.path, safe='/', encoding='utf-8')

    @property
    def path_components(self):
        return self.__url_comps

    @property
    def path(self):
        if self.__url_str is None:
            start = '/'
            end = '/' if self.__is_dir else ''
            self.__url_str = start + "/".join(self.__url_comps) + end
        return self.__url_str

    @property
    def real_path_components(self):
        if self.is_file:
            return self.__url_comps
        else:
            return (*self.__url_comps, "index.html")

    @property
    def real_path(self):
        end = '/' if self.is_dir else ''
        return "/" + "/".join(self.real_path_components) + end

    @property
    def norm_real_path(self):
        return self.real_path.lower()

    @property
    def norm_path_components(self):
        return tuple(c.lower() for c in self.__url_comps)

    @property
    def dir_components(self):
        if self.is_file:
            return self.__url_comps[:-1]
        else:
            return self.__url_comps

    @property
    def to_file_path(self):
        return self.__config.path_tree.create_path(
            (self.__config.site_settings.output_dir, *self.real_path_components),
            is_file=True
        )
