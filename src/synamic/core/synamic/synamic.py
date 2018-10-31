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
from synamic.core.synamic.sites.sites import Sites
from synamic.core.synamic.router import RouterService
from synamic.core.configs import DefaultConfigManager
from synamic.core.standalones.functions.decorators import loaded, not_loaded


class Synamic:
    def __init__(self, root_site_root):
        assert os.path.exists(root_site_root)
        assert os.path.isdir(root_site_root)
        self.__root_site_root = root_site_root

        # Default Config Manager
        self.__default_configs = DefaultConfigManager()

        self.__sites = Sites(self, self.__root_site_root)
        self.__router = RouterService(self)

        # env
        self.env = {
            'backend': 'file'
        }

        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @property
    def default_configs(self):
        return self.__default_configs

    @property
    # @loaded
    def sites(self):
        return self.__sites

    @property
    def root_path(self) -> str:
        return self.__root_site_root

    @not_loaded
    def load(self):
        self.__sites.load()  # TODO: sites should be loaded individually.
        self.__is_loaded = True

    @loaded
    @property
    def router(self):
        return self.__router


