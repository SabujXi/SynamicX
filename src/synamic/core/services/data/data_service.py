"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""
import json
from synamic.core.standalones.functions.decorators import not_loaded, loaded
from synamic.core.contracts import DataContract
from synamic.exceptions import SynamicError, SynamicErrors, SynamicDataError


class JsonData(DataContract):
    def __init__(self, data_name, json_map):
        self.__name = data_name
        self.__json_map = json_map

    def get_data_name(self):
        return self.__name

    @property
    def origin(self):
        return self.__json_map

    def get(self, key, default=None):
        return self.__json_map.get(key, default=default)

    def __getitem__(self, item):
        return self.get(item, default=None)

    def __getattr__(self, key):
        return self.get(key, default=None)

    def __str__(self):
        return str(self.__json_map)

    def __repr__(self):
        return repr(self.__json_map)


class SydData(DataContract):
    def __init__(self, name, syd):
        self.__name = name
        self.__syd = syd

    def get_data_name(self):
        return self.__name

    @property
    def origin(self):
        return self.__syd

    def get(self, key, default=None):
        return self.__syd.get(key, default=default)

    def __getitem__(self, item):
        return self.get(item, None)

    def __getattr__(self, key):
        return self.get(key, None)

    def __str__(self):
        return str(self.__syd)

    def __repr__(self):
        return repr(self.__syd)


class DataService:
    """
    Currently supports: 
    - syd (xxx.syd)
    - json (xxx.json)

    Supports have been removed for: (As I want to keep things clean and before syd like stuffs with lot of features including all those data type and conversions were not in synamic)
    - yaml (xxx.yaml, xxx.yml)
    - ini (xxx.ini)
    - toml (xxx.toml)
    """
    def __init__(self, site):
        self.__site = site
        self.__is_loaded = False

        data_dir = site.system_settings['dirs.metas.data']
        self.__data_cdir = site.path_tree.create_dir_cpath(data_dir)
        self.__available_extensions = ('.syd', '.json')

    @property
    def is_loaded(self):
        return self.__is_loaded

    @not_loaded
    def load(self):
        self.__is_loaded = True

    @loaded
    def make_data(self, data_name):
        syd_data_cfile = self.__data_cdir.join(f'{data_name}.syd', is_file=True)
        json_data_cfile = self.__data_cdir.join(f'{data_name}.json', is_file=True)
        res = None
        try:
            if syd_data_cfile.exists():
                syd = self.__site.object_manager.get_syd(syd_data_cfile)
                res = SydData(data_name, syd)
            elif json_data_cfile.exists():
                json_text = self.__site.object_manager.get_raw_text_data(json_data_cfile)
                json_obj = json.loads(json_text)
                res = JsonData(data_name, json_obj)
        except SynamicError as e:
            raise SynamicErrors(
                f'Data could not be made for data name {data_name}\n'
                f'One or both of the files tried: {syd_data_cfile.abs_path}, {json_data_cfile.abs_path}',
                e
            )

        if res is None:
            raise SynamicDataError(
                f'Data could not be made for data name {data_name}'
            )
        return res

    @loaded
    def get_data_names(self):
        names = []
        if self.__data_cdir.exists():
            data_file_cpaths = self.__data_cdir.list_files(checker=lambda cp: cp.basename.lower().endswith(self.__available_extensions))
            for file_cpath in data_file_cpaths:
                basename_wo_ext = file_cpath.basename_wo_ext
                names.append(basename_wo_ext)
        return names
