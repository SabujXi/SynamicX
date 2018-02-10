"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


from synamic.core.functions.normalizers import normalize_key, normalize_keys
from synamic.core.functions.decorators import loaded, not_loaded
from synamic.core.contracts.module import BaseMetaModuleContract
from synamic.core.contracts.content import MetaContentContract
from synamic.core.new_parsers.document_parser import FieldParser


class ModelContent(MetaContentContract):
    def __init__(self, config, module_object, path_object, file_content: str):
        self.__config = config
        self.__module = module_object
        self.__path_object = path_object
        self.__file_content = file_content

        self.__root_field = FieldParser(file_content)

    @property
    def module_object(self):
        return self.__module

    @property
    def path_object(self):
        return self.__path_object

    @property
    def config(self):
        return self.__config

    @property
    def root_field(self):
        return self.__root_field


class ModelModule(BaseMetaModuleContract):
    def __init__(self, config):
        self.__config = config
        self.__is_loaded = False

    @not_loaded
    def load(self):
        file_paths = self.__config.path_tree.get_module_file_paths(self)
        model_file_paths = []
        for file_path in file_paths:
            if file_path.basename.endswith('.model.txt') and file_path.basename != len('.model.txt'):
                model_file_paths.append(file_path)

        model_txts = []

        for model_file_path in model_file_paths:
            with self.__config.path_tree.open(model_file_path.relative_path, 'r', encoding='utf-8') as f:
                model_txt = f.read()
                model_txts.append(model_txt)

        self.__is_loaded = True

    @property
    def is_loaded(self):
        return self.__is_loaded

    @property
    def name(self):
        return normalize_key('model')

    @property
    def config(self):
        return self.__config

    @property
    def dependencies(self):
        return set()
