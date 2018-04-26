"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

from synamic.core.standalones.functions.decorators import not_loaded, loaded
from synamic.core.services.sass.css import CSSContent


class SASSService:
    def __init__(self, synamic):
        self.__synamic = synamic
        self.__is_loaded = False
        self.__service_home_path = None

        self.__synamic.register_path(self.service_home_path)

    @property
    def service_home_path(self):
        if self.__service_home_path is None:
            self.__service_home_path = self.__synamic.path_tree.create_path(('scss',))
        return self.__service_home_path

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        paths = self.__synamic.path_tree.list_file_paths(*('sass', ))
        for file_path in paths:
            scss_basename = file_path.basename
            if file_path.extension.lower() in {'scss'}:
                if scss_basename.lower().startswith('_'):
                    # partial file, ignore it.
                    continue
                css_path = self.get_static_css_path(file_path)
                content_obj = CSSContent(self.__synamic, file_path, css_path)
                self.__synamic.add_auxiliary_content(content_obj)
            else:
                static_path = self.__synamic.path_tree.create_path(('static', *file_path.path_components[1:]), is_file=True)
                self.__synamic.add_static_content(static_path)

        self.__is_loaded = True

    def get_static_css_path(self, scss_file_path):
        scss_basename = scss_file_path.basename
        bcomps = scss_file_path.dirname_comps
        bname = scss_basename[:len(scss_basename) - len('.scss')] + '.css'
        return self.__synamic.path_tree.create_path(('static', *bcomps[1:], bname), is_file=True)

    def get_css_content(self, scss_path_comp_str):
        scss_path = self.__synamic.path_tree.create_path(scss_path_comp_str, is_file=True)
        css_path = self.get_static_css_path(scss_path)
        return CSSContent(self.__synamic, scss_path, css_path)
