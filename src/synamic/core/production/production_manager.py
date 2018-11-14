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
from synamic.exceptions import SynamicError, SynamicErrors, SynamicDataError


class ProductionManager:
    def __init__(self, synamic):
        self.__synamic = synamic
        self.__is_loaded = False
        output_dir = self.__synamic.default_data.get_syd('dirs')['outputs.outputs']
        self.__output_cdir = self.__synamic.path_tree.create_dir_cpath(output_dir)

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__is_loaded = True

    def build(self):
        output_cdir = self.__output_cdir

    def upload(self):
        pass
