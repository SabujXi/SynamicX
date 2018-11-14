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
from .builtin_processors import _builtin_processor_classes
from synamic.exceptions import SynamicPreProcessorNotFound


class PreProcessorService:
    def __init__(self, site):
        self.__site = site

        self.__name_to_processor = {}

        self.__is_loaded = False

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        # load builtin processor
        path_tree = self.__site.get_service('path_tree')
        preprocess_cdir = path_tree.create_dir_cpath(self.__site.system_settings['dirs.contents.pre_process'])
        if preprocess_cdir.exists():
            cdirs = preprocess_cdir.list_dirs(depth=1)
            for cdir in cdirs:
                processor_name = cdir.basename
                if processor_name in _builtin_processor_classes:
                    self.add_processor(processor_name, cdir, _builtin_processor_classes[processor_name])
        # Add builtin pre-processor even if the dir does not exist for it
        for processor_name, processor_class in _builtin_processor_classes.items():
            if self.get_processor(processor_name, default=None, error_out=False) is None:
                cdir = preprocess_cdir.join(processor_name, is_file=False)
                self.add_processor(processor_name, cdir, processor_class)

        for processor in self.__name_to_processor.values():
            processor.load()
        self.__is_loaded = True

    def add_processor(self, processor_name, processor_cpath, processor_class):
        assert type(processor_class) is type
        assert processor_name not in self.__name_to_processor
        processor = processor_class(self.__site, processor_cpath)
        self.__name_to_processor[processor_name] = processor
        return processor

    def get_processor(self, processor_name, default=None, error_out=True):
        processor = self.__name_to_processor.get(processor_name, None)
        if processor is None and error_out is True:
            raise SynamicPreProcessorNotFound(f'Processor {processor_name} could not be found')
        elif processor is None:
            return default
        else:
            return processor

    @property
    def pre_processors(self):
        return tuple(self.__name_to_processor.values())

    def __getattr__(self, key):
        return self.get_processor(key, error_out=True)
