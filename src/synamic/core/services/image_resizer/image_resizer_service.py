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
from PIL import Image


class ImageResizerService:
    __algo_map = {
        'nearest': Image.NEAREST,
        'bicubic': Image.BICUBIC,
        'bilinear': Image.BILINEAR,
        'lanczos': Image.LANCZOS
    }

    def __init__(self, synamic):
        self.__synamic = synamic
        self.__image_path_map = {}
        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__is_loaded = True

    @classmethod
    def __get_algorithm_flag(cls, algorithm):
        algorithm = algorithm.lower()
        if algorithm not in cls.__algo_map:
            algorithm_flag = Image.BICUBIC
        else:
            algorithm_flag = cls.__algo_map[algorithm]
        return algorithm_flag

    @loaded
    def resize(self, file_path, width, height, algorithm=''):
        # decide algorithm
        algorithm_flag = self.__get_algorithm_flag(algorithm)
        path = file_path.absolute_path
        if path in self.__image_path_map:
            pass

        self.__synamic.path_tree.create_path()