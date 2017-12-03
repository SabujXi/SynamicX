import os
import urllib.parse
from synamic.core.contracts.url import ContentUrlContract
from synamic.core.functions.normalizers import normalize_content_url_path, generalize_content_url_path, normalize_key, split_content_url_path_components


class ContentUrl(ContentUrlContract):
    def __init__(self, config, url_str, is_dir=True):
        self.__config = config
        # self.__content = content_object
        self.__url_str = url_str
        # self.__url_name = url_name
        self.__is_dir = is_dir

        self.__url_str = normalize_content_url_path(self.__url_str)
        # if self.__url_name:
        #     self.__url_name = normalize_key(self.__url_name)

        # validation
        # if it is not is_dir - that is is_file - it must not end with a '/'
        if not is_dir:
            assert not self.__url_str.endswith('/'), "A file url_object path cannot end with '/'"

    def append_component(self, component):
        # self.__is_dir = True
        if self.__is_dir:
            if self.__url_str.endswith('/'):
                self.__url_str += component + '/'
            else:
                self.__url_str += '/' + component + '/'
        else:  # file
            if self.__url_str.endswith('/'):
                self.__url_str = self.__url_str.rstrip('/')
            self.__url_str += '-' + component + '/'
            self.__is_dir = True

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
    def path(self):
        return self.__url_str

    @property
    def generalized_path(self):
        return generalize_content_url_path(self.path)

    @property
    def generalized_real_path(self):
        return generalize_content_url_path(self.real_path)

    # @property
    # def content(self):
    #     return self.__content

    @property
    def real_path(self):
        if self.is_file:
            return self.path
        else:
            return self.path + "/index.html"  # TO-DO: Make it dynamic later to take that value 'index.html' or whatever from settings and/or config

    @property
    def dir_components(self):
        comps = split_content_url_path_components(self.path)
        if self.is_file:
            return comps[:-1]
        else:
            return comps

    @property
    def to_file_path(self):
        return os.path.join(split_content_url_path_components(self.real_path))
