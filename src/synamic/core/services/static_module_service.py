"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


from synamic.core.contracts import BaseContentModuleContract
from synamic.core.functions.decorators import not_loaded


class StaticModuleService(BaseContentModuleContract):
    def __init__(self, config):
        self.__config = config
        self.__is_loaded = False
        self.__service_home_path = None

        self.__config.register_path(self.service_home_path)

    @property
    def service_home_path(self):
        if self.__service_home_path is None:
            self.__service_home_path = self.__config.path_tree.create_path(('static',))
        return self.__service_home_path

    @property
    def name(self):
        return 'static'

    @property
    def config(self):
        return self.__config

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        # print("From static load: %s" % str(self.service_home_path.relative_path_components))
        paths = self.__config.path_tree.list_file_paths(*self.service_home_path.path_components)
        for file_path in paths:
            # print("File path relative is: ", file_path.relative_path)
            assert file_path.is_file  # Remove in prod
            self.__config.add_static_content(file_path)
        self.__is_loaded = True