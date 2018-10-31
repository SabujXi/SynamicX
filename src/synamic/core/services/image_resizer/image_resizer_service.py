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
from synamic.core.services.image_resizer.resized_image_content import ResizedImageContent


class ImageResizerService:
    __algo_map = {
        'nearest': Image.NEAREST,
        'bicubic': Image.BICUBIC,
        'bilinear': Image.BILINEAR,
        'lanczos': Image.LANCZOS
    }

    def __init__(self, site):
        self.__site = site
        self.__image_paths = set()  # image content is key and p
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
        # algorithm_flag = self.__get_algorithm_flag(algorithm)
        # Algorithm is both unused here and in the img content class
        if type(file_path) is str:
            file_path = self.__site.path_tree.create_cpath(file_path, is_file=True)
        imgcnt = ResizedImageContent(self.__site, file_path, width, height)
        if imgcnt not in self.__image_paths:
            self.__image_paths.add(imgcnt)
            self.__site.add_auxiliary_content(imgcnt)
        return imgcnt
